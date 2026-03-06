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
        border: "1px solid white",
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
        border: "1px solid white",
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
        border: "1px solid white",
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
        border: "1px solid white",
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
        border: "1px solid white",
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
        border: "1px solid white",
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
/*
Story: As a mission planner, I want to set CIA requirements on data flows for realistic simulations.
Acceptance Criteria:
1 [x] Double-clicking edge opens properties modal
2 [x] Can set: label, data_type, cia_requirement (dropdown), latency_sensitivity
3 [X] Changes reflected in edge state and visual labels (no visual label for other things but would look cluttered)
4 [x] CIA properties sent to backend when saving (should be covered just with save logic already since its in data)
5 [3] Visual indicator on edges showing CIA type (idk what this looks like yet, maybe a small colored dot or icon with tooltip on hover?)
*/
interface EdgeModalProps {
  isOpen: boolean;
  currentLabel: string;
  currentDataTypeEdge: string;
  currentCiaRequirement: string;
  currentLatencySensitivity: string;
  onClose: () => void;
  onSave: (label: string, dataTypeEdge: string, ciaRequirement: string, latencySensitivity: string) => void;
}


// CONNECTION/EDGE EDIT MODAL FUNCTION
function EdgeEditModal({ isOpen, currentLabel, currentDataTypeEdge, currentCiaRequirement, currentLatencySensitivity, onClose, onSave }: EdgeModalProps) {
  const [label, setLabel] = useState(currentLabel);
  const [dataTypeEdge, setDataTypeEdge] = useState(currentDataTypeEdge);
  const [ciaRequirement, setCiaRequirement] = useState(currentCiaRequirement);
  const [latencySensitivity, setLatencySensitivity] = useState(currentLatencySensitivity);

  // UPDATE LABEL STATE WHEN MODAL OPENS WITH NEW EDGE DATA
  React.useEffect(() => {
    if (isOpen) {
      setLabel(currentLabel);
      setDataTypeEdge(currentDataTypeEdge);
      setCiaRequirement(currentCiaRequirement);
      setLatencySensitivity(currentLatencySensitivity);
    }
  }, [isOpen, currentLabel, currentDataTypeEdge, currentCiaRequirement, currentLatencySensitivity]);

  const handleSave = () => {
    onSave(label, dataTypeEdge, ciaRequirement, latencySensitivity);
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

        <br></br>

        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>Data Type:</span>
          <input
            type="text"
            value={dataTypeEdge ?? ""}
            onChange={(e) => setDataTypeEdge(e.target.value)}
            placeholder="Enter data type"
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

        <br></br>

        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>CIA Requirement:</span>
          <select
            value={ciaRequirement ?? ""}
            onChange={(e) => setCiaRequirement(e.target.value)}
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
            <option value="">Select CIA Requirement</option>
            <option value="Confidentiality">Confidentiality</option>
            <option value="Integrity">Integrity</option>
            <option value="Availability">Availability</option>
          </select>
        </label>

        <br></br>

        <label style={{ display: "block", marginBottom: "15px" }}>
          <span>Latency Sensitivity:</span>
          <input
            type="text"
            value={latencySensitivity ?? ""}
            onChange={(e) => setLatencySensitivity(e.target.value)}
            placeholder="Enter latency sensitivity"
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
          strokeWidth: 2,
        },
        label: "",
        labelStyle: { fill: "#fff", fontWeight: 500 },
        labelBgStyle: { fill: "#141414"},
        data: {
          sourceNodeType: sourceNode?.type,
          targetNodeType: targetNode?.type,
          dataTypeEdge: "",
          ciaRequirement: "",
          latencySensitivity: "",
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
  const handleEdgeSave = useCallback((label: string, dataTypeEdge: string, ciaRequirement: string, latencySensitivity: string) => {
    setEdges((eds) =>
      eds.map((e) =>
        e.id === selectedEdge?.id ? { ...e, label, data: { ...e.data, dataTypeEdge, ciaRequirement, latencySensitivity } } : e
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
        backgroundImage: 'url(/BluePurp.jpeg)',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
       }}>
      <Navbar 
        nodes={nodes}
        edges={edges}
        setNodes={setNodes}
        setEdges={setEdges}
      />

      {/* SIDEBAR */}
      <div style={{ display: "flex", flex: 1, gap: "14px", padding: "14px", overflow: "hidden"}}>
        <div
          style={{
            flex: "0 0 clamp(200px, 20vw, 280px)",
            backgroundColor: "rgba(15, 15, 20, 0.85)",
            padding: "0",
            boxSizing: "border-box",
            color: "#FFFFFF",
            position: "relative",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: "4px",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
            margin: "14px 0",
            backdropFilter: "blur(10px)",
          }}
        >
          {/* HEADER CONTAINER */}
          <div style={{
            padding: "20px 20px 16px",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          }}>
            <h3 style={{
              margin: 0,
              fontSize: "0.75rem",
              fontWeight: 500,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "#A0A0A8",
            }}>
              Components
            </h3>
          </div>

          {/* INSTRUCTIONS CONTAINER */}
          <div style={{
            padding: "16px 20px",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          }}>
            <div style={{
              fontSize: "0.75rem",
              color: "#808088",
              lineHeight: "1.5",
            }}>
              <div style={{ marginBottom: "6px" }}>• Drag and drop components onto canvas</div>
              <div style={{ marginBottom: "6px" }}>• Double-click to edit nodes/edges</div>
              <div>• Connect nodes to link</div>
            </div>
          </div>

          {/* COMPONENT LIST CONTAINER */}
          <div style={{
            flex: 1,
            padding: "16px 20px",
            overflowY: "auto",
          }}>
            <ul
              style={{
                listStyle: "none",
                padding: 0,
                margin: 0,
                display: "flex",
                flexDirection: "column",
                gap: "8px",
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
                      padding: "12px 14px",
                      backgroundColor: "rgba(255, 255, 255, 0.04)",
                      color: "#FFFFFF",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      borderRadius: "3px",
                      textAlign: "left",
                      cursor: "grab",
                      fontSize: "0.85rem",
                      fontWeight: 400,
                      transition: "all 0.15s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.08)";
                      e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.2)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.04)";
                      e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)";
                    }}
                  >
                    {type}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* FOOTER CONTAINER - DELETE ACTIONS */}
          <div style={{
            padding: "16px 20px",
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
          }}>
            <button
              onClick={handleDeleteAll}
              style={{
                width: "100%",
                padding: "10px",
                background: "rgba(255, 255, 255, 0.04)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                borderRadius: "3px",
                color: "#A0A0A8",
                cursor: "pointer",
                fontSize: "0.8rem",
                fontWeight: 400,
                transition: "all 0.15s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(220, 50, 50, 0.1)";
                e.currentTarget.style.borderColor = "rgba(220, 80, 80, 0.3)";
                e.currentTarget.style.color = "#E08080";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.04)";
                e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)";
                e.currentTarget.style.color = "#A0A0A8";
              }}
            >
              Clear Canvas
            </button>
          </div>
        </div>
        { /* END SIDEBAR */ }

        <div
          ref={reactFlowWrapper}
          style={{
            flex: 1,
            position: "relative",
            margin: "14px",
            backgroundColor: "rgba(15, 15, 20, 0.85)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: "4px",
            overflow: "hidden",
            backdropFilter: "blur(10px)",
          }}
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
        currentDataTypeEdge={selectedEdge?.data?.dataTypeEdge || ""}
        currentCiaRequirement={selectedEdge?.data?.ciaRequirement || ""}
        currentLatencySensitivity={selectedEdge?.data?.latencySensitivity || ""}
        onClose={() => setIsEdgeModalOpen(false)}
        onSave={handleEdgeSave}
      />
    </div>
  );
}