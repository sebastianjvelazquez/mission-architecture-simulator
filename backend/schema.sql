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
    
    -- Core attributes
    name VARCHAR(255) NOT NULL,
    component_type VARCHAR(50) NOT NULL, -- sensor, compute, communication, control, etc.
    
    -- Flexible properties (JSONB for schema-less attributes)
    -- Example: {"confidentiality": 5, "integrity": 4, "availability": 5, "criticality": "HIGH"}
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
