"use client";

import React, { useState } from "react";
import Navbar from "@/components/NavbarDashboard";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Sample data for charts
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
        backgroundImage: 'url(/IrBG.jpeg)',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
       }}>
      <Navbar />
      
      <div className="container mx-auto px-6 py-6 space-y-6 max-w-7x5">
        {/* Top Row - Three Charts */}
        <div className="grid grid-cols-3 gap-8">
          {/* Baseline Chart */}
          <div className="bg-custom-block text-slate-100 border border-white shadow-xl p-5 rounded-xl">
            <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-slate-400 border-b border-slate-700 pb-2">
              BASELINE
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={baselineData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '11px' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '11px' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '4px' }}
                  labelStyle={{ color: '#cbd5e1' }}
                />
                <Bar dataKey="value" fill="#94a3b8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Compromised Chart */}
          <div className="bg-custom-block text-slate-100 border border-white shadow-xl p-5 rounded-xl">
            <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-slate-400 border-b border-slate-700 pb-2">
              COMPROMISED
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={compromisedData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '11px' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '11px' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '4px' }}
                  labelStyle={{ color: '#cbd5e1' }}
                />
                <Bar dataKey="value" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Score Impact Chart */}
          <div className="bg-custom-block text-slate-100 border border-white shadow-xl p-5 rounded-xl">
            <h3 className="text-center text-xs font-semibold tracking-wider uppercase mb-4 text-slate-400 border-b border-slate-700 pb-2">
              SCORE IMPACT
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={scoreImpactData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#64748b" style={{ fontSize: '11px' }} label={{ value: 'Time', position: 'insideBottom', offset: -5, style: { fill: '#64748b', fontSize: '10px' } }} />
                <YAxis stroke="#64748b" style={{ fontSize: '11px' }} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '4px' }}
                  labelStyle={{ color: '#cbd5e1' }}
                />
                <Line type="monotone" dataKey="score" stroke="#fbbf24" strokeWidth={2.5} dot={{ fill: '#fbbf24', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* What Happened Section */}
        <div className="bg-custom-block text-slate-100 border border-white shadow-xl p-6 rounded-xl">
          <h3 className="text-xs font-semibold tracking-wider uppercase mb-4 text-slate-400 border-b border-slate-700 pb-2">
            INCIDENT SUMMARY
          </h3>
          <p className="text-sm leading-relaxed text-slate-300 font-mono">
            Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example
            Example Example Example Example Example Example Example<br/>
            Example Example Example Example Example Example Example Example Example Example Example Example Example Example<br/>
            Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example Example
            Example Example Example Example
          </p>
        </div>

        {/* Bottom Tables */}
        <div className="grid grid-cols-2 gap-6">
          {/* Left Table */}
          <div className="bg-custom-block border border-white shadow-xl overflow-hidden rounded-xl">
            <div className="bg-slate-800 px-4 py-2 border-b border-white">
              <h4 className="text-xs font-semibold tracking-wider uppercase text-slate-400">UNAFFECTED COMPONENTS</h4>
            </div>
            <table className="w-full">
              <thead className="bg-custom-block text-slate-300">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold tracking-wider uppercase border-b border-slate-700">Component</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-slate-700">Criticality</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-slate-700">Status</th>
                </tr>
              </thead>
              <tbody className="bg-custom-block text-slate-300 divide-y divide-slate-800">
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono">Example</td>
                  <td className="px-4 py-3 text-sm text-center font-mono">9</td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-emerald-900/30 text-emerald-400 border border-emerald-700">SECURE</span>
                  </td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Right Table */}
          <div className="bg-custom-block border border-white shadow-xl overflow-hidden rounded-xl">
            <div className="bg-slate-800 px-4 py-2 border-b border-white">
              <h4 className="text-xs font-semibold tracking-wider uppercase text-white">COMPROMISED COMPONENTS</h4>
            </div>
            <table className="w-full">
              <thead className="bg-custom-block text-slate-300">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold tracking-wider uppercase border-b border-slate-700">Component</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-slate-700">Criticality</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold tracking-wider uppercase border-b border-slate-700">Status</th>
                </tr>
              </thead>
              <tbody className="bg-custom-block text-slate-300 divide-y divide-slate-800">
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono">Example X</td>
                  <td className="px-4 py-3 text-sm text-center font-mono">3</td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-red-900/30 text-red-400 border border-red-700">BREACH</span>
                  </td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center font-mono text-slate-600">—</td>
                  <td className="px-4 py-3 text-sm text-center text-slate-600">—</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}