from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import uuid
import datetime
import os
import zipfile
import io
import re
import requests

from .config import settings
from .graph import get_graph_driver
from .vectorstore import get_vector_store
from .agents import AgentOrchestrator
from .data import seed_all_data
from .repository_ingestion import inspect_public_repository, MANIFEST_NAMES, DOC_SUFFIXES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="The Living Engineering Ontology and Knowledge Graph Platform API"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory query activity log
activity_log: List[Dict[str, Any]] = []

# Instantiate Orchestrator
orchestrator = AgentOrchestrator()

class AnalyzeRequest(BaseModel):
    query: str

class RepositoryImportRequest(BaseModel):
    repository_url: str

@app.on_event("startup")
def startup_event():
    # Attempt to establish connections and auto-seed if graph database is empty
    try:
        driver = get_graph_driver()
        nodes = driver.get_nodes()
        if not nodes:
            logger.info("Graph database is empty. Auto-seeding initial data...")
            seed_all_data()
    except Exception as e:
        logger.error(f"Startup database connection or seed failed: {e}")

@app.post("/api/v1/seed", tags=["Data"])
def trigger_seed():
    try:
        seed_all_data()
        return {"status": "success", "message": "Database seeded successfully."}
    except Exception as e:
        logger.error(f"Manual seed trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats", tags=["Dashboard"])
def get_dashboard_stats():
    try:
        driver = get_graph_driver()
        services = len(driver.get_nodes("Service"))
        repos = len(driver.get_nodes("Repository"))
        teams = len(driver.get_nodes("Team"))
        engineers = len(driver.get_nodes("Engineer"))
        requirements = len(driver.get_nodes("Requirement"))
        
        all_incidents = driver.get_nodes("Incident")
        active_incidents = sum(1 for inc in all_incidents if inc["properties"].get("status") == "Active")
        
        # Calculate system health score
        # Base health is 100%, deduct points for active incidents and missing compliance
        health_score = max(30, 100 - (active_incidents * 15))
        
        return {
            "services": services,
            "repositories": repos,
            "teams": teams,
            "engineers": engineers,
            "requirements": requirements,
            "active_incidents": active_incidents,
            "system_health_score": health_score
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        return {
            "services": 0, "repositories": 0, "teams": 0, "engineers": 0,
            "requirements": 0, "active_incidents": 0, "system_health_score": 100
        }

@app.get("/api/v1/incidents", tags=["Dashboard"])
def list_incidents():
    try:
        driver = get_graph_driver()
        incidents = driver.get_nodes("Incident")
        return [inc["properties"] for inc in incidents]
    except Exception as e:
        logger.error(f"Failed to list incidents: {e}")
        return []

@app.get("/api/v1/requirements", tags=["Dashboard"])
def list_requirements():
    try:
        driver = get_graph_driver()
        reqs = driver.get_nodes("Requirement")
        return [r["properties"] for r in reqs]
    except Exception as e:
        logger.error(f"Failed to list requirements: {e}")
        return []

@app.post("/api/v1/analyze", tags=["Agents"])
def analyze_query(request: AnalyzeRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    start_time = datetime.datetime.now()
    try:
        result = orchestrator.execute(request.query)
        end_time = datetime.datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": start_time.isoformat(),
            "query": request.query,
            "flow_type": result.get("flow_type"),
            "target_agent": result.get("target_agent"),
            "duration_ms": duration_ms,
            "status": "Success"
        }
        activity_log.insert(0, log_entry)
        
        return result
    except Exception as e:
        logger.error(f"Error in orchestrator execution: {e}", exc_info=True)
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": start_time.isoformat(),
            "query": request.query,
            "flow_type": "unknown",
            "target_agent": "Orchestrator",
            "duration_ms": 0,
            "status": f"Error: {str(e)}"
        }
        activity_log.insert(0, log_entry)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/repositories/import", tags=["Repository Intake"])
def import_public_repository(request: RepositoryImportRequest):
    """Inspect public GitHub metadata and add the discoverable evidence to the graph."""
    try:
        profile = inspect_public_repository(request.repository_url)
        graph = get_graph_driver()
        graph.add_node("Repository", {
            "name": profile["repository"],
            "url": profile["url"],
            "description": profile["description"],
            "default_branch": profile["default_branch"],
            "languages": ", ".join(profile["languages"]),
            "source": "Public GitHub import",
        })
        for path in profile["documents"]:
            title = f"{profile['repository']} · {path}"
            graph.add_node("Document", {"title": title, "path": path, "repository": profile["repository"], "source": "Public GitHub import"})
            graph.add_relationship("Repository", profile["repository"], "Document", title, "CONTAINS")

        activity_log.insert(0, {
            "id": str(uuid.uuid4()), "timestamp": datetime.datetime.now().isoformat(),
            "query": f"Imported public repository {profile['repository']}", "flow_type": "repository_intake",
            "target_agent": "Repository Intake", "duration_ms": 0, "status": "Success"
        })
        return {**profile, "graph_nodes_added": 1 + len(profile["documents"])}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException:
        logger.exception("Public repository lookup failed")
        raise HTTPException(status_code=502, detail="Could not reach GitHub. Please try again.")

@app.post("/api/v1/repositories/upload", tags=["Repository Intake"])
async def upload_repository_zip(request: Request, filename: str):
    """Stage and inspect a local repository uploaded as a ZIP archive, adding it to the graph."""
    try:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
            
        repo_name = filename
        if repo_name.lower().endswith(".zip"):
            repo_name = repo_name[:-4]
            
        # Read zip in-memory
        try:
            with zipfile.ZipFile(io.BytesIO(body)) as z:
                paths = [info.filename for info in z.infolist() if not info.is_dir()][:1000]
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file structure.")
            
        # Classify files
        manifests = [path for path in paths if path.rsplit("/", 1)[-1].lower() in MANIFEST_NAMES][:12]
        documents = [path for path in paths if path.lower().endswith(DOC_SUFFIXES)][:12]
        api_candidates = [path for path in paths if re.search(r"(^|/)(api|routes?|controllers?)(/|$)|/(route|controller)\.", path, re.IGNORECASE)][:12]
        
        # Detect languages based on file extensions
        lang_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".jsx": "JavaScript",
            ".go": "Go",
            ".java": "Java",
            ".rb": "Ruby",
            ".rs": "Rust",
            ".cs": "C#",
            ".cpp": "C++",
            ".c": "C",
        }
        detected_langs = set()
        for path in paths:
            ext = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
            if ext in lang_map:
                detected_langs.add(lang_map[ext])
                
        languages = list(detected_langs)[:8]
        
        profile = {
            "repository": repo_name,
            "url": f"local://{filename}",
            "description": f"Local repository staged via ZIP upload of {filename}.",
            "default_branch": "main",
            "languages": languages,
            "files_scanned": len(paths),
            "tree_truncated": len(paths) >= 1000,
            "manifests": manifests,
            "documents": documents,
            "api_candidates": api_candidates,
            "graph_nodes_added": 1 + len(documents),
        }
        
        # Add to graph
        graph = get_graph_driver()
        graph.add_node("Repository", {
            "name": profile["repository"],
            "url": profile["url"],
            "description": profile["description"],
            "default_branch": profile["default_branch"],
            "languages": ", ".join(profile["languages"]),
            "source": "Local ZIP upload",
        })
        for path in profile["documents"]:
            title = f"{profile['repository']} · {path}"
            graph.add_node("Document", {"title": title, "path": path, "repository": profile["repository"], "source": "Local ZIP upload"})
            graph.add_relationship("Repository", profile["repository"], "Document", title, "CONTAINS")
            
        # Add to activity log
        activity_log.insert(0, {
            "id": str(uuid.uuid4()), "timestamp": datetime.datetime.now().isoformat(),
            "query": f"Uploaded local repository {profile['repository']}", "flow_type": "repository_intake",
            "target_agent": "Repository Intake", "duration_ms": 0, "status": "Success"
        })
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ZIP upload failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agent-activity-log", tags=["Agents"])
def get_activity_log():
    return activity_log

@app.get("/api/v1/knowledge-gaps", tags=["Agents"])
def scan_knowledge_gaps():
    try:
        agent = orchestrator.agents["knowledge_gap"]
        res = agent.run("Scan for knowledge gaps")
        return res["result"]
    except Exception as e:
        logger.error(f"Failed to scan knowledge gaps: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/experts", tags=["Agents"])
def search_experts(service: str):
    try:
        agent = orchestrator.agents["expert_discovery"]
        res = agent.run(f"Who owns {service}")
        return res["result"]
    except Exception as e:
        logger.error(f"Failed to search experts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/graph/data", tags=["Graph"])
def get_graph_data():
    """Retrieve nodes and edges formatted for React Flow rendering."""
    try:
        driver = get_graph_driver()
        raw_nodes = driver.get_nodes()
        raw_rels = driver.get_relationships()
        
        formatted_nodes = []
        formatted_edges = []
        
        # Color mapping for UI ontology nodes
        # React Flow custom node styles
        color_map = {
            "Team": {"background": "#FFF3CD", "border": "#FFC107", "color": "#856404"},       # Yellow
            "Engineer": {"background": "#D4EDDA", "border": "#28A745", "color": "#155724"},   # Green
            "Service": {"background": "#CCE5FF", "border": "#007BFF", "color": "#004085"},    # Blue
            "Repository": {"background": "#E8D9F2", "border": "#9C27B0", "color": "#4A0072"}, # Purple
            "API": {"background": "#D1ECF1", "border": "#17A2B8", "color": "#0C5460"},        # Teal
            "Requirement": {"background": "#F8D7DA", "border": "#DC3545", "color": "#721C24"},# Red/Pink
            "Incident": {"background": "#FCE8E6", "border": "#EA4335", "color": "#C5221F"},   # Orange/Red
            "Document": {"background": "#E2E3E5", "border": "#6C757D", "color": "#383D41"},   # Grey
            "Runbook": {"background": "#E2F0D9", "border": "#70AD47", "color": "#385623"}     # Light Green
        }
        
        # Grid layout helper coordinates to prevent overlapping
        category_x = {
            "Team": 100,
            "Engineer": 100,
            "Service": 400,
            "Repository": 700,
            "API": 700,
            "Requirement": 400,
            "Incident": 400,
            "Document": 950,
            "Runbook": 950
        }
        
        y_counters = {k: 50 for k in category_x.keys()}
        
        for node in raw_nodes:
            lbl = node["labels"][0]
            properties = node["properties"]
            
            # Primary naming extraction
            name = properties.get("name") or properties.get("title") or properties.get("req_id") or properties.get("inc_id") or "Unnamed Node"
            
            # Position allocation
            x = category_x.get(lbl, 500)
            if lbl == "Engineer":
                x = 100
                y = y_counters["Team"] + 50
                y_counters["Team"] = y  # Stagger them
            else:
                y = y_counters.get(lbl, 100)
                y_counters[lbl] = y + 120
            
            style = color_map.get(lbl, {"background": "#FFFFFF", "border": "#CCCCCC", "color": "#333333"})
            
            formatted_nodes.append({
                "id": node["id"],
                "type": "customNode",  # React Flow custom node
                "position": {"x": x, "y": y},
                "data": {
                    "label": name,
                    "type": lbl,
                    "properties": properties,
                    "style": style
                }
            })
            
        for rel in raw_rels:
            formatted_edges.append({
                "id": f"edge-{rel['id']}",
                "source": rel["start_node"]["id"],
                "target": rel["end_node"]["id"],
                "label": rel["type"],
                "animated": rel["type"] in ("DEPENDS_ON", "USES"),
                "style": {"stroke": "#999999", "strokeWidth": 2}
            })
            
        return {
            "nodes": formatted_nodes,
            "edges": formatted_edges
        }
    except Exception as e:
        logger.error(f"Failed to fetch graph data: {e}", exc_info=True)
        return {"nodes": [], "edges": []}

# In the Render image, the Next.js static export is copied here during the Docker build.
# Mount this last so all API and documentation routes remain owned by FastAPI.
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
