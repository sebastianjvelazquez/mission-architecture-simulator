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
} from "reactflow";
import "reactflow/dist/style.css";
import Navbar from "@/components/Navbar";
import { nodeServerAppPaths } from "next/dist/build/webpack/plugins/pages-manifest-plugin";
import { on } from "events";

// ALL CUSTOM NODES
function ProcessNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        border: "1px solid #777",
        borderRadius: "5px",
        background: "black",
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

function StoreNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        border: "1px solid #777",
        borderRadius: "5px",
        background: "black",
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

function ActorNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        border: "1px solid #777",
        borderRadius: "5px",
        background: "black",
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

function FlowNode({ data }: { data: { label: string } }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        border: "1px solid #777",
        borderRadius: "5px",
        background: "black",
        // color: "white",
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

// DEFINE NODE TYPES
const nodeTypes = {
  Process: ProcessNode,
  Store: StoreNode,
  Actor: ActorNode,
  "Data Flow": FlowNode,
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

function NodeEditModal({ isOpen, nodeType, currentName, currentCriticality, onClose, onSave }: NodeModalProps) {
  const [name, setName] = useState(currentName);
  const [criticality, setCriticality] = useState(currentCriticality);

  // Update state when modal opens with new node data
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

function EdgeEditModal({ isOpen, currentLabel, onClose, onSave }: EdgeModalProps) {
  const [label, setLabel] = useState(currentLabel);

  // Update state when modal opens with new edge data
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
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Navbar />

      {/* SIDEBAR */}
      <div style={{ display: "flex", flex: 1 }}>
        <div
          style={{
            width: "220px",
            backgroundColor: "#141414",
            padding: "16px",
            boxSizing: "border-box",
            color: "#FFFFFF",
            position: "relative",
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
                style={{ width: "22px", height: "22px" }}
              />
            </button>
            <p style={{ fontSize: "0.7rem", color: "#B3B3B3" }}>
              To add a component, drag and drop it onto the canvas.
              <br></br>
              <br></br>
            </p>
            <p style={{ fontSize: "0.7rem", color: "#B3B3B3" }}>
              To delete a component, select and press delete key, or press the trash can icon to delete all.
              <br></br>
              <br></br>
            </p>
            <p style={{ fontSize: "0.7rem", color: "#B3B3B3" }}>
              To name a connection, double click anywhere on the arrow and enter your label.
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
            {["Process", "Store", "Actor", "Data Flow"].map((type) => (
              <li key={type}>
                <button
                  type="button"
                  draggable
                  onDragStart={(event) => onDragStart(event, type)}
                  style={{
                    width: "100%",
                    height: "80px",
                    padding: "10px",
                    backgroundColor: "#1A1A1A",
                    color: "#FFFFFF",
                    border: "1px solid #3A3A3A",
                    borderRadius: "12px",
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
          style={{ flex: 1, position: "relative", borderLeft: "1px solid #ccc" }}
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
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      </div>

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


// HANDLE SAVE ARCHITECTURE - SEND POST REQUEST TO BACKEND WITH NODES AND EDGES - WIP
const handleSaveArchitecture = useCallback(event {
  try {
    const response = await fetch("/backend/api/architectures", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify ({
        name: "My Architecture", // Need to prompt user for this
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type,
          data: n.data,
          position: n.position,
        })),
        edges: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.label,
          data: e.data,
        })),
        }),
    });
    const data = await response.json();
    alert("Architecture saved successfully!");
  } catch (error) { 
    alert("Error saving architecture");
  }
}, [nodes, edges]);

<Navbar onSave={handleSaveArchitecture} />