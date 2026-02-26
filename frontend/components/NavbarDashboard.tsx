"use client";

import React, { useState } from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';
import Link from "next/dist/client/link";

const inter = Inter({ weight: "500", subsets: ['latin'] });

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar() {
  return (
    <>
      <nav 
      className={inter.className}
      style={{
        width: "100%",
        height: "60px",
        backgroundColor: "#0A0A0A",
        color: "white",
        display: "flex",
        alignItems: "center",
        padding: "10px 10px",
        boxSizing: "border-box",
        justifyContent: "space-between",
      }}>
        <Image 
          src="/masSmall.png" 
          alt="Logo" 
          width={200}
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
              id="home-button"
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
              <Image 
                src="/homeIcon.png" 
                alt="Home Icon" 
                width={24} 
                height={16}
              />
              <Link href="/" style={{margin: "0", fontSize: "14px"}}>Home</Link>
            </button>
          </li>
        </ul>
      </nav>
    </>
  );
}