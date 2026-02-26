"use client";

import React, { useCallback, useRef, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  ReactFlowInstance
} from "reactflow";
import "reactflow/dist/style.css";
import Navbar from "@/components/NavbarDashboard";
import { nodeServerAppPaths } from "next/dist/build/webpack/plugins/pages-manifest-plugin";
import { on } from "events";
import { Line, LineChart } from 'recharts';


export default function Dashboard() {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
    return (
    <div>
        <Navbar />
        {/* DASHBOARD HERE, USE RECHARTS */}
        <div>Dashboard content</div>
    </div>
  );
}