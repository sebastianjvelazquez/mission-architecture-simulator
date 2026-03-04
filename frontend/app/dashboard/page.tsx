"use client";

import React from "react";
import Navbar from "@/components/NavbarDashboard";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// SAMPLE DATA, REPLACE WITH REAL DATA FROM DB WHEN INTEGRATED
const baselineData = [
  { name: 'A', value: 4 },
  { name: 'B', value: 6 },
  { name: 'C', value: 8 },
  { name: 'D', value: 5 },
];

const compromisedData = [
  { name: 'A', value: 5 },
  { name: 'B', value: 8 },
  { name: 'C', value: 6 },
  { name: 'D', value: 7 },
];

const scoreImpactData = [
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