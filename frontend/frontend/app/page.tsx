"use client";

import React, { useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  applyNodeChanges,
  NodeChange,
  Node
} from "reactflow";
import "reactflow/dist/style.css";
import Navbar from "@/components/Navbar";

export default function Home() {
  // State for nodes and edges
  const [nodes, setNodes] = useState<Node<{ label: string }>[]>([
  { id: "1", position: { x: 100, y: 100 }, data: { label: "Sensor 1" }, type: "default" },
  ]);

  const [edges, setEdges] = useState([]);

  const onNodesChange = (changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  };

  const addNode = (type: string) => {
    const id = `${nodes.length + 1}`;
    const label = type;
    setNodes([
      ...nodes,
      {
        id,
        position: { x: 50, y: 50 },
        data: { label },
        type: "default",
      },
    ]);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* NAVBAR */}
      <Navbar />

      {/* MAIN */}
      <div style={{ display: "flex", flex: 1 }}>
        {/* SIDEBAR */}
        <div
          style={{
            width: "200px",
            backgroundColor: "#1C1C1C",
            padding: "10px",
            boxSizing: "border-box",
          }}
        >
          <h3>Components</h3>
          <br></br>
          {/*COMPONENTS LIST SIDEBAR*/}
          <ul>
            <li>
              <button onClick={() => addNode("Process")}>Add Process</button>
            </li>
            <li>
              <button onClick={() => addNode("Store")}>Add Store</button>
            </li>
            <li>
              <button onClick={() => addNode("Actor")}>Add Actor</button>
            </li>
            <li>
              <button onClick={() => addNode("DataFlow")}>Add Data Flow</button>
            </li>
          </ul>
        </div>

        {/*CANVAS/GRID*/}
        <div style={{ flex: 1, position: "relative", borderLeft: "1px solid #ccc" }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
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
