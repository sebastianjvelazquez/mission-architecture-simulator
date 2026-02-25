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
      height: "60px",
      backgroundColor: "#080808",
      color: "white",
      display: "flex",
      alignItems: "center",
      padding: "10px 10px",
      boxSizing: "border-box",
      justifyContent: "space-between",
    }}>
      <Image 
        src="/MasLogo.png" 
        alt="Logo" 
        width={300}
        height={50}
        style={{marginTop: "0px", objectFit: "contain" }}
      />
      
      <ul style={{
        display: "flex",
        listStyle: "none",
        margin: 0,
        padding: 0,
        gap: "10px",
      }}>
        <li>
          <button 
          
            id="load-button"
            style={{
              padding: "10px 16px",
              backgroundColor: "#1A1A1A",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px", 
            }}
          >
            <Image 
              src="/loadIcon.png" 
              alt="Load Icon" 
              width={16} 
              height={16}
            />
            <h3 style={{margin: "0", fontSize: "14px"}}>Load</h3>
          </button>
        </li>

        <li>
          <button 
            
            id="save-button"
            style={{
              padding: "10px 16px",
              backgroundColor: "#1A1A1A",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <Image 
              src="/SaveIcon.png" 
              alt="Save Icon" 
              width={16} 
              height={16}
            />
            <h3 style={{margin: "0", fontSize: "14px"}}>Save</h3>
          </button>
        </li>
      </ul>
    </nav>
  );
}