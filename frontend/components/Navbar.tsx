"use client";

import React from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';

const inter = Inter({ weight: "500", subsets: ['latin'] });

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar() {
  return (
    <nav 
    className={inter.className}
    style={{
      width: "100%",
      height: "80px",
      backgroundColor: "#080808",
      color: "white",
      display: "flex",
      alignItems: "center",
      padding: "0 20px",
      boxSizing: "border-box",
      justifyContent: "center",
    }}>
      <Image 
        src="/MissionSystemsArchitecture.png" 
        alt="Logo" 
        width={500}
        height={500}
        style={{ marginRight: "10px"}}
      />
    </nav>
  );
}
