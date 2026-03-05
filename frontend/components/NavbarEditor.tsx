"use client";

import React, { useState } from "react";
import Image from "next/image";
import {Inter } from 'next/font/google';
import Link from "next/dist/client/link";
import handleDeleteAll from "@/app/page";

const inter = Inter({ weight: "500", subsets: ['latin'] });

{/* NAVBAR CODE FOR USE INSIDE PAGE.TSX */}
export default function Navbar() {
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [modelName, setModelName] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = () => {
    // TODO: ADD LOGIC FOR SAVING THE MODEL TO DB
    // SAVE MODEL WITH NAME, ASSOCIATE NAME WITH ID IN DB
    /*
    Save button sends POST request to /architectures

    Components include: component_id, name, type, criticality, position

    Flows include: source_component_id, target_component_id, data_type, cia_requirement

    Success toast/notification displayed after save

    Error messages shown if save fails

    Architecture ID stored in state after save

    Loading spinner shown during save operation
    */
    console.log("Saving model:", modelName);
    setShowSaveModal(false);
    setModelName("");
  };

  const handleLoad = () => {
    // TODO: ADD LOGIC FOR LOADING THE MODEL FROM DB
    // LOAD MODEL FROM DB BASED ON ID IN DATABASE
    /*
    1 [ ] Load button fetches list of architectures from GET /architectures
    2 [ ] User can select an architecture from the list
    3 [ ] Selected architecture loads components and flows onto canvas
    4 [x] Canvas cleared before loading new architecture
    5 [ ] Architecture metadata displayed in UI
    6 [ ] Error handling for failed loads or empty list
    7 [ ] Loading spinner during fetch
    */
    /*
    STRUCTURE:
    1. DISPLAY LIST OF ARCHITECTURES IN MODAL (ID + NAME)
    2. USER SELECTS ARCHITECTURE TO LOAD
    3. FETCH COMPONENTS AND FLOWS FOR SELECTED ARCHITECTURE
    4. CLEAR CURRENT CANVAS
    5. DISPLAY LOADING SPINNER
    6. RENDER COMPONENTS AND FLOWS ON CANVAS
    7. DISPLAY SUCCESS OR FAILURE MESSAGE
    */
    // TODO: SET LOADING TO TRUE WHEN FETCHING STARTS → setIsLoading(true);

    // Display/Select Start
    /*
    for x in db, display name and id in modal as options
    user clicks on one option → that is the architecture we load (store selected architecture id in state)
    */
    // Display/Select End

    // Display Loading Spinner Start
    setIsLoading(true);
    // Display Loading Spinner End

    // Fetch Components Start
    /* 
    fetch all data from architecture (nodes, edges, id, label, criticality, cia requirements, etc...)
    store all data in setEdgesNew and setNodesNew as temp array so if other failure the current architecture doesn't delete
    if works keep going, else display error message
    */
    // Fetch Components End

    // Clear Canvas Start
    /*
    clear components, start of real loading actions
    if works keep going, else display error message
    */
    handleDeleteAll();
    // Clear Canvas End

    // Render Components and Flows Start
    /*
    assign setEdges and setNodes to the new versions of each, ports all data to current structure
    if works keep going, else display error message
    */
    // Render Components and Flows End

    // Display Success/Failure Message Start
    setIsLoading(false); // not loading anymore
    // TODO: DISPLAY SUCCESS MESSAGE IF FETCH AND RENDERING SUCCEEDS, FAILURE MESSAGE IF ANY STEP FAILS
    // Display Success/Failure Message End

    setShowLoadModal(false);
    setModelName("");
  };

  React.useEffect(() => {
    if (showSaveModal || showLoadModal) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [showSaveModal, showLoadModal]);

  return (
    <>
    <div className="container mx-auto px-6 py-6 space-y-6 max-w-7x5">
      <nav 
      className={inter.className}
      style={{
        width: "100%",
        height: "0px",
        backgroundColor: "transparent",
        color: "white",
        display: "flex",
        alignItems: "center",
        padding: "10px 10px",
        boxSizing: "border-box",
        position: "relative",
        justifyContent: "center",
      }}>
        <Image 
          src="/TextNewLogo.svg"
          alt="Logo" 
          width={365}
          height={50}
          style={{position: "absolute", marginTop: "28px", objectFit: "contain", left: "0px" }}
        />
        
        <div style={{
          // NAVBAR ELIPSE SHAPE
          //backgroundColor: "rgba(15, 15, 20, 0.85)",
          //borderRadius: "25px",
          padding: "5px 15px",
          //border: "1px solid #333",
          marginTop: "20px",
        }}>
          <ul style={{
            display: "flex",
            listStyle: "none",
            margin: 0,
            padding: 0,
            gap: "0px",
          }}>
            <li>
              <button 
                // TODO: ADD disabled={isLoading} HERE TO DISABLE BUTTON WHILE LOADING
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
                <h3 style={{margin: "0", fontSize: "16px"}}>Load</h3>
                {/* TODO: ADD LOADING SPINNER HERE INSIDE CONDITIONAL: {isLoading && <YourSpinnerComponent />} */}
                <h3 style={{margin: "0", fontSize: "16px"}}>Load</h3>
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
                <h3 style={{margin: "0", fontSize: "16px"}}>Save</h3>
              </button>
            </li>
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
                <Link href="/dashboard" style={{margin: "0", fontSize: "16px"}}>Dashboard</Link>
              </button>
            </li>
          </ul>
        </div>
      </nav>
    </div>

    {/* SAVE MODAL DESIGN CODE */}
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

    {/* LOAD MODAL DESIGN CODE */}
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