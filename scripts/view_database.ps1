# Quick Database Viewer Script
# Usage: .\view_database.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   MISSION DATABASE VIEWER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if container is running
$containerRunning = docker ps --filter "name=mission-db" --format "{{.Names}}" 2>$null

if (-not $containerRunning) {
    Write-Host "❌ Database container 'mission-db' is not running!" -ForegroundColor Red
    Write-Host "   Start it with: docker start mission-db`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Database container is running`n" -ForegroundColor Green

# Architectures
Write-Host "[ARCHITECTURES]" -ForegroundColor Yellow
Write-Host "=========================================`n" -ForegroundColor Gray
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT id, name, description, created_at FROM architectures;" 2>$null

# Components
Write-Host "`n[COMPONENTS]" -ForegroundColor Yellow
Write-Host "=========================================`n" -ForegroundColor Gray
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT id, name, component_type, properties->>'criticality' as criticality, architecture_id FROM components ORDER BY id;" 2>$null

# Flows
Write-Host "`n[FLOWS - Graph Edges]" -ForegroundColor Yellow
Write-Host "=========================================`n" -ForegroundColor Gray
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT f.id, src.name as source, f.flow_type, tgt.name as target FROM flows f JOIN components src ON f.source_component_id = src.id JOIN components tgt ON f.target_component_id = tgt.id ORDER BY f.id;" 2>$null

# Record counts
Write-Host "`n[RECORD COUNTS]" -ForegroundColor Yellow
Write-Host "=========================================`n" -ForegroundColor Gray
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT 'Architectures' as entity, COUNT(*) as count FROM architectures UNION ALL SELECT 'Components', COUNT(*) FROM components UNION ALL SELECT 'Flows', COUNT(*) FROM flows;" 2>$null

Write-Host "`n========================================`n" -ForegroundColor Cyan
Write-Host "TIPS:" -ForegroundColor Cyan
Write-Host "   - Install pgAdmin for visual browsing: https://www.pgadmin.org" -ForegroundColor Gray
Write-Host "   - Interactive shell: docker exec -it mission-db psql -U postgres -d mission_simulator" -ForegroundColor Gray
Write-Host "   - Clear test data: docker exec -i mission-db psql -U postgres -d mission_simulator -c 'TRUNCATE TABLE architectures CASCADE;'" -ForegroundColor Gray
Write-Host "`n" -ForegroundColor Gray
