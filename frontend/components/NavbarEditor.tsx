"use client";

import React, { useState } from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';
import Link from "next/dist/client/link";
import { Node, Edge, MarkerType } from "reactflow";

const inter = Inter({ weight: "500", subsets: ['latin'] });
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

type ArchitectureSummary = {
  id: number;
  name: string;
};
type ArchitecturePayload = {
  name: string;
  description: string;
  properties: Record<string, unknown>;
  components: Array<{
    component_id: string;
    name: string;
    component_type: string;
    criticality: number;
    position_x: number;
    position_y: number;
  }>;
  flows: Array<{
    source_component_id: string;
    target_component_id: string;
    data_type: string;
    cia_requirement: string;
    latency_sensitivity: string;
    source_handle: string;
    target_handle: string;
  }>;
};

type LoadedArchitecture = {
  id: number;
  name: string;
  components: Array<{
    id: number;
    component_id: string;
    name: string;
    component_type: string;
    criticality: number;
    position_x: number | null;
    position_y: number | null;
  }>;
  flows: Array<{
    id: number;
    source_component_id: number;
    target_component_id: number;
    data_type: string | null;
    cia_requirement: string | null;
    latency_sensitivity: string | null;
    source_handle: string | null;
    target_handle: string | null;
  }>;
};

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar({ nodes, edges, setNodes, setEdges}: {
  nodes: Node[];
  edges: Edge[];
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
}) {
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [modelName, setModelName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [architectureList, setArchitectureList] = useState<ArchitectureSummary[]>([]);
  const [selectedArchitectureId, setSelectedArchitectureId] = useState<number | null>(null);
  const [currentArchitectureId, setCurrentArchitectureId] = useState<number | null>(null);
  const [currentArchitectureName, setCurrentArchitectureName] = useState("Architecture");
  const [toast, setToast] = useState<{ kind: "success" | "error"; message: string } | null>(null);

  const isMitigationComponentType = (componentType?: string | null) =>
    componentType === "Redundancy" || componentType === "ValidationGate" || componentType === "SegmentationBoundary";

  const getEdgeStyle = (sourceType?: string | null, targetType?: string | null) => {
    if (isMitigationComponentType(sourceType) || isMitigationComponentType(targetType)) {
      return {
        stroke: "#38bdf8",
        strokeWidth: 2,
        strokeDasharray: "6 4",
      };
    }

    return {
      stroke: "#fff",
      strokeWidth: 2,
    };
  };

  const showToast = (kind: "success" | "error", message: string) => {
    setToast({ kind, message });
  };

  React.useEffect(() => {
    if (!toast) {
      return;
    }

    const timeout = window.setTimeout(() => setToast(null), 2600);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  const buildPayload = (name: string): ArchitecturePayload => ({
    name,
    description: "",
    properties: {},
    components: nodes.map((node) => ({
      component_id: node.id,
      name: String(node.data?.label ?? node.id),
      component_type: node.type ?? "Compute",
      criticality: Number(node.data?.criticality ?? 1),
      position_x: node.position.x,
      position_y: node.position.y,
    })),
    flows: edges.map((edge) => ({
      source_component_id: edge.source ?? "",
      target_component_id: edge.target ?? "",
      data_type: String(edge.data?.dataTypeEdge ?? ""),
      cia_requirement: String(edge.data?.ciaRequirement ?? ""),
      latency_sensitivity: String(edge.data?.latencySensitivity ?? ""),
      source_handle: edge.sourceHandle ?? "right",
      target_handle: edge.targetHandle ?? "left",
    })),
  });

  const applyArchitectureToCanvas = (architecture: LoadedArchitecture) => {
    const componentTypeLookup = new Map<number, string>();
    for (const component of architecture.components) {
      componentTypeLookup.set(component.id, component.component_type);
    }

    const dbIdToFrontendId = new Map<number, string>();
    for (const component of architecture.components) {
      dbIdToFrontendId.set(component.id, component.component_id);
    }

    const loadedNodes: Node[] = architecture.components.map((component) => ({
      id: component.component_id,
      type: component.component_type,
      position: {
        x: component.position_x ?? 0,
        y: component.position_y ?? 0,
      },
      data: {
        label: component.name,
        criticality: component.criticality,
        variant:
          component.component_type === "ValidationGate"
            ? "validation_gate"
            : component.component_type === "SegmentationBoundary"
              ? "segmentation_boundary"
              : component.component_type === "Redundancy"
                ? "redundancy"
                : undefined,
      },
    }));

    const loadedEdges: Edge[] = architecture.flows
      .map((flow) => {
        const source = dbIdToFrontendId.get(flow.source_component_id);
        const target = dbIdToFrontendId.get(flow.target_component_id);

        if (!source || !target) {
          return null;
        }

        return {
          id: `e-${flow.id}`,
          source,
          target,
          sourceHandle: flow.source_handle ?? 'right',
          targetHandle: flow.target_handle ?? 'left',
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: isMitigationComponentType(componentTypeLookup.get(flow.source_component_id)) || isMitigationComponentType(componentTypeLookup.get(flow.target_component_id)) ? '#38bdf8' : '#fff',
          },
          style: getEdgeStyle(componentTypeLookup.get(flow.source_component_id), componentTypeLookup.get(flow.target_component_id)),
          label: flow.data_type ?? '',
          labelStyle: { fill: '#fff', fontWeight: 500 },
          labelBgStyle: { fill: '#141414' },
          data: {
            dataTypeEdge: flow.data_type ?? '',
            ciaRequirement: flow.cia_requirement ?? '',
            latencySensitivity: flow.latency_sensitivity ?? '',
          },
        } as Edge;
      })
      .filter((edge): edge is Edge => edge !== null);

    setNodes(loadedNodes);
    setEdges(loadedEdges);
    setCurrentArchitectureId(architecture.id);
    setCurrentArchitectureName(architecture.name);
    setModelName(architecture.name);
  };

  const persistArchitecture = async (name: string) => {
    setIsLoading(true);

    try {
      const payload = buildPayload(name);
      const shouldUpdate = Boolean(currentArchitectureId);
      const response = await fetch(
        shouldUpdate ? `${API_BASE_URL}/architectures/${currentArchitectureId}` : `${API_BASE_URL}/architectures`,
        {
          method: shouldUpdate ? "PUT" : "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || (shouldUpdate ? "Failed to update architecture" : "Failed to save architecture"));
      }

      const data = await response.json();
      setCurrentArchitectureId(data.id);
      setCurrentArchitectureName(data.name);
      setModelName(data.name);
      showToast("success", `Saved as ${data.name}.`);
      return data as LoadedArchitecture;
    } catch (error) {
      console.error("Error saving architecture:", error);
      showToast("error", error instanceof Error ? error.message : "Failed to save architecture.");
      throw error;
    } finally {
      setIsLoading(false);
    }
  };


  const handleSave = async () => {
    const nextName = modelName.trim();
    if (!nextName) {
      showToast("error", "Please enter a model name.");
      return;
    }

    await persistArchitecture(nextName);
    setShowSaveModal(false);
  };

  const handleCloneArchitecture = async () => {
    if (!currentArchitectureId) {
      showToast("error", "Load or save an architecture before cloning.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/architectures/${currentArchitectureId}/clone`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || "Failed to clone architecture.");
      }

      const architecture: LoadedArchitecture = await response.json();
      applyArchitectureToCanvas(architecture);
      showToast("success", `Cloned as ${architecture.name}.`);
    } catch (error) {
      console.error("Error cloning architecture:", error);
      showToast("error", error instanceof Error ? error.message : "Failed to clone architecture.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoad = async () => {
    setIsLoading(true);

    try{
      const response = await fetch(`${API_BASE_URL}/architectures`);
      if (!response.ok) {
        throw new Error('Failed to fetch architecture list');
      }
      const list = await response.json();

      setArchitectureList(list);
      setSelectedArchitectureId(null);
      setShowLoadModal(true);
    } catch (error) {
      console.error('Error fetching architectures:', error);
      showToast('error', 'Unable to load saved architectures. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadSelectedArchitecture = async () => {
    if (!selectedArchitectureId) {
      showToast('error', 'Please select an architecture to load.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/architectures/${selectedArchitectureId}`
      );
      if (!response.ok) {
        throw new Error('Failed to fetch selected architecture');
      }

      const architecture: LoadedArchitecture = await response.json();
      applyArchitectureToCanvas(architecture);
      setShowLoadModal(false);
      setSelectedArchitectureId(null);
      showToast("success", `Loaded ${architecture.name}.`);
    } catch (error) {
      console.error('Error loading selected architecture:', error);
      showToast('error', 'Failed to load selected architecture. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    if (showSaveModal || showLoadModal) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [showSaveModal, showLoadModal]);

  return (
    <>
    <div className="container mx-auto px-6 py-2 space-y-6 max-w-7x5">
      <nav 
      className={inter.className}
      style={{
        width: "100%",
        height: "0px",
        backgroundColor: "transparent",
        color: "white",
        display: "flex",
        alignItems: "center",
        padding: "10px 10px",
        boxSizing: "border-box",
        position: "relative",
        justifyContent: "center",
      }}>
        <Image 
          src="/TextMAS.svg"
          alt="Logo" 
          width={365}
          height={50}
          style={{position: "fixed", marginTop: "20px", objectFit: "contain", left: "40px" }}
        />
        
        <div style={{
          // NAVBAR ELIPSE SHAPE
          //backgroundColor: "rgba(15, 15, 20, 0.85)",
          //borderRadius: "25px",
          padding: "5px 15px",
          //border: "1px solid #333",
          marginTop: "20px",
        }}>
          <ul style={{
            display: "flex",
            listStyle: "none",
            margin: 0,
            padding: 0,
            gap: "0px",
          }}>
            <li>
              <button
                id="load-button"
                onClick={handleLoad}
                disabled={isLoading}
                style={{
                  padding: "10px 16px",
                  backgroundColor: "transparent",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px", 
                  opacity: isLoading ? 0.75 : 1,
                }}
              >
                {isLoading && (
                  <span
                    aria-label="Loading"
                    style={{
                      width: "14px",
                      height: "14px",
                      border: "2px solid rgba(255,255,255,0.35)",
                      borderTop: "2px solid #ffffff",
                      borderRadius: "50%",
                      display: "inline-block",
                      animation: "spin 0.8s linear infinite",
                    }}
                  />
                )}
                <h3 style={{margin: "0", fontSize: "16px"}}>Load</h3>
              </button>
            </li>
            <li>
              <button 
                id="save-button"
                disabled={isLoading}
                onClick={() => {
                  setModelName(currentArchitectureName);
                  setShowSaveModal(true);
                }}
                style={{
                  padding: "10px 16px",
                  backgroundColor: "transparent",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  opacity: isLoading ? 0.75 : 1,
                }}
              > 
                <h3 style={{margin: "0", fontSize: "16px"}}>Save</h3>
              </button>
            </li>
            <li>
              <button
                id="clone-button"
                onClick={handleCloneArchitecture}
                disabled={isLoading || !currentArchitectureId}
                style={{
                  padding: "10px 16px",
                  backgroundColor: "transparent",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: isLoading || !currentArchitectureId ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  opacity: isLoading || !currentArchitectureId ? 0.7 : 1,
                }}
                title={currentArchitectureId ? "Clone the currently loaded architecture" : "Load or save an architecture before cloning"}
              >
                <h3 style={{margin: "0", fontSize: "16px"}}>Clone Architecture</h3>
              </button>
            </li>
            <li>
              <button
                id="dashboard-button"
                style={{
                  padding: "10px 16px",
                  backgroundColor: "transparent",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <Link href="/dashboard" style={{margin: "0", fontSize: "16px"}}>Dashboard</Link>
              </button>
            </li>
          </ul>
        </div>
      </nav>
    </div>

    {toast && (
      <div
        style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          zIndex: 1100,
          padding: "12px 16px",
          borderRadius: "8px",
          color: "white",
          backgroundColor: toast.kind === "success" ? "rgba(16, 185, 129, 0.95)" : "rgba(239, 68, 68, 0.95)",
          boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
          maxWidth: "320px",
          fontSize: "14px",
        }}
      >
        {toast.message}
      </div>
    )}

    {/* SAVE MODAL DESIGN CODE */}
    {showSaveModal && (
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
      }}>
        <div style={{
          backgroundColor: "#1a1a1a",
          padding: "30px",
          borderRadius: "8px",
          minWidth: "400px",
          color: "white",
        }}>
          <h2 style={{ marginTop: 0, marginBottom: "20px" }}>Save Model</h2>
          <input
            type="text"
            placeholder="Enter model name"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            style={{
              width: "100%",
              padding: "10px",
              marginBottom: "20px",
              borderRadius: "4px",
              border: "1px solid #333",
              backgroundColor: "#0a0a0a",
              color: "white",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
          <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
            <button
              onClick={() => {
                setShowSaveModal(false);
                setModelName("");
              }}
              style={{
                padding: "10px 20px",
                backgroundColor: "#333",
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
              disabled={!modelName.trim() || isLoading}
              style={{
                padding: "10px 20px",
                backgroundColor: modelName.trim() && !isLoading ? "#0070f3" : "#555",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: modelName.trim() && !isLoading ? "pointer" : "not-allowed",
              }}
            >
              Save
            </button>
          </div>
        </div>
      </div>
    )}

    {/* LOAD MODAL DESIGN CODE */}
    {showLoadModal && (
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
      }}>
        <div style={{
          backgroundColor: "#1a1a1a",
          padding: "30px",
          borderRadius: "8px",
          width: "400px",
          maxWidth: "90vw",
          color: "white",
          boxSizing: "border-box",
        }}>
          <h2 style={{ marginTop: 0, marginBottom: "20px" }}>Load Model</h2>
          <div style={{ maxHeight: "240px", overflowY: "auto", marginBottom: "20px" }}>
            {architectureList.length === 0 ? (
              <p style={{ color: "#aaa", margin: 0 }}>No saved architectures found.</p>
            ) : (
              architectureList.map((architecture) => (
                <button
                  key={architecture.id}
                  type="button"
                  onClick={() => setSelectedArchitectureId(architecture.id)}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    marginBottom: "8px",
                    padding: "10px",
                    borderRadius: "4px",
                    border:
                      selectedArchitectureId === architecture.id
                        ? "1px solid #0070f3"
                        : "1px solid #333",
                    backgroundColor:
                      selectedArchitectureId === architecture.id ? "#0b2a4a" : "#0a0a0a",
                    color: "white",
                    cursor: "pointer",
                    boxSizing: "border-box",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                  title={architecture.name}
                >
                  {architecture.name} (ID: {architecture.id})
                </button>
              ))
            )}
          </div>
          <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
            <button
              onClick={() => {
                setShowLoadModal(false);
                setSelectedArchitectureId(null);
              }}
              style={{
                padding: "10px 20px",
                backgroundColor: "#333",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleLoadSelectedArchitecture}
              disabled={!selectedArchitectureId || isLoading}
              style={{
                padding: "10px 20px",
                backgroundColor: selectedArchitectureId && !isLoading ? "#0070f3" : "#555",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: selectedArchitectureId && !isLoading ? "pointer" : "not-allowed",
              }}
            >
              Load
            </button>
          </div>
        </div>
      </div>
    )}

    {/* LOADING SPINNER CODE */}
    {/* MIGHT CHANGE, GOOD FOR NOW */}
    <style jsx>{`
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    `}</style>
    </>
  );
}
