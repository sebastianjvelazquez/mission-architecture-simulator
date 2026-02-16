"use client";

import React, { useCallback, useRef, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  ReactFlowInstance,
  applyNodeChanges,
  NodeChange,
  Node,
} from "reactflow";
import "reactflow/dist/style.css";
import Navbar from "@/components/Navbar";

export default function Home() {
  // State for nodes and edges
  const [nodes, setNodes] = useState<Node<{ label: string }>[]>([
    {
      id: "1",
      position: { x: 100, y: 100 },
      data: { label: "Sensor 1" },
      type: "default",
    },
  ]);

  const [edges, setEdges] = useState([]);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);

  const onNodesChange = (changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  };

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
            type: "default",
          },
        ];
      });
    },
    [reactFlowInstance]
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* NAVBAR */}
      <Navbar />

      {/* MAIN */}
      <div style={{ display: "flex", flex: 1 }}>
        {/* SIDEBAR */}
        <div
          style={{
            width: "220px",
            backgroundColor: "#1C1C1C",
            padding: "16px",
            boxSizing: "border-box",
            color: "#FFFFFF",
          }}
        >
          <h3 style={{ margin: 0 }}>Components</h3>
          <p style={{ fontSize: "0.85rem", color: "#B3B3B3" }}>
            Drag a component and drop it onto the canvas.
            <br></br>
            <br></br>
          </p>
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
            {["Process", "Store", "Actor", "Data Flow"].map((label) => (
              <li key={label}>
                <button
                  type="button"
                  draggable
                  onDragStart={(event) => onDragStart(event, label)}
                  style={{
                    width: "100%",
                    padding: "12px",
                    backgroundColor: "#2E2E2E",
                    color: "#FFFFFF",
                    border: "1px solid #3A3A3A",
                    borderRadius: "6px",
                    textAlign: "left",
                    cursor: "grab",
                  }}
                >
                  {label}
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/*CANVAS/GRID*/}
        <div
          ref={reactFlowWrapper}
          style={{ flex: 1, position: "relative", borderLeft: "1px solid #ccc" }}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
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
