"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/NavbarDashboard";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// TODO: MOVE ALL RUN AND COMPARE TO NAVBAR. LOOKS BETTER AND FITS CRITERIA MORE ACCURATELY. ALSO ALREADY HAVE GET AND POST THERE SO CAN USE DESIGN PATTERNS

/*
  FRONTEND-ONLY TYPES FOR SIMULATION FLOW
  Light TypeScript types used only by this dashboard page
  Mirrora response shapes already exposed by the backend APIs so this page
  can safely call existing endpoints without changing anything in backend
*/
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

type SimulationResult = {
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

// SAMPLE DATA, REPLACE WITH REAL DATA
// DB IS NOW WORKING, NEED TO GRAB FROM BACKEND AND FORMAT PROPERLY FOR CHARTS AND TABLES
// OVERHAUL OF DASHBOARD ESSENTIALLY

/*
FROM SIMULATOR.PY, THIS IS WHAT WE WILL BE BUILDING THE CHARTS BASED ON
def _build_explanation(
        self,
        scenario_type: str,
        target_id: str,
        affected_ids: set[str],
        baseline_score: float,
        compromised_score: float,
    ) -> str:
*/

/* WHAT WE NEED:
SCENARIO TYPE
TARGET ID
AFFECTED IDS
BASELINE SCORE
COMPROMISED SCORE
*/

/*
WE NEED RUN BUTTON AND SCENARIO COMPARISON
Ideas: for scenario comparison, i was thinking have first scenario take up full page, then i can have a "test another scenario" button that opens
a side by side view with the other scenario, and then a "return to single scenario view" button that goes back to the original view. 
this way we can have a nice clean UI for both single and comparison modes without needing to cram everything into one page

"compare" button next to run button on dashboard, when clicked it opens a modal with a dropdown of other scenarios to compare against, 
once user selects scenario and clicks "compare" it runs the second scenario and then opens the side by side view with both scenarios' results.

For the run and compare buttons i was thinking two green buttons top right but not inside the navbar just above charts and data

kind of like how inside github on an issue you see the edit and new issue buttons in the top right above the content

Make both green? Or maybe run is green and compare is yellow? Not sure on the colors but i think run should be green

Problems: Will we need to re-run the simulator for the second scenario? If so, how do we handle that? 
Do we want to have a loading state while the second scenario is being processed? Do we just put a run different scenario button
next to the run button on dashboard? Would make it a little better looking. 

Need to figure out how to handle the state for the two scenarios and the loading state for when we are running the second scenario.
*/

/* RUN BUTTON CRITERIA: 
Requirements:
[x] "Run Simulation" button added to editor toolbar/navbar (added to body instead)
[-] Modal or panel to select: scenario type (node_compromise, link_degradation, insider_tampering), target component
[-] Target component selectable from dropdown of current architecture components
[-] Sends POST request to /architectures/{id}/simulate with scenario_type and target_component_id
[-] Navigates to dashboard page with simulation results upon success
[-] Error handling for unsaved architectures (prompt to save first)
[-] Loading state during simulation

Technical Notes:
Architecture must be saved before simulating (need architecture ID)
Pass simulation results via URL params, context, or state management
File: frontend/components/NavbarEditor.tsx, new component for simulation modal
*/

/* LIVE RESULTS CRITERIA:
[-] Dashboard receives real simulation results (not hardcoded data)
[-] Bar chart shows baseline vs. compromised mission scores (Recharts)
[-] Table lists all affected components with name, type, criticality
[-] Unaffected components listed separately
[-] Mission score percentage prominently displayed with color coding (green >80%, yellow 50-80%, red <50%)
[-] Attack path narrative/explanation displayed
[-] Criticality ranking table shown
[-] Responsive design

Technical Notes:
Currently dashboard/page.tsx has hardcoded sample data
Replace with data passed from simulation or fetched from API
Use Recharts for charts, Tailwind for styling
File: frontend/app/dashboard/page.tsx
*/

/* SCENARIO COMPARISON CRITERIA:
[-] "Compare Scenarios" view on dashboard
[-] Side-by-side display of two simulation results
[-] Comparison chart showing both scores overlaid
[-] Table highlighting differences in affected components
[-] User can select which two scenarios to compare
[-] Clear labeling of scenario A vs. scenario B

Technical Notes:
Requires scenario storage (see Issue [TASK] Frontend Polish & Accessibility (Inc 2) #48)
Could use a split-panel layout or tabbed comparison
File: frontend/app/dashboard/page.tsx or new comparison page
*/

const baselineData = [
  // USE GET FOR REAL DATA
  { name: 'A', value: 4 },
  { name: 'B', value: 6 },
  { name: 'C', value: 8 },
  { name: 'D', value: 5 },
];

const compromisedData = [
  // USE GET FOR REAL DATA
  { name: 'A', value: 5 },
  { name: 'B', value: 8 },
  { name: 'C', value: 6 },
  { name: 'D', value: 7 },
];

const scoreImpactData = [
  // USE GET FOR REAL DATA
  { time: 0, score: 100 },
  { time: 1, score: 100 },
  { time: 2, score: 95 },
  { time: 3, score: 85 },
  { time: 4, score: 70 },
  { time: 5, score: 50 },
];

export default function Dashboard() {
  // STATE: RUN BUTTON + MODAL + API DATA
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
  const [latestSimulation, setLatestSimulation] = useState<SimulationResult | null>(null);

  // PREVENTS BACKGROUND SCROLL WHEN MODAL IS OPEN
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

  // LOAD ARCHITECTURES AND OPEN MODAL, SAME LOGIC AS LOAD BUTTON FROM NAVBAR
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

      // RESET MODAL INPUT SO OPENS FROM EMPTY
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

  // FETCH COMPONENTS (AFTER ARCHITECTURE SELECTED), SAME AS LOAD BUTTON FROM NAVBAR AGAIN
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

        // AUTO SELECT FIRST COMPONENT
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

  // RUNNING SIMULATION AND HANDLE RESPONSE USING "POST /architectures/{id}/simulate?scenario_type=...&target_component_id=..."
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
          // IF RESPONSE !JSON KEEP FALLBACK
        }
        throw new Error(detail);
      }

      const data: SimulationResult = await response.json();
      setLatestSimulation(data);
      setShowRunModal(false);
    } catch (error) {
      console.error("Error running simulation:", error);
      setRunError(error instanceof Error ? error.message : "Simulation failed. Please try again.");
    } finally {
      setIsRunningSimulation(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ 
        backgroundColor: 'rgba(15, 15, 18, 1)',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
       }}>
      <Navbar />
      
      <div className="container mx-auto px-6 py-6 space-y-6 max-w-7x5">
        {/* RUN AND COMPARE BUTTONS, TOP RIGHT CORNER */}

        <div className="flex items-center justify-end gap-2">
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

        {/* RUN ACTION SUCCEEDED NOTIFICATION, OPTIONAL */}
        {latestSimulation && (
          <div className="rounded-md border border-emerald-500/30 bg-emerald-900/20 p-4 text-sm text-emerald-200">
            <div className="font-semibold">Latest simulation completed</div>
            <div className="mt-1 text-emerald-100/90">
              Architecture #{latestSimulation.architecture_id} • Scenario: {latestSimulation.scenario_type} • Target: {latestSimulation.target_component_id}
            </div>
            <div className="mt-1 text-emerald-100/90">
              Baseline: {latestSimulation.baseline_score.toFixed(1)}% • Compromised: {latestSimulation.compromised_score.toFixed(1)}%
            </div>
          </div>
        )}

        {runError && (
          <div className="rounded-md border border-red-500/40 bg-red-900/20 p-3 text-sm text-red-200">
            {runError}
          </div>
        )}

        {/* TOP ROW - THREE CHARTS MOCKUP */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {/* BASELINE CHART MOCKUP */}
          <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-5 rounded-md">
            <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
              BASELINE
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={baselineData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                <YAxis stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(20,20,24,0.95)', border: '1px solid rgba(255,255,255,0.18)', borderRadius: '4px' }}
                  labelStyle={{ color: 'rgba(255,255,255,0.85)' }}
                />
                <Bar dataKey="value" fill="rgba(255,255,255,0.55)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* COMPROMISED CHART MOCKUP */}
          <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-5 rounded-md">
            <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
              COMPROMISED
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={compromisedData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                <YAxis stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(20,20,24,0.95)', border: '1px solid rgba(255,255,255,0.18)', borderRadius: '4px' }}
                  labelStyle={{ color: 'rgba(255,255,255,0.85)' }}
                />
                <Bar dataKey="value" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* SCORE IMPACT CHART MOCKUP */}
          <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-5 rounded-md">
            <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
              SCORE IMPACT
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={scoreImpactData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                <XAxis dataKey="time" stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} label={{ value: 'Time', position: 'insideBottom', offset: -5, style: { fill: 'rgba(255,255,255,0.55)', fontSize: '10px' } }} />
                <YAxis stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(20,20,24,0.95)', border: '1px solid rgba(255,255,255,0.18)', borderRadius: '4px' }}
                  labelStyle={{ color: 'rgba(255,255,255,0.85)' }}
                />
                <Line type="monotone" dataKey="score" stroke="#fbbf24" strokeWidth={2.5} dot={{ fill: '#fbbf24', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* WHAT HAPPENED SECTION MOCKUP */}
        <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-6 rounded-md">
          <h3 className="text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
            INCIDENT SUMMARY
          </h3>
          <p className="text-sm leading-relaxed text-white/75 font-mono">
            Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example
            Example Example Example Example Example Example Example<br/>
            Example Example Example Example Example Example Example Example Example Example Example Example Example Example<br/>
            Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example
            Example Example Example Example
          </p>
        </div>

        {/* UNAFFECTED VS. AFFECTED COMPONENTS TABLES MOCKUP */}
        <div className="grid grid-cols-2 gap-6">
          {/* LEFT TABLE */}
          <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md border border-white/15 overflow-hidden rounded-md">
            <div className="bg-white/5 px-4 py-2 border-b border-white/10">
              <h4 className="text-xs font-semibold tracking-wider uppercase text-white/65">UNAFFECTED COMPONENTS</h4>
            </div>
            <table className="w-full">
              <thead className="bg-transparent text-white/75">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold tracking-wider uppercase border-b border-white/15">Component</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-white/15">Criticality</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-white/15">Status</th>
                </tr>
              </thead>
              <tbody className="bg-transparent text-white/75 divide-y divide-white/10">
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono">Example</td>
                  <td className="px-4 py-3 text-sm text-center font-mono">9</td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-emerald-900/30 text-emerald-400 border border-emerald-700">SECURE</span>
                  </td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* RIGHT TABLE MOCKUP */}
          <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md border border-white/15 overflow-hidden rounded-md">
            <div className="bg-white/5 px-4 py-2 border-b border-white/10">
              <h4 className="text-xs font-semibold tracking-wider uppercase text-white/65">COMPROMISED COMPONENTS</h4>
            </div>
            <table className="w-full">
              <thead className="bg-transparent text-white/75">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold tracking-wider uppercase border-b border-white/15">Component</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-white/15">Criticality</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-white/15">Status</th>
                </tr>
              </thead>
              <tbody className="bg-transparent text-white/75 divide-y divide-white/10">
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono">Example X</td>
                  <td className="px-4 py-3 text-sm text-center font-mono">3</td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-red-900/30 text-red-400 border border-red-700">BREACH</span>
                  </td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-white/35">—</td>
                  <td className="px-4 py-3 text-sm text-center text-white/35">—</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* RUN SIMULATION MODAL */}
      {showRunModal && (
        <div
          style={{
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
          }}
        >
          <div
            style={{
              backgroundColor: "#1a1a1a",
              padding: "30px",
              borderRadius: "8px",
              minWidth: "460px",
              color: "white",
              border: "1px solid rgba(255,255,255,0.12)",
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: "18px" }}>Run Simulation</h2>

            {/* SAVED ARCHITECTURE SELECTOR */}
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

            {/* SCENARIO SELECTOR */}
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

            {/* TARGET COMPONENT SELECTOR */}
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
                  {component.name} ({component.component_type}) • Criticality {component.criticality}
                </option>
              ))}
            </select>

            {/* LOCAL INLINE ERROR FOR WHEN INSIDE MODAL */}
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
    </div>
  );
}