-- ============================================================================
-- MISSION SYSTEM SECURITY ARCHITECTURE SIMULATOR - DATABASE SCHEMA
-- ============================================================================
-- Version: 1.0.0 (Increment 1)
-- PostgreSQL 15+
-- Purpose: Store mission architectures, components, and flows for simulation
-- ============================================================================

-- ============================================================================
-- ⚠️  WARNING: DROP TABLES (Development Only)
-- ============================================================================
-- These DROP statements are useful for local development to reset the schema.
-- For production deployment, these will NOT be used (we'll use Alembic migrations).
-- If you're running this manually on production, COMMENT OUT the lines below!
-- ============================================================================

DROP TABLE IF EXISTS simulation_results CASCADE;
DROP TABLE IF EXISTS scenarios CASCADE;
DROP TABLE IF EXISTS mitigations CASCADE;
DROP TABLE IF EXISTS flows CASCADE;
DROP TABLE IF EXISTS components CASCADE;
DROP TABLE IF EXISTS architectures CASCADE;

-- ============================================================================
-- TABLE: architectures
-- ============================================================================
-- Description: Top-level mission systems created by users
-- Example: "UAV Surveillance System", "Naval Command Network"
-- ============================================================================

CREATE TABLE architectures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_clone BOOLEAN NOT NULL DEFAULT FALSE,
    parent_id INTEGER REFERENCES architectures(id) ON DELETE SET NULL,

    -- Flexible properties (JSONB for future extensibility)
    properties JSONB DEFAULT '{}'::jsonb,

    -- Future: Add user_id when authentication is implemented
    -- user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT name_not_empty CHECK (char_length(name) > 0)
);

-- Indexes for architectures
CREATE INDEX idx_architectures_created_at ON architectures(created_at DESC);
CREATE INDEX idx_architectures_parent_id ON architectures(parent_id);
-- CREATE INDEX idx_architectures_user_id ON architectures(user_id); -- Uncomment when users added


-- ============================================================================
-- TABLE: components
-- ============================================================================
-- Description: Nodes in an architecture graph (sensors, compute, control, etc.)
-- Properties stored as JSONB for flexibility (CIA requirements, criticality)
-- ============================================================================

CREATE TABLE components (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER NOT NULL REFERENCES architectures(id) ON DELETE CASCADE,

    -- User-defined string identifier (e.g. "s1", "ctrl1")
    component_id VARCHAR(255),

    -- Core attributes
    name VARCHAR(255) NOT NULL,
    component_type VARCHAR(50) NOT NULL, -- sensor, compute, communication, control, etc.
    criticality INTEGER NOT NULL DEFAULT 5,

    -- Flexible properties (JSONB for schema-less attributes)
    -- Example: {"confidentiality": 5, "integrity": 4, "availability": 5}
    properties JSONB DEFAULT '{}'::jsonb,
    
    -- UI/Diagram editor position
    position_x FLOAT,
    position_y FLOAT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT name_not_empty CHECK (char_length(name) > 0),
    CONSTRAINT valid_component_type CHECK (char_length(component_type) > 0)
);

-- Indexes for components
CREATE INDEX idx_components_architecture_id ON components(architecture_id);
CREATE INDEX idx_components_type ON components(component_type);
CREATE INDEX idx_components_created_at ON components(created_at DESC);

-- GIN index for JSONB property queries (e.g., WHERE properties @> '{"criticality": "HIGH"}')
CREATE INDEX idx_components_properties ON components USING GIN (properties);


-- ============================================================================
-- TABLE: flows
-- ============================================================================
-- Description: Directed edges between components (data flows, control signals)
-- Represents dependencies in the mission system graph
-- ============================================================================

CREATE TABLE flows (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER NOT NULL REFERENCES architectures(id) ON DELETE CASCADE,
    
    -- Graph edge: source → target
    source_component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    target_component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    
    -- Flow attributes
    flow_type VARCHAR(50) DEFAULT 'data', -- data, control, power, etc.
    data_type VARCHAR(100),
    cia_requirement VARCHAR(50),
    latency_sensitivity VARCHAR(20),
    
    -- Flexible properties (JSONB for bandwidth, latency, protocol, etc.)
    -- Example: {"bandwidth_mbps": 100, "latency_ms": 5, "protocol": "TCP"}
    properties JSONB DEFAULT '{}'::jsonb,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT no_self_loops CHECK (source_component_id != target_component_id),
    CONSTRAINT valid_flow_type CHECK (char_length(flow_type) > 0)
);

-- Indexes for flows
CREATE INDEX idx_flows_architecture_id ON flows(architecture_id);
CREATE INDEX idx_flows_source_component_id ON flows(source_component_id);
CREATE INDEX idx_flows_target_component_id ON flows(target_component_id);
CREATE INDEX idx_flows_type ON flows(flow_type);

-- Composite index for graph traversal queries
CREATE INDEX idx_flows_source_target ON flows(source_component_id, target_component_id);

-- GIN index for JSONB property queries
CREATE INDEX idx_flows_properties ON flows USING GIN (properties);


-- ============================================================================
-- TABLE: mitigations
-- ============================================================================
-- Description: Persisted mitigation suggestions linked to an architecture.
-- ============================================================================

CREATE TABLE mitigations (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER NOT NULL REFERENCES architectures(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    affected_component_id INTEGER REFERENCES components(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for mitigations
CREATE INDEX idx_mitigations_architecture_id ON mitigations(architecture_id);
CREATE INDEX idx_mitigations_type ON mitigations(type);
CREATE INDEX idx_mitigations_affected_component_id ON mitigations(affected_component_id);


-- ============================================================================
-- TABLE: scenarios
-- ============================================================================
-- Description: Saved attack scenarios for replay/comparison.
-- ============================================================================

CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER NOT NULL REFERENCES architectures(id) ON DELETE CASCADE,
    scenario_type VARCHAR(100) NOT NULL,
    target_component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    parameters JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for scenarios
CREATE INDEX idx_scenarios_architecture_id ON scenarios(architecture_id);
CREATE INDEX idx_scenarios_scenario_type ON scenarios(scenario_type);
CREATE INDEX idx_scenarios_target_component_id ON scenarios(target_component_id);
CREATE INDEX idx_scenarios_created_at ON scenarios(created_at DESC);
CREATE INDEX idx_scenarios_parameters ON scenarios USING GIN (parameters);


-- ============================================================================
-- TABLE: simulation_results
-- ============================================================================
-- Description: Simulation output snapshots associated with saved scenarios.
-- ============================================================================

CREATE TABLE simulation_results (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    baseline_score FLOAT NOT NULL,
    compromised_score FLOAT NOT NULL,
    affected_components JSONB DEFAULT '[]'::jsonb,
    attack_path JSONB DEFAULT '[]'::jsonb,
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for simulation_results
CREATE INDEX idx_simulation_results_scenario_id ON simulation_results(scenario_id);
CREATE INDEX idx_simulation_results_created_at ON simulation_results(created_at DESC);
CREATE INDEX idx_simulation_results_affected_components ON simulation_results USING GIN (affected_components);
CREATE INDEX idx_simulation_results_attack_path ON simulation_results USING GIN (attack_path);


-- ============================================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================================
-- Automatically updates the updated_at column when a row is modified
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_architectures_updated_at
    BEFORE UPDATE ON architectures
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_components_updated_at
    BEFORE UPDATE ON components
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flows_updated_at
    BEFORE UPDATE ON flows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================
-- Uncomment to insert sample architecture for development/testing
-- ============================================================================

/*
-- Sample Architecture: UAV Surveillance System
INSERT INTO architectures (name, description) VALUES 
('UAV Surveillance System', 'Unmanned aerial vehicle with ground control station');

-- Sample Components
INSERT INTO components (architecture_id, name, component_type, properties, position_x, position_y) VALUES
(1, 'EO/IR Camera', 'sensor', '{"confidentiality": 4, "integrity": 5, "availability": 5}', 100, 100),
(1, 'GPS Receiver', 'sensor', '{"confidentiality": 3, "integrity": 5, "availability": 5}', 100, 200),
(1, 'Flight Computer', 'compute', '{"confidentiality": 5, "integrity": 5, "availability": 5}', 300, 150),
(1, 'Radio Transceiver', 'communication', '{"confidentiality": 5, "integrity": 4, "availability": 5}', 500, 150),
(1, 'Ground Control Station', 'control', '{"confidentiality": 5, "integrity": 5, "availability": 5}', 700, 150);

-- Sample Flows
INSERT INTO flows (architecture_id, source_component_id, target_component_id, flow_type, properties) VALUES
(1, 1, 3, 'data', '{"bandwidth_mbps": 50, "protocol": "internal"}'),
(1, 2, 3, 'data', '{"bandwidth_mbps": 1, "protocol": "NMEA"}'),
(1, 3, 4, 'data', '{"bandwidth_mbps": 10, "protocol": "encrypted"}'),
(1, 4, 5, 'data', '{"bandwidth_mbps": 10, "protocol": "AES-256"}'),
(1, 5, 4, 'control', '{"bandwidth_mbps": 1, "protocol": "command"}');
*/


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify schema is working correctly
-- ============================================================================

-- Check table structure
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check indexes
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;

-- Check foreign keys
-- SELECT conname, conrelid::regclass, confrelid::regclass 
-- FROM pg_constraint WHERE contype = 'f';
