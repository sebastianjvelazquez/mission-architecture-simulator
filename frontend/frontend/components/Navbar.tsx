"use client";

import React from "react";

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar() {
  return (
    <nav style={{
      width: "100%",
      height: "60px",
      backgroundColor: "#0a0a0a",
      color: "white",
      display: "flex",
      alignItems: "center",
      padding: "0 20px",
      boxSizing: "border-box",
      fontWeight: "normal"
    }}>
      Mission Architecture Simulator
    </nav>
  );
}
