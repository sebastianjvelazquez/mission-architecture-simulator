"use client";

import React, { useState } from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';
import Link from "next/dist/client/link";

const inter = Inter({ weight: "500", subsets: ['latin'] });

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar() {
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [modelName, setModelName] = useState("");

  const handleSave = () => {
    // TODO: ADD LOGIC FOR SAVING THE MODEL TO DB
    console.log("Saving model:", modelName);
    setShowSaveModal(false);
    setModelName("");
  };

  const handleLoad = () => {
    // TODO: ADD LOGIC FOR LOADING THE MODEL FROM DB
    // LOAD MODEL FROM DB BASED ON ID IN DATABASE
    console.log("Loading model:", modelName);
    setShowLoadModal(false);
    setModelName("");
  };

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
              id="dashboard-button"
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
                src="/dashboardIcon.png" 
                alt="Dashboard Icon" 
                width={24} 
                height={16}
              />
              <Link href="/dashboard" style={{margin: "0", fontSize: "14px"}}>Dashboard</Link>
            </button>
          </li>
          <li>
            <button 
              id="load-button"
              onClick={() => setShowLoadModal(true)}
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
                src="/loadIcon.png" 
                alt="Load Icon" 
                width={19} 
                height={16}
              />
              <h3 style={{margin: "0", fontSize: "14px"}}>Load</h3>
            </button>
          </li>

          <li>
            <button 
              id="save-button"
              onClick={() => setShowSaveModal(true)}
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

      {/* Save Modal */}
      {showSaveModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: "#1a1a1a",
            padding: "30px",
            borderRadius: "8px",
            minWidth: "400px",
            color: "white",
          }}>
            <h2 style={{ marginTop: 0, marginBottom: "20px" }}>Save Model</h2>
            <input
              type="text"
              placeholder="Enter model name"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                marginBottom: "20px",
                borderRadius: "4px",
                border: "1px solid #333",
                backgroundColor: "#0a0a0a",
                color: "white",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
            <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
              <button
                onClick={() => {
                  setShowSaveModal(false);
                  setModelName("");
                }}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#333",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={!modelName.trim()}
                style={{
                  padding: "10px 20px",
                  backgroundColor: modelName.trim() ? "#0070f3" : "#555",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: modelName.trim() ? "pointer" : "not-allowed",
                }}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Modal */}
      {showLoadModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: "#1a1a1a",
            padding: "30px",
            borderRadius: "8px",
            minWidth: "400px",
            color: "white",
          }}>
            <h2 style={{ marginTop: 0, marginBottom: "20px" }}>Load Model</h2>
            <input
              type="text"
              placeholder="Enter model ID:"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                marginBottom: "20px",
                borderRadius: "4px",
                border: "1px solid #333",
                backgroundColor: "#0a0a0a",
                color: "white",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
            <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
              <button
                onClick={() => {
                  setShowLoadModal(false);
                  setModelName("");
                }}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#333",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleLoad}
                disabled={!modelName.trim()}
                style={{
                  padding: "10px 20px",
                  backgroundColor: modelName.trim() ? "#0070f3" : "#555",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: modelName.trim() ? "pointer" : "not-allowed",
                }}
              >
                Load
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}