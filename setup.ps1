# Quick Setup Script for Windows PowerShell
# Run this to set up the entire environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Telecom Data Pipeline - Quick Setup  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/6] Checking Docker installation..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker --version
    Write-Host "✓ Docker is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Docker not found! Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check Python
Write-Host "`n[2/6] Checking Python installation..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    python --version
    Write-Host "✓ Python is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.9+." -ForegroundColor Red
    exit 1
}

# Step 3: Install Python dependencies
Write-Host "`n[3/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python packages installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install packages" -ForegroundColor Red
    exit 1
}

# Step 4: Create necessary directories
Write-Host "`n[4/6] Creating project directories..." -ForegroundColor Yellow
$directories = @(
    "data/raw",
    "data/processed",
    "data/streaming",
    "data/quality_reports",
    "airflow/logs"
)
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Step 5: Stop any existing containers
Write-Host "`n[5/6] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "✓ Cleaned up old containers" -ForegroundColor Green

# Step 6: Start all services
Write-Host "`n[6/6] Starting Docker containers..." -ForegroundColor Yellow
Write-Host "    This may take 2-3 minutes on first run..." -ForegroundColor Gray
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All containers started successfully!" -ForegroundColor Green
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Setup Complete! 🎉" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nWait 60 seconds for initialization, then access:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  📊 Airflow UI       : http://localhost:8088 (admin/admin)" -ForegroundColor White
    Write-Host "  ⚡ Spark Master UI  : http://localhost:8080" -ForegroundColor White
    Write-Host "  🔧 Spark Worker UI  : http://localhost:8081" -ForegroundColor White
    Write-Host "  📨 Kafka UI         : http://localhost:8082" -ForegroundColor White
    Write-Host "  💾 Hadoop HDFS UI   : http://localhost:9870" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Generate data    : python src/generator.py" -ForegroundColor Gray
    Write-Host "  2. Validate quality : python src/data_quality_validator.py" -ForegroundColor Gray
    Write-Host "  3. Process with Spark" -ForegroundColor Gray
    Write-Host ""
    Write-Host "For full instructions, see README.md" -ForegroundColor Cyan
    
} else {
    Write-Host "✗ Failed to start containers" -ForegroundColor Red
    Write-Host "Run 'docker-compose logs' to see errors" -ForegroundColor Yellow
    exit 1
}
