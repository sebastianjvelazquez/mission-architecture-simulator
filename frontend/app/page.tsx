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
      
      <div>{data.label}</div>
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
      
      <div>{data.label}</div>
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
      
      <div>{data.label}</div>
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
      
      <div>{data.label}</div>
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

export default function Home() {
  const [nodes, setNodes] = useState<Node<{ label: string }>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
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
      setEdges((eds) => addEdge({
        ...connection,
        
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
      }, eds));
    },
    []
  );

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
            data: { label: type },
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
            <p style={{ fontSize: "0.85rem", color: "#B3B3B3" }}>
              To add a component, drag and drop it onto the canvas.
              <br></br>
              <br></br>
            </p>
            <p style={{ fontSize: "0.85rem", color: "#B3B3B3" }}>
              To delete a component, select and press delete key, or press the trash can icon to delete all.
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
                    height: "100px",
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
    </div>
  );
}