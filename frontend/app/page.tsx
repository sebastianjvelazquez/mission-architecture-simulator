"use client";

import React, { useCallback, useRef, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  ReactFlowInstance,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
  Node,
  Handle,
  Position,
  Edge,
  addEdge,
  Connection,
  MarkerType,
  ConnectionMode,
} from "reactflow";
import "reactflow/dist/style.css";
import Navbar from "@/components/NavbarEditor";
import { nodeServerAppPaths } from "next/dist/build/webpack/plugins/pages-manifest-plugin";
import { on } from "events";

// ALL CUSTOM NODES
function SensorNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        borderRadius: "100px",
        background: "rgba(0, 0, 0, 0.5)",
        border: "2px solid white",
      }}
    >
      {/* Top Handle */}
      <Handle type="target" position={Position.Top} id="top" />
      
      {/* Right Handle */}
      <Handle type="source" position={Position.Right} id="right" />
      
      {/* Bottom Handle */}
      <Handle type="source" position={Position.Bottom} id="bottom" />
      
      {/* Left Handle */}
      <Handle type="target" position={Position.Left} id="left" />
      
      <div style={{ color: "white" }}>{data.label}</div>
    </div>
  );
}

function ComputeNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        borderRadius: "100px",
        background: "rgba(0, 0, 0, 0.5)",
        border: "2px solid white",
      }}
    >
      {/* Top Handle */}
      <Handle type="target" position={Position.Top} id="top" />
      
      {/* Right Handle */}
      <Handle type="source" position={Position.Right} id="right" />
      
      {/* Bottom Handle */}
      <Handle type="source" position={Position.Bottom} id="bottom" />
      
      {/* Left Handle */}
      <Handle type="target" position={Position.Left} id="left" />
      
      <div style={{ color: "white" }}>{data.label}</div>
    </div>
  );
}

function CommsLinkNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        borderRadius: "100px",
        background: "rgba(0, 0, 0, 0.5)",
        border: "2px solid white",
      }}
    >
      {/* Top Handle */}
      <Handle type="target" position={Position.Top} id="top" />
      
      {/* Right Handle */}
      <Handle type="source" position={Position.Right} id="right" />
      
      {/* Bottom Handle */}
      <Handle type="source" position={Position.Bottom} id="bottom" />
      
      {/* Left Handle */}
      <Handle type="target" position={Position.Left} id="left" />
      
      <div style={{ color: "white" }}>{data.label}</div>
    </div>
  );
}

function ControlNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        borderRadius: "100px",
        background: "rgba(0, 0, 0, 0.5)",
        border: "2px solid white",
      }}
    >
      {/* Top Handle */}
      <Handle type="target" position={Position.Top} id="top" />
      
      {/* Right Handle */}
      <Handle type="source" position={Position.Right} id="right" />
      
      {/* Bottom Handle */}
      <Handle type="source" position={Position.Bottom} id="bottom" />
      
      {/* Left Handle */}
      <Handle type="target" position={Position.Left} id="left" />
      
      <div style={{ color: "white" }}>{data.label}</div>
    </div>
  );
}

function StorageNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        borderRadius: "100px",
        background: "rgba(0, 0, 0, 0.5)",
        border: "2px solid white",
      }}
    >
      {/* Top Handle */}
      <Handle type="target" position={Position.Top} id="top"/>
      
      {/* Right Handle */}
      <Handle type="source" position={Position.Right} id="right" />
      
      {/* Bottom Handle */}
      <Handle type="source" position={Position.Bottom} id="bottom" />
      
      {/* Left Handle */}
      <Handle type="target" position={Position.Left} id="left" />
      
      <div style={{ color: "white" }}>{data.label}</div>
    </div>
  );
}

function ExternalNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        borderRadius: "100px",
        background: "rgba(0, 0, 0, 0.5)",
        border: "2px solid white",
      }}
    >
      {/* Top Handle */}
      <Handle type="target" position={Position.Top} id="top" />
      
      {/* Right Handle */}
      <Handle type="source" position={Position.Right} id="right" />
      
      {/* Bottom Handle */}
      <Handle type="source" position={Position.Bottom} id="bottom" />
      
      {/* Left Handle */}
      <Handle type="target" position={Position.Left} id="left" />
      
      <div style={{ color: "white" }}>{data.label}</div>
    </div>
  );
}
{/* END OF CUSTOM NODES */}

// DEFINE NODE TYPES
const nodeTypes = {
  Sensor: SensorNode,
  Compute: ComputeNode,
  CommsLink: CommsLinkNode,
  Control: ControlNode,
  Storage: StorageNode,
  External: ExternalNode,
};

// NODE EDIT MODAL COMPONENT
interface NodeModalProps {
  isOpen: boolean;
  nodeType: string;
  currentName: string;
  currentCriticality: number;
  onClose: () => void;
  onSave: (name: string, criticality: number) => void;
}

// NODE EDIT MODAL FUNCTION
function NodeEditModal({ isOpen, nodeType, currentName, currentCriticality, onClose, onSave }: NodeModalProps) {
  const [name, setName] = useState(currentName);
  const [criticality, setCriticality] = useState(currentCriticality);

  // UPDATE NAME AND CRITICALITY STATE WHEN MODAL OPENS WITH NEW NODE DATA
  React.useEffect(() => {
    if (isOpen) {
      setName(currentName);
      setCriticality(currentCriticality);
    }
  }, [isOpen, currentName, currentCriticality]);

  const handleSave = () => {
    onSave(name || currentName, criticality);
    onClose();
  };

  if (!isOpen) return null;

  return (
    // MODAL STYLING AND POSITIONING
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: "#1A1A1A",
        padding: "20px",
        borderRadius: "8px",
        color: "white",
        minWidth: "300px",
      }}>
        <h3 style={{ marginTop: 0 }}>Node Properties</h3>
        <br></br>
        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>Type:</span>
          <input
            type="text"
            value={nodeType ?? ""}
            disabled
            style={{
              width: "100%",
              padding: "8px",
              marginTop: "5px",
              backgroundColor: "#2A2A2A",
              color: "#888",
              border: "1px solid #444",
              borderRadius: "4px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>Name:</span>
          <input
            type="text"
            value={name ?? ""}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter node name"
            style={{
              width: "100%",
              padding: "8px",
              marginTop: "5px",
              backgroundColor: "#2A2A2A",
              color: "white",
              border: "1px solid #444",
              borderRadius: "4px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>Criticality:</span>
          <select
            value={criticality ?? 1}
            onChange={(e) => setCriticality(Number(e.target.value))}
            style={{
              width: "100%",
              padding: "8px",
              marginTop: "5px",
              backgroundColor: "#2A2A2A",
              color: "white",
              border: "1px solid #444",
              borderRadius: "4px",
              boxSizing: "border-box",
            }}
          >
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="8">8</option>
            <option value="9">9</option>
            <option value="10">10</option>
          </select>
        </label>

        <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
          <button
            onClick={onClose}
            style={{
              padding: "8px 16px",
              backgroundColor: "#444",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            style={{
              padding: "8px 16px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

// EDGE EDIT MODAL COMPONENT
interface EdgeModalProps {
  isOpen: boolean;
  currentLabel: string;
  onClose: () => void;
  onSave: (label: string) => void;
}


// CONNECTION/EDGE EDIT MODAL FUNCTION
function EdgeEditModal({ isOpen, currentLabel, onClose, onSave }: EdgeModalProps) {
  const [label, setLabel] = useState(currentLabel);

  // UPDATE LABEL STATE WHEN MODAL OPENS WITH NEW EDGE DATA
  React.useEffect(() => {
    if (isOpen) {
      setLabel(currentLabel);
    }
  }, [isOpen, currentLabel]);

  const handleSave = () => {
    onSave(label);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: "#1A1A1A",
        padding: "20px",
        borderRadius: "8px",
        color: "white",
        minWidth: "300px",
      }}>
        <h3 style={{ marginTop: 0 }}>Edge Properties</h3>
        <br></br>
        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>Label:</span>
          <input
            type="text"
            value={label ?? ""}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Enter edge label"
            style={{
              width: "100%",
              padding: "8px",
              marginTop: "5px",
              backgroundColor: "#2A2A2A",
              color: "white",
              border: "1px solid #444",
              borderRadius: "4px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
          <button
            onClick={onClose}
            style={{
              padding: "8px 16px",
              backgroundColor: "#444",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            style={{
              padding: "8px 16px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [nodes, setNodes] = useState<Node<{ label: string }>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [isEdgeModalOpen, setIsEdgeModalOpen] = useState(false);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);

  const onNodesChange = (changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  };

  const onEdgesChange = (changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
  };

  // CONNECTIONS BETWEEN NODES (ARROWS)
  const onConnect = useCallback(
    (connection: Connection) => {
      const sourceNode = nodes.find((n) => n.id === connection.source);
      const targetNode = nodes.find((n) => n.id === connection.target);

      setEdges((eds) => addEdge({
        ...connection,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: "#fff",
        },
        style: {
          stroke: "#fff",
          strokeWidth: 3,
        },
        label: "",
        labelStyle: { fill: "#fff", fontWeight: 500 },
        labelBgStyle: { fill: "#141414"},
        data: {
          sourceNodeType: sourceNode?.type,
          targetNodeType: targetNode?.type,
        }
      }, eds));
    },
    [nodes]
  );

  // ON DOUBLE CLICK EDGE - OPEN MODAL
  const onEdgeDoubleClick = useCallback((_: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge);
    setIsEdgeModalOpen(true);
  }, []);

  // HANDLE EDGE SAVE FROM MODAL
  const handleEdgeSave = useCallback((label: string) => {
    setEdges((eds) =>
      eds.map((e) =>
        e.id === selectedEdge?.id ? { ...e, label } : e
      )
    );
    setIsEdgeModalOpen(false);
    setSelectedEdge(null);
  }, [selectedEdge]);

  // ON DOUBLE CLICK NODE - OPEN MODAL
  const onNodeDoubleClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setIsModalOpen(true);
  }, []);

  // HANDLE NODE SAVE FROM MODAL
  const handleNodeSave = useCallback((name: string, criticality: number) => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === selectedNode?.id
          ? {
              ...n,
              data: { ...n.data, label: name, criticality },
            }
          : n
      )
    );
    setIsModalOpen(false);
    setSelectedNode(null);
  }, [selectedNode]);

  const onDragStart = useCallback((event: React.DragEvent, type: string) => {
    event.dataTransfer.setData("application/reactflow", type);
    event.dataTransfer.effectAllowed = "move";
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData("application/reactflow");
      if (!type || !reactFlowWrapper.current || !reactFlowInstance) {
        return;
      }

      const bounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      });

      setNodes((nds) => {
        const id = `${nds.length + 1}`;
        return [
          ...nds,
          {
            id,
            position,
            data: { label: type, criticality: 1 },
            type,
          },
        ];
      });
    },
    [reactFlowInstance]
  );

  const handleDeleteAll = () => {
    setNodes([]);
    setEdges([]);
  }

  return (
    <div className="min-h-screen" style={{ 
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        backgroundImage: 'url(/IrBG.jpeg)',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
       }}>
      <Navbar />

      {/* SIDEBAR */}
      <div style={{ display: "flex", flex: 1, gap: "14px", padding: "14px", overflow: "hidden"}}>
        <div
          style={{
            flex: "0 0 clamp(180px, 20vw, 280px)",
            backgroundColor: "transparent",
            padding: "16px",
            boxSizing: "border-box",
            color: "#FFFFFF",
            position: "relative",
            border: "1px solid rgba(255,255,255,1)",
            borderRadius: "8px",
            overflow: "auto",
            display: "flex",
            flexDirection: "column",
            margin: "14px 0",
          }}
        >
          <div>
            <button
              onClick={handleDeleteAll}
              style={{
                position: "absolute",
                bottom: "16px",
                right: "16px",
                background: "transparent",
                border: "none",
                cursor: "pointer",
              }}
            >
              <img
                src="/TrashCanPNG.png"
                alt="Delete all"
                style={{ width: "32px", height: "32px" }}
              />
            </button>
            <p style={{ fontSize: "0.75rem", color: "#fff" }}>
              Drag and drop components onto the canvas
              <br></br>
              <br></br>
              Double click nodes or edges to edit
              <br></br>
              <br></br>
              Click the trash can icon to clear the canvas
              <br></br>
              <br></br>
            </p>
          </div>
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              margin: 0,
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            {["Sensor", "Compute", "CommsLink", "Control", "Storage", "External"].map((type) => (
              <li key={type}>
                <button
                  type="button"
                  draggable
                  onDragStart={(event) => onDragStart(event, type)}
                  style={{
                    width: "100%",
                    height: "60px",
                    padding: "10px",
                    backgroundColor: "transparent",
                    color: "#FFFFFF",
                    border: "1px solid rgba(255,255,255,1)",
                    borderRadius: "25px",
                    textAlign: "center",
                    cursor: "grab",
                  }}
                >
                  {type}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div
          ref={reactFlowWrapper}
          style={{ flex: 1, position: "relative", margin: "14px", borderLeft: "1px solid #ccc", border: "1px solid rgba(255,255,255,1)", borderRadius: "8px", overflow: "hidden" }}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onEdgeDoubleClick={onEdgeDoubleClick}
            onNodeDoubleClick={onNodeDoubleClick}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
            connectionMode={ConnectionMode.Loose}
          >
            <Background gap={24}/>
            <Controls />
          </ReactFlow>
        </div>
      </div>
      { /* END SIDEBAR */ }

      {/* NODE EDIT MODAL */}
      <NodeEditModal
        isOpen={isModalOpen}
        nodeType={selectedNode?.type || ""}
        currentName={selectedNode?.data?.label || ""}
        currentCriticality={selectedNode?.data?.criticality || 1}
        onClose={() => setIsModalOpen(false)}
        onSave={handleNodeSave}
      />

      {/* EDGE EDIT MODAL */}
      <EdgeEditModal
        isOpen={isEdgeModalOpen}
        currentLabel={selectedEdge?.label?.toString() || ""}
        onClose={() => setIsEdgeModalOpen(false)}
        onSave={handleEdgeSave}
      />
    </div>
  );
}