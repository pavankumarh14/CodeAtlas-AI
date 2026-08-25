"use client";

import React, { useState, useEffect, useCallback } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  MarkerType
} from "reactflow";
import "reactflow/dist/style.css";
import { Search, Loader2, Info, Share2, HelpCircle } from "lucide-react";

// Custom node component for customized color styling
const CustomNode = ({ data }: any) => {
  const style = data.style || { background: "#fff", border: "#ccc", color: "#333" };
  return (
    <div 
      className="px-4 py-3 rounded-lg border-2 shadow-lg transition-all duration-300 text-left min-w-[150px]"
      style={{ 
        background: style.background, 
        borderColor: style.border, 
        color: style.color
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: style.border }} />
      <span className="text-[9px] font-mono uppercase tracking-widest font-semibold opacity-60 block">
        {data.type}
      </span>
      <span className="text-xs font-bold block mt-0.5 truncate">{data.label}</span>
      <Handle type="source" position={Position.Right} style={{ background: style.border }} />
    </div>
  );
};

const nodeTypes = {
  customNode: CustomNode,
};

export default function GraphExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightMode, setHighlightMode] = useState<"none" | "upstream" | "downstream">("none");

  // Fallback seed graph in case backend is not running
  const loadFallbackGraph = () => {
    const mockNodes: any[] = [
      { id: "Team:Commerce Team", type: "customNode", position: { x: 100, y: 150 }, data: { label: "Commerce Team", type: "Team", properties: { description: "Manages checkouts and payments" }, style: { background: "#FFF3CD", border: "#FFC107", color: "#856404" } } },
      { id: "Team:Notifications Team", type: "customNode", position: { x: 100, y: 350 }, data: { label: "Notifications Team", type: "Team", properties: { description: "Sends SMS and WhatsApp alerts" }, style: { background: "#FFF3CD", border: "#FFC107", color: "#856404" } } },
      { id: "Engineer:Sarah Smith", type: "customNode", position: { x: 100, y: 50 }, data: { label: "Sarah Smith", type: "Engineer", properties: { role: "Lead Engineer", email: "sarah@company.com" }, style: { background: "#D4EDDA", border: "#28A745", color: "#155724" } } },
      { id: "Service:Checkout Service", type: "customNode", position: { x: 400, y: 150 }, data: { label: "Checkout Service", type: "Service", properties: { purpose: "Handles customer checkout transactions", capability: "Commerce", risk_level: "High", failure_impact: "Revenue loss" }, style: { background: "#CCE5FF", border: "#007BFF", color: "#004085" } } },
      { id: "Service:Payment Service", type: "customNode", position: { x: 400, y: 300 }, data: { label: "Payment Service", type: "Service", properties: { purpose: "Triggers Stripe charges", capability: "Commerce", risk_level: "High" }, style: { background: "#CCE5FF", border: "#007BFF", color: "#004085" } } },
      { id: "Service:Notifications Service", type: "customNode", position: { x: 400, y: 450 }, data: { label: "Notifications Service", type: "Service", properties: { purpose: "Triggers dispatch alerts", capability: "Notifications" }, style: { background: "#CCE5FF", border: "#007BFF", color: "#004085" } } },
      { id: "Repository:checkout-api", type: "customNode", position: { x: 700, y: 100 }, data: { label: "checkout-api", type: "Repository", properties: { language: "TypeScript", url: "git@github.com:org/checkout-api.git" }, style: { background: "#E8D9F2", border: "#9C27B0", color: "#4A0072" } } },
      { id: "Repository:payment-gateway", type: "customNode", position: { x: 700, y: 250 }, data: { label: "payment-gateway", type: "Repository", properties: { language: "Python" }, style: { background: "#E8D9F2", border: "#9C27B0", color: "#4A0072" } } },
      { id: "API:POST /api/v1/checkout", type: "customNode", position: { x: 700, y: 400 }, data: { label: "POST /api/v1/checkout", type: "API", properties: { method: "POST", path: "/api/v1/checkout" }, style: { background: "#D1ECF1", border: "#17A2B8", color: "#0C5460" } } },
      { id: "Incident:INC-212", type: "customNode", position: { x: 400, y: -20 }, data: { label: "INC-212: Stripe Outage", type: "Incident", properties: { severity: "Critical", status: "Active", root_cause: "Stripe API timeouts" }, style: { background: "#FCE8E6", border: "#EA4335", color: "#C5221F" } } }
    ];

    const mockEdges: any[] = [
      { id: "edge-1", source: "Team:Commerce Team", target: "Service:Checkout Service", label: "OWNS", animated: false },
      { id: "edge-2", source: "Team:Commerce Team", target: "Service:Payment Service", label: "OWNS", animated: false },
      { id: "edge-3", source: "Team:Notifications Team", target: "Service:Notifications Service", label: "OWNS", animated: false },
      { id: "edge-4", source: "Engineer:Sarah Smith", target: "Team:Commerce Team", label: "MEMBER_OF", animated: false },
      { id: "edge-5", source: "Service:Checkout Service", target: "Service:Payment Service", label: "DEPENDS_ON", animated: true },
      { id: "edge-6", source: "Service:Checkout Service", target: "Service:Notifications Service", label: "DEPENDS_ON", animated: true },
      { id: "edge-7", source: "Repository:checkout-api", target: "Service:Checkout Service", label: "IMPLEMENTS", animated: false },
      { id: "edge-8", source: "Repository:payment-gateway", target: "Service:Payment Service", label: "IMPLEMENTS", animated: false },
      { id: "edge-9", source: "API:POST /api/v1/checkout", target: "Service:Checkout Service", label: "EXPOSES", animated: false },
      { id: "edge-10", source: "Incident:INC-212", target: "Service:Payment Service", label: "TRIGGERED_BY", animated: false }
    ];

    setNodes(mockNodes);
    setEdges(mockEdges);
  };

  useEffect(() => {
    async function fetchGraph() {
      setLoading(true);
      try {
        const res = await fetch("http://localhost:8000/api/v1/graph/data");
        if (res.ok) {
          const data = await res.json();
          if (data.nodes && data.nodes.length > 0) {
            setNodes(data.nodes);
            setEdges(data.edges);
          } else {
            loadFallbackGraph();
          }
        } else {
          loadFallbackGraph();
        }
      } catch (err) {
        console.warn("Backend not running, loading fallback interactive graph.", err);
        loadFallbackGraph();
      } finally {
        setLoading(false);
      }
    }
    fetchGraph();
  }, [setNodes, setEdges]);

  // Click handler on React Flow nodes
  const onNodeClick = useCallback((event: any, node: any) => {
    setSelectedNode(node.data);
    setHighlightMode("none");
  }, []);

  // Search logic to highlight matching nodes
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      // Clear styles override
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          style: {}
        }))
      );
      return;
    }

    setNodes((nds) =>
      nds.map((node) => {
        const isMatch = node.data.label.toLowerCase().includes(searchQuery.toLowerCase()) || 
                        node.data.type.toLowerCase().includes(searchQuery.toLowerCase());
        return {
          ...node,
          style: isMatch 
            ? { boxShadow: "0 0 20px 5px rgba(99, 102, 241, 0.8)", border: "2px solid #6366f1" } 
            : { opacity: 0.3 }
        };
      })
    );
  };

  // Upstream / Downstream path traversal highlighter
  const highlightPath = (direction: "upstream" | "downstream") => {
    if (!selectedNode) return;
    
    // Simple BFS traversal on edges to find connected paths
    const startId = nodes.find(n => n.data.label === selectedNode.label)?.id;
    if (!startId) return;

    const visitedNodes = new Set<string>([startId]);
    const highlightedEdges = new Set<string>();

    let queue = [startId];
    while (queue.length > 0) {
      const curr = queue.shift()!;
      edges.forEach((edge) => {
        if (direction === "upstream") {
          // If we rely on it, edge goes: Checkout -> DEPENDS_ON -> Payment. Start node depends on Target node.
          if (edge.source === curr) {
            if (!visitedNodes.has(edge.target)) {
              visitedNodes.add(edge.target);
              highlightedEdges.add(edge.id);
              queue.push(edge.target);
            }
          }
        } else {
          // Downstream blast radius: who depends on us.
          // Checkout Service is downstream from Payment Service (Payment <- Checkout)
          if (edge.target === curr) {
            if (!visitedNodes.has(edge.source)) {
              visitedNodes.add(edge.source);
              highlightedEdges.add(edge.id);
              queue.push(edge.source);
            }
          }
        }
      });
    }

    // Apply styles to highlight path
    setNodes((nds) =>
      nds.map((node) => {
        const isVisited = visitedNodes.has(node.id);
        return {
          ...node,
          style: isVisited 
            ? { border: "3px solid #f43f5e", boxShadow: "0 0 15px rgba(244, 63, 94, 0.6)" } 
            : { opacity: 0.2 }
        };
      })
    );

    setEdges((eds) =>
      eds.map((edge) => {
        const isHighlighted = highlightedEdges.has(edge.id);
        return {
          ...edge,
          animated: isHighlighted,
          style: isHighlighted 
            ? { stroke: "#f43f5e", strokeWidth: 4 } 
            : { stroke: "#334155", opacity: 0.2 }
        };
      })
    );

    setHighlightMode(direction);
  };

  const resetHighlight = () => {
    setNodes((nds) => nds.map((n) => ({ ...n, style: {} })));
    setEdges((eds) => eds.map((e) => ({ 
      ...e, 
      animated: e.label === "DEPENDS_ON" || e.label === "USES", 
      style: { stroke: "#999999", strokeWidth: 2 } 
    })));
    setHighlightMode("none");
  };

  return (
    <div className="h-[calc(100vh-140px)] flex gap-8 animate-fadeIn overflow-hidden">
      
      {/* React Flow Canvas */}
      <div className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/80 z-10 gap-3">
            <Loader2 className="h-6 w-6 text-indigo-500 animate-spin" />
            <span className="text-slate-400 text-sm font-medium">Drawing Ontology Graph...</span>
          </div>
        ) : null}

        {/* Toolbar Overlay */}
        <div className="absolute top-4 left-4 z-10 bg-slate-900 border border-slate-800 p-2.5 rounded-xl flex gap-3 shadow-xl">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              placeholder="Search graph..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="px-3 py-1.5 bg-slate-950 border border-slate-850 focus:border-indigo-500 rounded-lg text-xs text-slate-200 outline-none w-48"
            />
            <button type="submit" className="p-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white transition cursor-pointer">
              <Search className="h-3.5 w-3.5" />
            </button>
          </form>
          
          {highlightMode !== "none" && (
            <button 
              onClick={resetHighlight} 
              className="px-3 py-1 bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/30 text-rose-400 text-xs font-semibold rounded-lg transition cursor-pointer"
            >
              Reset Path
            </button>
          )}
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={1.5}
        >
          <Background color="#334155" gap={24} size={1} />
          <Controls className="bg-slate-900 border border-slate-800 rounded-lg text-slate-200 fill-slate-200" />
          <MiniMap 
            nodeColor={(node: any) => node.data.style?.border || "#ccc"}
            maskColor="rgba(15, 23, 42, 0.6)"
            className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden hidden md:block" 
          />
        </ReactFlow>
      </div>

      {/* Selected Node Details Drawer */}
      <div className="w-80 shrink-0 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between overflow-y-auto">
        {selectedNode ? (
          <div className="space-y-6">
            {/* Node Metadata header */}
            <div className="border-b border-slate-800 pb-4">
              <span className="text-[10px] font-mono font-bold uppercase tracking-widest px-2.5 py-1 rounded bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
                {selectedNode.type}
              </span>
              <h3 className="text-lg font-bold text-white mt-3 truncate">{selectedNode.label}</h3>
            </div>

            {/* Properties List */}
            <div className="space-y-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Properties</h4>
              <div className="space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-850">
                {Object.entries(selectedNode.properties || {}).map(([key, value]: any) => (
                  <div key={key} className="text-xs">
                    <span className="font-semibold text-slate-500 capitalize">{key.replace("_", " ")}:</span>
                    <p className="text-slate-300 mt-0.5 whitespace-pre-line leading-relaxed">{String(value)}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Graph Query helpers */}
            {selectedNode.type === "Service" && (
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                  <Share2 className="h-3.5 w-3.5" />
                  Path Traversals
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  <button 
                    onClick={() => highlightPath("upstream")}
                    className="py-2 bg-slate-800 hover:bg-slate-750 text-slate-200 hover:text-white rounded-lg text-xs font-semibold transition border border-slate-700 cursor-pointer"
                  >
                    Dependencies
                  </button>
                  <button 
                    onClick={() => highlightPath("downstream")}
                    className="py-2 bg-rose-950/40 hover:bg-rose-950/60 border border-rose-900/40 text-rose-300 rounded-lg text-xs font-semibold transition cursor-pointer"
                  >
                    Blast Radius
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center h-full text-slate-500 gap-3">
            <HelpCircle className="h-8 w-8 text-slate-700 animate-pulse" />
            <div>
              <h4 className="text-sm font-semibold text-slate-400">No Node Selected</h4>
              <p className="text-xs text-slate-600 mt-1 max-w-[200px]">
                Click any node in the knowledge graph to view its metadata properties and dependency connections.
              </p>
            </div>
          </div>
        )}

        {/* Legend */}
        {selectedNode && (
          <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl mt-6 flex gap-2">
            <Info className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
            <p className="text-[10px] text-slate-500 leading-normal">
              Nodes are pre-aligned by ontology category: Left (Teams/People) → Middle (Services/Incidents) → Right (Repos/APIs/Docs).
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
