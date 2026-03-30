"use client";

import React, {useState, useEffect} from "react";
import Navbar from "@/components/NavbarDashboard";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

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
[-] "Run Simulation" button added to editor toolbar/navbar
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
  return (
    <div className="min-h-screen" style={{ 
        backgroundImage: 'url(/BluePurp.jpeg)',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
       }}>
      <Navbar />
      
      <div className="container mx-auto px-6 py-6 space-y-6 max-w-7x5">
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
    </div>
  );
}