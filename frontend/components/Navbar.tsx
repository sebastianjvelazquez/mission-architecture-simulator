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
      height: "50px",
      backgroundColor: "#080808",
      color: "white",
      display: "flex",
      alignItems: "center",
      padding: "0px",
      boxSizing: "border-box",
      justifyContent: "left",
    }}>
      <Image 
        src="/LogoMASBlue.png" 
        alt="Logo" 
        width={150}
        height={150}
        style={{marginTop : "10px" }}
      />
      <button 
        onClick={onSave}
        style={{
          padding: "8px 16px",
          backgroundColor: "#1A1A1A",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Save Architecture
      </button>
    </nav>
  );
}