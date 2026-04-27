"use client";

import React, { useEffect, useMemo, useState } from "react";
import Navbar, { CompareSimulationResult, SimulationResult } from "@/components/NavbarDashboard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

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

type ArchitectureComponent = {
  id: number;
  component_id: string;
  name: string;
  component_type: string;
  criticality: number;
};

type ArchitectureDetail = {
  id: number;
  name: string;
  components: ArchitectureComponent[];
};

const placeholderSeries = [{ name: "N/A", value: 0 }];

const scenarioLabel: Record<string, string> = {
  node_compromise: "Node Compromise",
  link_degradation: "Link Degradation",
  insider_tampering: "Insider Tampering",
};

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

const getScoreColorClasses = (score: number) => {
  if (score > 80) {
    return "border-emerald-500/40 bg-emerald-900/20 text-emerald-200";
  }
  if (score >= 50) {
    return "border-yellow-500/40 bg-yellow-900/20 text-yellow-200";
  }
  return "border-red-500/40 bg-red-900/20 text-red-200";
};

type SimulationPanelProps = {
  title: string;
  result: SimulationResult | null;
  architectureComponents: ArchitectureComponent[];
  isLoadingArchitecture: boolean;
  architectureLoadError: string | null;
  emptyMessage: string;
};

function SimulationPanel({
  title,
  result,
  architectureComponents,
  isLoadingArchitecture,
  architectureLoadError,
  emptyMessage,
}: SimulationPanelProps) {
  const baselineChartData = result
    ? [{ name: "Mission", value: Number(result.baseline_score.toFixed(1)) }]
    : placeholderSeries;

  const compromisedChartData = result
    ? [{ name: "Mission", value: Number(result.compromised_score.toFixed(1)) }]
    : placeholderSeries;

  const scoreImpactData = result
    ? [
        {
          name: "Mission",
          baseline: Number(result.baseline_score.toFixed(1)),
          compromised: Number(result.compromised_score.toFixed(1)),
        },
      ]
    : [{ name: "Mission", baseline: 0, compromised: 0 }];

  const affectedComponentIdSet = useMemo(
    () => new Set(result?.affected_components ?? []),
    [result]
  );

  const affectedRows = useMemo(
    () => architectureComponents.filter((component) => affectedComponentIdSet.has(component.component_id)),
    [architectureComponents, affectedComponentIdSet]
  );

  const unaffectedRows = useMemo(
    () => architectureComponents.filter((component) => !affectedComponentIdSet.has(component.component_id)),
    [architectureComponents, affectedComponentIdSet]
  );

  const simulatedScenarioLabel = result
    ? (scenarioLabel[result.scenario_type] ?? result.scenario_type)
    : emptyMessage;

  return (
    <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-6 rounded-md space-y-6">
      <div className="flex items-center justify-between border-b border-white/15 pb-2">
        <h3 className="text-xs font-semibold tracking-wider uppercase text-white/65">{title}</h3>
        {result && (
          <span className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-white/70">
            {simulatedScenarioLabel}
          </span>
        )}
      </div>

      {result ? (
        <>
          <div className={`rounded-md border p-4 text-sm ${getScoreColorClasses(result.compromised_score)}`}>
            <div className="font-semibold">Mission Score After Incident</div>
            <div className="mt-1 text-xl font-bold">
              {result.compromised_score.toFixed(1)}%
            </div>
            <div className="mt-1 opacity-90">
              Delta: {result.score_delta >= 0 ? "+" : ""}{result.score_delta.toFixed(1)}%
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-5 rounded-md">
              <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
                BASELINE
              </h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={baselineChartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }} barCategoryGap="55%">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                  <YAxis stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(20,20,24,0.95)', border: '1px solid rgba(255,255,255,0.18)', borderRadius: '4px' }}
                    labelStyle={{ color: 'rgba(255,255,255,0.85)' }}
                  />
                  <Bar dataKey="value" fill="rgba(255,255,255,0.55)" barSize={14} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-5 rounded-md">
              <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
                COMPROMISED
              </h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={compromisedChartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }} barCategoryGap="55%">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                  <YAxis stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(20,20,24,0.95)', border: '1px solid rgba(255,255,255,0.18)', borderRadius: '4px' }}
                    labelStyle={{ color: 'rgba(255,255,255,0.85)' }}
                  />
                  <Bar dataKey="value" fill="#ef4444" barSize={14} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-5 rounded-md">
              <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
                SCORE IMPACT
              </h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={scoreImpactData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }} barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} />
                  <YAxis stroke="rgba(255,255,255,0.55)" style={{ fontSize: '11px' }} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(20,20,24,0.95)', border: '1px solid rgba(255,255,255,0.18)', borderRadius: '4px' }}
                    labelStyle={{ color: 'rgba(255,255,255,0.85)' }}
                  />
                  <Bar dataKey="baseline" fill="rgba(255,255,255,0.55)" barSize={12} />
                  <Bar dataKey="compromised" fill="#fbbf24" barSize={12} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-[rgba(15,15,20,0.85)] backdrop-blur-md text-white/90 border border-white/15 p-6 rounded-md">
            <h3 className="text-xs font-semibold tracking-wider uppercase mb-4 text-white/65 border-b border-white/15 pb-2">
              INCIDENT SUMMARY
            </h3>
            <p className="text-sm leading-relaxed text-white/75 font-mono">
              {result.explanation}
            </p>
            {result.attack_path.length > 0 && (
              <p className="mt-3 text-xs leading-relaxed text-white/60 font-mono">
                Attack path: {result.attack_path.join(" -> ")}
              </p>
            )}
          </div>

          {architectureLoadError && (
            <div className="rounded-md border border-red-500/40 bg-red-900/20 p-3 text-sm text-red-200">
              {architectureLoadError}
            </div>
          )}

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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
                  {isLoadingArchitecture && (
                    <tr>
                      <td colSpan={3} className="px-4 py-4 text-sm text-white/60">Loading components...</td>
                    </tr>
                  )}
                  {!isLoadingArchitecture && unaffectedRows.map((component) => (
                    <tr key={component.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-4 py-3 text-sm font-mono">{component.name}</td>
                      <td className="px-4 py-3 text-sm text-center font-mono">{component.criticality}</td>
                      <td className="px-4 py-3 text-sm text-center">
                        <span className="px-2 py-1 text-xs font-semibold rounded bg-emerald-900/30 text-emerald-400 border border-emerald-700">SECURE</span>
                      </td>
                    </tr>
                  ))}
                  {!isLoadingArchitecture && result && unaffectedRows.length === 0 && (
                    <tr>
                      <td colSpan={3} className="px-4 py-4 text-sm text-white/45">No unaffected components in this scenario.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

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
                  {isLoadingArchitecture && (
                    <tr>
                      <td colSpan={3} className="px-4 py-4 text-sm text-white/60">Loading components...</td>
                    </tr>
                  )}
                  {!isLoadingArchitecture && affectedRows.map((component) => (
                    <tr key={component.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-4 py-3 text-sm font-mono">{component.name}</td>
                      <td className="px-4 py-3 text-sm text-center font-mono">{component.criticality}</td>
                      <td className="px-4 py-3 text-sm text-center">
                        <span className="px-2 py-1 text-xs font-semibold rounded bg-red-900/30 text-red-400 border border-red-700">BREACH</span>
                      </td>
                    </tr>
                  ))}
                  {!isLoadingArchitecture && result && affectedRows.length === 0 && (
                    <tr>
                      <td colSpan={3} className="px-4 py-4 text-sm text-white/45">No compromised components reported for this scenario.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <p className="text-sm leading-relaxed text-white/55 font-mono">
          {emptyMessage}
        </p>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [latestSimulation, setLatestSimulation] = useState<SimulationResult | null>(null);
  const [comparisonSimulation, setComparisonSimulation] = useState<CompareSimulationResult | null>(null);
  const [architectureComponents, setArchitectureComponents] = useState<ArchitectureComponent[]>([]);
  const [isLoadingArchitecture, setIsLoadingArchitecture] = useState(false);
  const [architectureLoadError, setArchitectureLoadError] = useState<string | null>(null);

  const activeArchitectureId = comparisonSimulation?.architecture_id ?? latestSimulation?.architecture_id ?? null;
  const activeScenarioLabel = latestSimulation
    ? (scenarioLabel[latestSimulation.scenario_type] ?? latestSimulation.scenario_type)
    : "No simulation yet";

  useEffect(() => {
    const loadArchitecture = async () => {
      if (!activeArchitectureId) {
        setArchitectureComponents([]);
        setArchitectureLoadError(null);
        return;
      }

      setIsLoadingArchitecture(true);
      setArchitectureLoadError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/architectures/${activeArchitectureId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch architecture details for component breakdown.");
        }

        const architecture: ArchitectureDetail = await response.json();
        setArchitectureComponents(architecture.components);
      } catch (error) {
        console.error("Error loading architecture details on dashboard:", error);
        setArchitectureLoadError("Unable to load full component details for affected/unaffected tables.");
        setArchitectureComponents([]);
      } finally {
        setIsLoadingArchitecture(false);
      }
    };

    loadArchitecture();
  }, [activeArchitectureId]);

  return (
    <div className="min-h-screen" style={{
      backgroundColor: 'rgba(15, 15, 18, 1)',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      backgroundSize: 'cover',
    }}>
      <Navbar
        onSimulationCompleted={(result) => {
          setLatestSimulation(result);
          setComparisonSimulation(null);
        }}
        onCompareCompleted={(result) => {
          setComparisonSimulation(result);
          setLatestSimulation(null);
        }}
      />

      <div className="container mx-auto px-6 py-6 space-y-6 max-w-7x5">
        {comparisonSimulation ? (
          <div className="rounded-md border border-cyan-500/30 bg-cyan-900/20 p-4 text-sm text-cyan-100">
            <div className="font-semibold">Comparison ready</div>
            <div className="mt-1 text-cyan-50/90">
              Architecture #{comparisonSimulation.architecture_id} • {scenarioLabel[comparisonSimulation.left.scenario_type] ?? comparisonSimulation.left.scenario_type} vs {scenarioLabel[comparisonSimulation.right.scenario_type] ?? comparisonSimulation.right.scenario_type}
            </div>
            <div className="mt-1 text-cyan-50/90">
              Targets: {comparisonSimulation.left.target_component_id} vs {comparisonSimulation.right.target_component_id}
            </div>
          </div>
        ) : latestSimulation ? (
          <>
            <div className="rounded-md border border-emerald-500/30 bg-emerald-900/20 p-4 text-sm text-emerald-200">
              <div className="font-semibold">Latest simulation completed</div>
              <div className="mt-1 text-emerald-100/90">
                Architecture #{latestSimulation.architecture_id} • Scenario: {activeScenarioLabel} • Target: {latestSimulation.target_component_id}
              </div>
            </div>
          </>
        ) : (
          <div className="rounded-md border border-white/20 bg-white/5 p-4 text-sm text-white/75">
            Run a simulation from the top-right navbar to populate live mission-impact charts and component tables.
          </div>
        )}

        {architectureLoadError && !comparisonSimulation && !latestSimulation && (
          <div className="rounded-md border border-red-500/40 bg-red-900/20 p-3 text-sm text-red-200">
            {architectureLoadError}
          </div>
        )}

        {comparisonSimulation ? (
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <SimulationPanel
              title="Scenario A"
              result={comparisonSimulation.left}
              architectureComponents={architectureComponents}
              isLoadingArchitecture={isLoadingArchitecture}
              architectureLoadError={architectureLoadError}
              emptyMessage="No comparison result available."
            />
            <SimulationPanel
              title="Scenario B"
              result={comparisonSimulation.right}
              architectureComponents={architectureComponents}
              isLoadingArchitecture={isLoadingArchitecture}
              architectureLoadError={architectureLoadError}
              emptyMessage="No comparison result available."
            />
          </div>
        ) : (
          <SimulationPanel
            title="Incident Overview"
            result={latestSimulation}
            architectureComponents={architectureComponents}
            isLoadingArchitecture={isLoadingArchitecture}
            architectureLoadError={architectureLoadError}
            emptyMessage="No simulation narrative available yet. Run one scenario from the navbar to generate mission impact explanation."
          />
        )}
      </div>
    </div>
  );
}
