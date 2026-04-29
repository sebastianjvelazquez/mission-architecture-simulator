"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';
import Link from "next/dist/client/link";

const inter = Inter({ weight: "500", subsets: ['latin'] });
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

type ArchitectureSummary = {
  id: number;
  name: string;
};

type ArchitectureDetail = {
  id: number;
  name: string;
  components: Array<{
    id: number;
    component_id: string;
    name: string;
    component_type: string;
    criticality: number;
  }>;
};

type ScenarioType = "node_compromise" | "link_degradation" | "insider_tampering";

export type SimulationResult = {
  architecture_id: number;
  scenario_type: string;
  target_component_id: string;
  baseline_score: number;
  compromised_score: number;
  score_delta: number;
  affected_components: string[];
  affected_component_names: string[];
  attack_path: string[];
  explanation: string;
};

export type CompareSimulationResult = {
  architecture_id: number;
  left: SimulationResult;
  right: SimulationResult;
};

type NavbarProps = {
  onSimulationCompleted?: (result: SimulationResult) => void;
  onCompareCompleted?: (result: CompareSimulationResult) => void;
};

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar({ onSimulationCompleted, onCompareCompleted }: NavbarProps) {
  const [modalMode, setModalMode] = useState<"run" | "compare" | null>(null);
  const [isFetchingArchitectures, setIsFetchingArchitectures] = useState(false);
  const [isFetchingComponents, setIsFetchingComponents] = useState(false);
  const [isRunningSimulation, setIsRunningSimulation] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ kind: "success" | "error"; message: string } | null>(null);
  const [architectureList, setArchitectureList] = useState<ArchitectureSummary[]>([]);
  const [selectedArchitectureId, setSelectedArchitectureId] = useState<number | null>(null);
  const [selectedScenarioType, setSelectedScenarioType] = useState<ScenarioType>("node_compromise");
  const [selectedCompareScenarioTypeLeft, setSelectedCompareScenarioTypeLeft] = useState<ScenarioType>("node_compromise");
  const [selectedCompareScenarioTypeRight, setSelectedCompareScenarioTypeRight] = useState<ScenarioType>("node_compromise");
  const [componentsForSelectedArchitecture, setComponentsForSelectedArchitecture] = useState<ArchitectureDetail["components"]>([]);
  const [selectedTargetComponentId, setSelectedTargetComponentId] = useState<string>("");
  const [selectedCompareTargetComponentIdLeft, setSelectedCompareTargetComponentIdLeft] = useState<string>("");
  const [selectedCompareTargetComponentIdRight, setSelectedCompareTargetComponentIdRight] = useState<string>("");

  const isCompareMode = modalMode === "compare";

  const resetSelections = () => {
    setSelectedArchitectureId(null);
    setComponentsForSelectedArchitecture([]);
    setSelectedTargetComponentId("");
    setSelectedScenarioType("node_compromise");
    setSelectedCompareScenarioTypeLeft("node_compromise");
    setSelectedCompareScenarioTypeRight("node_compromise");
    setSelectedCompareTargetComponentIdLeft("");
    setSelectedCompareTargetComponentIdRight("");
  };

  const showToast = (kind: "success" | "error", message: string) => {
    setToast({ kind, message });
  };

  useEffect(() => {
    if (!toast) {
      return;
    }

    const timeout = window.setTimeout(() => setToast(null), 2800);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  const runSimulationRequest = async (
    architectureId: number,
    scenarioType: ScenarioType,
    targetComponentId: string,
  ): Promise<SimulationResult> => {
    const query = new URLSearchParams({
      scenario_type: scenarioType,
      target_component_id: targetComponentId,
    }).toString();

    const response = await fetch(
      `${API_BASE_URL}/architectures/${architectureId}/simulate?${query}`,
      { method: "POST" }
    );

    if (!response.ok) {
      let detail = "Simulation failed.";
      try {
        const errBody = await response.json();
        detail = errBody?.detail || detail;
      } catch {
        // KEEP FALLBACK WHEN RESPONSE !JSON
      }
      throw new Error(detail);
    }

    return response.json();
  };

  const handleOpenModal = async (mode: "run" | "compare") => {
    setRunError(null);
    setIsFetchingArchitectures(true);

    try {
      const response = await fetch(`${API_BASE_URL}/architectures`);
      if (!response.ok) {
        throw new Error("Failed to fetch saved architectures.");
      }

      const list: ArchitectureSummary[] = await response.json();
      setArchitectureList(list);
      resetSelections();
      setModalMode(mode);
    } catch (error) {
      console.error("Error fetching architecture list:", error);
      setRunError("Unable to load saved architectures. Please try again.");
      showToast("error", "Unable to load saved architectures.");
    } finally {
      setIsFetchingArchitectures(false);
    }
  };

  useEffect(() => {
    if (modalMode) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [modalMode]);

  useEffect(() => {
    const loadArchitectureComponents = async () => {
      if (!selectedArchitectureId) {
        setComponentsForSelectedArchitecture([]);
        setSelectedTargetComponentId("");
        setSelectedCompareTargetComponentIdLeft("");
        setSelectedCompareTargetComponentIdRight("");
        return;
      }

      setRunError(null);
      setIsFetchingComponents(true);

      try {
        const response = await fetch(`${API_BASE_URL}/architectures/${selectedArchitectureId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch selected architecture details.");
        }

        const architecture: ArchitectureDetail = await response.json();
        setComponentsForSelectedArchitecture(architecture.components);

        if (architecture.components.length > 0) {
          setSelectedTargetComponentId(architecture.components[0].component_id);
          setSelectedCompareTargetComponentIdLeft(architecture.components[0].component_id);
          setSelectedCompareTargetComponentIdRight(
            architecture.components[1]?.component_id ?? architecture.components[0].component_id,
          );
        } else {
          setSelectedTargetComponentId("");
          setSelectedCompareTargetComponentIdLeft("");
          setSelectedCompareTargetComponentIdRight("");
        }
      } catch (error) {
        console.error("Error fetching selected architecture details:", error);
        setRunError("Unable to load components for this architecture.");
        showToast("error", "Unable to load components for the selected architecture.");
        setComponentsForSelectedArchitecture([]);
        setSelectedTargetComponentId("");
        setSelectedCompareTargetComponentIdLeft("");
        setSelectedCompareTargetComponentIdRight("");
      } finally {
        setIsFetchingComponents(false);
      }
    };

    if (modalMode) {
      loadArchitectureComponents();
    }
  }, [selectedArchitectureId, modalMode]);

  const handleRunSimulation = async () => {
    if (!selectedArchitectureId) {
      setRunError("Please select a saved architecture.");
      return;
    }

    if (!selectedTargetComponentId) {
      setRunError("Please select a target component.");
      return;
    }

    setRunError(null);
    setIsRunningSimulation(true);

    try {
      const data = await runSimulationRequest(
        selectedArchitectureId,
        selectedScenarioType,
        selectedTargetComponentId,
      );
      onSimulationCompleted?.(data);
      showToast("success", "Simulation completed successfully.");
      setModalMode(null);
    } catch (error) {
      console.error("Error running simulation:", error);
      setRunError(error instanceof Error ? error.message : "Simulation failed. Please try again.");
      showToast("error", error instanceof Error ? error.message : "Simulation failed.");
    } finally {
      setIsRunningSimulation(false);
    }
  };

  const handleCompareSimulation = async () => {
    if (!selectedArchitectureId) {
      setRunError("Please select a saved architecture.");
      return;
    }

    if (!selectedCompareTargetComponentIdLeft || !selectedCompareTargetComponentIdRight) {
      setRunError("Please select two target components.");
      return;
    }

    setRunError(null);
    setIsRunningSimulation(true);

    try {
      const [left, right] = await Promise.all([
        runSimulationRequest(
          selectedArchitectureId,
          selectedCompareScenarioTypeLeft,
          selectedCompareTargetComponentIdLeft,
        ),
        runSimulationRequest(
          selectedArchitectureId,
          selectedCompareScenarioTypeRight,
          selectedCompareTargetComponentIdRight,
        ),
      ]);

      onCompareCompleted?.({
        architecture_id: selectedArchitectureId,
        left,
        right,
      });
      showToast("success", "Scenario comparison completed successfully.");
      setModalMode(null);
    } catch (error) {
      console.error("Error running compare simulation:", error);
      setRunError(error instanceof Error ? error.message : "Comparison failed. Please try again.");
      showToast("error", error instanceof Error ? error.message : "Comparison failed.");
    } finally {
      setIsRunningSimulation(false);
    }
  };

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
                <Link href="/" style={{margin: "0", fontSize: "16px"}}>Home</Link>
              </button>
            </li>
          </ul>
        </div>

        <div style={{ position: "fixed", right: "24px", marginTop: "20px", display: "flex", gap: "8px" }}>
          <button
            onClick={() => handleOpenModal("compare")}
            disabled={isFetchingArchitectures || isRunningSimulation}
            className="inline-flex items-center gap-2 rounded-md border border-gray-700 bg-gray-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-gray-500 disabled:cursor-not-allowed disabled:bg-gray-800/70"
            style={{ opacity: isFetchingArchitectures || isRunningSimulation ? 0.75 : 1 }}
          >
            {(isFetchingArchitectures || isRunningSimulation) && (
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
            Compare
          </button>

          <button
            onClick={() => handleOpenModal("run")}
            disabled={isFetchingArchitectures || isRunningSimulation}
            className="inline-flex items-center gap-2 rounded-md border border-emerald-700 bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-800/70"
            style={{ opacity: isFetchingArchitectures || isRunningSimulation ? 0.75 : 1 }}
          >
            {(isFetchingArchitectures || isRunningSimulation) && (
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
            Run
          </button>
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

    {modalMode && (
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
          minWidth: isCompareMode ? "920px" : "460px",
          color: "white",
          border: "1px solid rgba(255,255,255,0.12)",
        }}>
          <h2 style={{ marginTop: 0, marginBottom: "18px" }}>
            {isCompareMode ? "Compare Scenarios" : "Run Simulation"}
          </h2>

          <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
            Saved Architecture
          </label>
          <select
            value={selectedArchitectureId ?? ""}
            onChange={(e) => {
              const nextValue = e.target.value ? Number(e.target.value) : null;
              setSelectedArchitectureId(nextValue);
            }}
            disabled={isFetchingArchitectures || isRunningSimulation}
            style={{
              width: "100%",
              padding: "10px",
              marginBottom: "14px",
              borderRadius: "4px",
              border: "1px solid #333",
              backgroundColor: "#0a0a0a",
              color: "white",
              fontSize: "14px",
              boxSizing: "border-box",
              opacity: isFetchingArchitectures || isRunningSimulation ? 0.75 : 1,
              cursor: isFetchingArchitectures || isRunningSimulation ? "not-allowed" : "pointer",
            }}
          >
            <option value="">Select a saved architecture...</option>
            {architectureList.map((architecture) => (
              <option key={architecture.id} value={architecture.id}>
                {architecture.name} (ID: {architecture.id})
              </option>
            ))}
          </select>

          {isCompareMode ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
                  Scenario A
                </label>
                <select
                  value={selectedCompareScenarioTypeLeft}
                  onChange={(e) => setSelectedCompareScenarioTypeLeft(e.target.value as ScenarioType)}
                  style={{
                    width: "100%",
                    padding: "10px",
                    marginBottom: "14px",
                    borderRadius: "4px",
                    border: "1px solid #333",
                    backgroundColor: "#0a0a0a",
                    color: "white",
                    fontSize: "14px",
                    boxSizing: "border-box",
                  }}
                >
                  <option value="node_compromise">Node Compromise</option>
                  <option value="link_degradation">Link Degradation</option>
                  <option value="insider_tampering">Insider Tampering</option>
                </select>

                <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
                  Target Component A
                </label>
                <select
                  value={selectedCompareTargetComponentIdLeft}
                  onChange={(e) => setSelectedCompareTargetComponentIdLeft(e.target.value)}
                  disabled={!selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0}
                  style={{
                    width: "100%",
                    padding: "10px",
                    marginBottom: "10px",
                    borderRadius: "4px",
                    border: "1px solid #333",
                    backgroundColor: "#0a0a0a",
                    color: "white",
                    fontSize: "14px",
                    boxSizing: "border-box",
                    opacity: !selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0 ? 0.75 : 1,
                    cursor: !selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0 ? "not-allowed" : "pointer",
                  }}
                >
                  <option value="">
                    {!selectedArchitectureId
                      ? "Select an architecture first..."
                      : isFetchingComponents
                        ? "Loading components..."
                        : componentsForSelectedArchitecture.length === 0
                          ? "No components found"
                          : "Select target component..."}
                  </option>
                  {componentsForSelectedArchitecture.map((component) => (
                    <option key={`left-${component.id}`} value={component.component_id}>
                      {component.name} ({component.component_type}) - Criticality {component.criticality}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
                  Scenario B
                </label>
                <select
                  value={selectedCompareScenarioTypeRight}
                  onChange={(e) => setSelectedCompareScenarioTypeRight(e.target.value as ScenarioType)}
                  style={{
                    width: "100%",
                    padding: "10px",
                    marginBottom: "14px",
                    borderRadius: "4px",
                    border: "1px solid #333",
                    backgroundColor: "#0a0a0a",
                    color: "white",
                    fontSize: "14px",
                    boxSizing: "border-box",
                  }}
                >
                  <option value="node_compromise">Node Compromise</option>
                  <option value="link_degradation">Link Degradation</option>
                  <option value="insider_tampering">Insider Tampering</option>
                </select>

                <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
                  Target Component B
                </label>
                <select
                  value={selectedCompareTargetComponentIdRight}
                  onChange={(e) => setSelectedCompareTargetComponentIdRight(e.target.value)}
                  disabled={!selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0}
                  style={{
                    width: "100%",
                    padding: "10px",
                    marginBottom: "10px",
                    borderRadius: "4px",
                    border: "1px solid #333",
                    backgroundColor: "#0a0a0a",
                    color: "white",
                    fontSize: "14px",
                    boxSizing: "border-box",
                    opacity: !selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0 ? 0.75 : 1,
                    cursor: !selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0 ? "not-allowed" : "pointer",
                  }}
                >
                  <option value="">
                    {!selectedArchitectureId
                      ? "Select an architecture first..."
                      : isFetchingComponents
                        ? "Loading components..."
                        : componentsForSelectedArchitecture.length === 0
                          ? "No components found"
                          : "Select target component..."}
                  </option>
                  {componentsForSelectedArchitecture.map((component) => (
                    <option key={`right-${component.id}`} value={component.component_id}>
                      {component.name} ({component.component_type}) - Criticality {component.criticality}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ) : (
            <>
              <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
                Scenario Type
              </label>
              <select
                value={selectedScenarioType}
                onChange={(e) => setSelectedScenarioType(e.target.value as ScenarioType)}
                style={{
                  width: "100%",
                  padding: "10px",
                  marginBottom: "14px",
                  borderRadius: "4px",
                  border: "1px solid #333",
                  backgroundColor: "#0a0a0a",
                  color: "white",
                  fontSize: "14px",
                  boxSizing: "border-box",
                }}
              >
                <option value="node_compromise">Node Compromise</option>
                <option value="link_degradation">Link Degradation</option>
                <option value="insider_tampering">Insider Tampering</option>
              </select>

              <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
                Target Component
              </label>
              <select
                value={selectedTargetComponentId}
                onChange={(e) => setSelectedTargetComponentId(e.target.value)}
                disabled={!selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0}
                style={{
                  width: "100%",
                  padding: "10px",
                  marginBottom: "10px",
                  borderRadius: "4px",
                  border: "1px solid #333",
                  backgroundColor: "#0a0a0a",
                  color: "white",
                  fontSize: "14px",
                  boxSizing: "border-box",
                  opacity: !selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0 ? 0.75 : 1,
                  cursor: !selectedArchitectureId || isFetchingComponents || componentsForSelectedArchitecture.length === 0 ? "not-allowed" : "pointer",
                }}
              >
                <option value="">
                  {!selectedArchitectureId
                    ? "Select an architecture first..."
                    : isFetchingComponents
                      ? "Loading components..."
                      : componentsForSelectedArchitecture.length === 0
                        ? "No components found"
                        : "Select target component..."}
                </option>
                {componentsForSelectedArchitecture.map((component) => (
                  <option key={component.id} value={component.component_id}>
                    {component.name} ({component.component_type}) - Criticality {component.criticality}
                  </option>
                ))}
              </select>
            </>
          )}

          {runError && (
            <div style={{ marginBottom: "12px", fontSize: "13px", color: "#fca5a5" }}>
              {runError}
            </div>
          )}

          <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end", marginTop: "12px" }}>
            <button
              onClick={() => {
                setModalMode(null);
                setRunError(null);
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
            {isCompareMode ? (
              <button
                onClick={handleCompareSimulation}
                disabled={
                  isRunningSimulation ||
                  !selectedArchitectureId ||
                  !selectedCompareTargetComponentIdLeft ||
                  !selectedCompareTargetComponentIdRight ||
                  isFetchingComponents
                }
                style={{
                  padding: "10px 20px",
                  backgroundColor:
                    isRunningSimulation || !selectedArchitectureId || !selectedCompareTargetComponentIdLeft || !selectedCompareTargetComponentIdRight || isFetchingComponents
                      ? "#166534"
                      : "#16a34a",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor:
                    isRunningSimulation || !selectedArchitectureId || !selectedCompareTargetComponentIdLeft || !selectedCompareTargetComponentIdRight || isFetchingComponents
                      ? "not-allowed"
                      : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                {isRunningSimulation && (
                  <span
                    aria-label="Running"
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
                {isRunningSimulation ? "Comparing..." : "Compare"}
              </button>
            ) : (
              <button
                onClick={handleRunSimulation}
                disabled={
                  isRunningSimulation ||
                  !selectedArchitectureId ||
                  !selectedTargetComponentId ||
                  isFetchingComponents
                }
                style={{
                  padding: "10px 20px",
                  backgroundColor:
                    isRunningSimulation || !selectedArchitectureId || !selectedTargetComponentId || isFetchingComponents
                      ? "#166534"
                      : "#16a34a",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor:
                    isRunningSimulation || !selectedArchitectureId || !selectedTargetComponentId || isFetchingComponents
                      ? "not-allowed"
                      : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                {isRunningSimulation && (
                  <span
                    aria-label="Running"
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
                {isRunningSimulation ? "Running..." : "Run"}
              </button>
            )}
          </div>
        </div>
      </div>
    )}
    </>
  );
}
