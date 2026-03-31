"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';
import Link from "next/dist/client/link";

const inter = Inter({ weight: "500", subsets: ['latin'] });

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

type NavbarProps = {
  onSimulationCompleted?: (result: SimulationResult) => void;
};

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar({ onSimulationCompleted }: NavbarProps) {
  const [showRunModal, setShowRunModal] = useState(false);
  const [isFetchingArchitectures, setIsFetchingArchitectures] = useState(false);
  const [isFetchingComponents, setIsFetchingComponents] = useState(false);
  const [isRunningSimulation, setIsRunningSimulation] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [architectureList, setArchitectureList] = useState<ArchitectureSummary[]>([]);
  const [selectedArchitectureId, setSelectedArchitectureId] = useState<number | null>(null);
  const [selectedScenarioType, setSelectedScenarioType] = useState<ScenarioType>("node_compromise");
  const [componentsForSelectedArchitecture, setComponentsForSelectedArchitecture] = useState<ArchitectureDetail["components"]>([]);
  const [selectedTargetComponentId, setSelectedTargetComponentId] = useState<string>("");

  useEffect(() => {
    if (showRunModal) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [showRunModal]);

  const handleOpenRunModal = async () => {
    setRunError(null);
    setIsFetchingArchitectures(true);

    try {
      const response = await fetch("http://localhost:8000/architectures");
      if (!response.ok) {
        throw new Error("Failed to fetch saved architectures.");
      }

      const list: ArchitectureSummary[] = await response.json();
      setArchitectureList(list);
      setSelectedArchitectureId(null);
      setComponentsForSelectedArchitecture([]);
      setSelectedTargetComponentId("");
      setSelectedScenarioType("node_compromise");
      setShowRunModal(true);
    } catch (error) {
      console.error("Error fetching architecture list:", error);
      setRunError("Unable to load saved architectures. Please try again.");
    } finally {
      setIsFetchingArchitectures(false);
    }
  };

  useEffect(() => {
    const loadArchitectureComponents = async () => {
      if (!selectedArchitectureId) {
        setComponentsForSelectedArchitecture([]);
        setSelectedTargetComponentId("");
        return;
      }

      setRunError(null);
      setIsFetchingComponents(true);

      try {
        const response = await fetch(`http://localhost:8000/architectures/${selectedArchitectureId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch selected architecture details.");
        }

        const architecture: ArchitectureDetail = await response.json();
        setComponentsForSelectedArchitecture(architecture.components);

        if (architecture.components.length > 0) {
          setSelectedTargetComponentId(architecture.components[0].component_id);
        } else {
          setSelectedTargetComponentId("");
        }
      } catch (error) {
        console.error("Error fetching selected architecture details:", error);
        setRunError("Unable to load components for this architecture.");
        setComponentsForSelectedArchitecture([]);
        setSelectedTargetComponentId("");
      } finally {
        setIsFetchingComponents(false);
      }
    };

    if (showRunModal) {
      loadArchitectureComponents();
    }
  }, [selectedArchitectureId, showRunModal]);

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
      const query = new URLSearchParams({
        scenario_type: selectedScenarioType,
        target_component_id: selectedTargetComponentId,
      }).toString();

      const response = await fetch(
        `http://localhost:8000/architectures/${selectedArchitectureId}/simulate?${query}`,
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

      const data: SimulationResult = await response.json();
      onSimulationCompleted?.(data);
      setShowRunModal(false);
    } catch (error) {
      console.error("Error running simulation:", error);
      setRunError(error instanceof Error ? error.message : "Simulation failed. Please try again.");
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
            onClick={handleOpenRunModal}
            disabled={isFetchingArchitectures || isRunningSimulation}
            className="inline-flex items-center gap-2 rounded-md border border-gray-700 bg-gray-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-gray-500 disabled:cursor-not-allowed disabled:bg-gray-800/70"
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
            onClick={handleOpenRunModal}
            disabled={isFetchingArchitectures || isRunningSimulation}
            className="inline-flex items-center gap-2 rounded-md border border-emerald-700 bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-800/70"
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

    {showRunModal && (
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
          minWidth: "460px",
          color: "white",
          border: "1px solid rgba(255,255,255,0.12)",
        }}>
          <h2 style={{ marginTop: 0, marginBottom: "18px" }}>Run Simulation</h2>

          <label style={{ display: "block", marginBottom: "6px", fontSize: "13px", color: "rgba(255,255,255,0.8)" }}>
            Saved Architecture
          </label>
          <select
            value={selectedArchitectureId ?? ""}
            onChange={(e) => {
              const nextValue = e.target.value ? Number(e.target.value) : null;
              setSelectedArchitectureId(nextValue);
            }}
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
            <option value="">Select a saved architecture...</option>
            {architectureList.map((architecture) => (
              <option key={architecture.id} value={architecture.id}>
                {architecture.name} (ID: {architecture.id})
              </option>
            ))}
          </select>

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

          {runError && (
            <div style={{ marginBottom: "12px", fontSize: "13px", color: "#fca5a5" }}>
              {runError}
            </div>
          )}

          <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end", marginTop: "12px" }}>
            <button
              onClick={() => {
                setShowRunModal(false);
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
          </div>
        </div>
      </div>
    )}
    </>
  );
}