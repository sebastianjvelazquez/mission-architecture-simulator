-- Test data insertion

-- Insert components with JSONB properties
INSERT INTO components (architecture_id, name, component_type, properties, position_x, position_y) VALUES 
(1, 'EO/IR Camera', 'sensor', '{"confidentiality": 4, "integrity": 5, "availability": 5, "criticality": "HIGH"}'::jsonb, 100, 100),
(1, 'Flight Computer', 'compute', '{"confidentiality": 5, "integrity": 5, "availability": 5, "criticality": "CRITICAL"}'::jsonb, 300, 150),
(1, 'Radio Transceiver', 'communication', '{"confidentiality": 5, "integrity": 4, "availability": 5}'::jsonb, 500, 150);

-- Insert flows
INSERT INTO flows (architecture_id, source_component_id, target_component_id, flow_type, properties) VALUES
(1, 1, 2, 'data', '{"bandwidth_mbps": 50, "protocol": "internal"}'::jsonb),
(1, 2, 3, 'data', '{"bandwidth_mbps": 10, "protocol": "encrypted"}'::jsonb);

-- Verify data
SELECT 'Architectures:' as table_name;
SELECT id, name, created_at FROM architectures;

SELECT 'Components:' as table_name;
SELECT id, name, component_type, properties->>'criticality' as criticality FROM components;

SELECT 'Flows:' as table_name;
SELECT id, source_component_id, target_component_id, flow_type FROM flows;

-- Test JSONB query
SELECT 'High Criticality Components:' as query_name;
SELECT name, component_type FROM components WHERE properties @> '{"criticality": "HIGH"}';
