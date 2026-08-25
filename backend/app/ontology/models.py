from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BusinessCapability(BaseModel):
    name: str
    description: str
    risk_level: str = "Medium"  # Low, Medium, High

class Service(BaseModel):
    name: str
    purpose: str
    capability: str
    failure_impact: str
    risk_level: str = "Medium"
    knowledge_sources: List[str] = Field(default_factory=list)

class Repository(BaseModel):
    name: str
    url: str
    language: str

class API(BaseModel):
    path: str
    method: str
    description: str
    service_name: str

class Engineer(BaseModel):
    name: str
    email: str
    role: str
    github: str

class Team(BaseModel):
    name: str
    description: str

class Requirement(BaseModel):
    req_id: str
    title: str
    description: str
    priority: str = "Medium"  # Low, Medium, High
    status: str = "Proposed"  # Proposed, In Progress, Implemented

class Incident(BaseModel):
    inc_id: str
    title: str
    severity: str  # Low, Medium, High, Critical
    status: str  # Active, Resolved
    root_cause: Optional[str] = None
    resolution: Optional[str] = None

class Document(BaseModel):
    title: str
    type: str  # Confluence, Slack, Architecture, README
    content: str
    url: Optional[str] = None

class Runbook(BaseModel):
    title: str
    content: str
    service_name: str

class Technology(BaseModel):
    name: str
    category: str  # Language, Database, Library, Cloud

class Database(BaseModel):
    name: str
    db_type: str  # Relational, Document, Graph, Cache

class Feature(BaseModel):
    name: str
    description: str
    status: str  # Planned, Active, Deprecated
