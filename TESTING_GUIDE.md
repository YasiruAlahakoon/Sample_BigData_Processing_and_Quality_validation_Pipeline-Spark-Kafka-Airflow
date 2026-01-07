# 🧪 Testing & Validation Guide

## Complete Setup and Testing Checklist

### ✅ Phase 1: Initial Setup (10 minutes)

#### Step 1.1: Install Prerequisites
```powershell
# Check Docker
docker --version
# Expected: Docker version 20.x or higher

# Check Python
python --version
# Expected: Python 3.9 or higher

# Check pip
pip --version
```

#### Step 1.2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

**Verify installations:**
```powershell
python -c "import pandas; print('pandas OK')"
python -c "import faker; print('faker OK')"
python -c "import great_expectations; print('great_expectations OK')"
python -c "import kafka; print('kafka OK')"
```

#### Step 1.3: Create Directory Structure
```powershell
# Run setup script (recommended)
.\setup.ps1

# OR manually create directories:
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/streaming
mkdir -p data/quality_reports
mkdir -p airflow/logs
```

---

### ✅ Phase 2: Start Infrastructure (5 minutes)

#### Step 2.1: Launch Docker Containers
```powershell
docker-compose up -d
```

**Expected output:**
```
Creating network "telecom_data_pipeline_sample_telecom_network" with driver "bridge"
Creating zookeeper ... done
Creating namenode ... done
Creating datanode ... done
Creating spark-master ... done
Creating kafka ... done
Creating airflow-postgres ... done
Creating spark-worker ... done
Creating kafka-ui ... done
Creating airflow-webserver ... done
Creating airflow-scheduler ... done
```

#### Step 2.2: Wait for Initialization (90 seconds)
```powershell
# Wait
Start-Sleep -Seconds 90

# Or check container status
docker ps
```

**Expected: 10 containers running:**
- ✅ namenode
- ✅ datanode
- ✅ spark-master
- ✅ spark-worker
- ✅ zookeeper
- ✅ kafka
- ✅ kafka-ui
- ✅ airflow-postgres
- ✅ airflow-webserver
- ✅ airflow-scheduler

#### Step 2.3: Verify Services
```powershell
# Check Spark Master
curl http://localhost:8080
# Should return HTML

# Check Airflow
curl http://localhost:8088
# Should return HTML

# Check container logs (no errors)
docker logs spark-master | Select-String -Pattern "ERROR"
docker logs airflow-webserver | Select-String -Pattern "ERROR"
```

---

### ✅ Phase 3: Test Batch Pipeline (10 minutes)

#### Step 3.1: Generate Test Data
```powershell
python src/generator.py
```

**Expected output:**
```
[INFO] Created directory: ./data/raw
[INFO] Generating 5000 records...
[SUCCESS] Data generated at: ./data/raw/cdr_20260107_123456.csv
```

**Verify:**
```powershell
# Check file exists
ls data/raw/*.csv

# Peek at data
Get-Content data/raw/cdr_*.csv | Select-Object -First 5
```

#### Step 3.2: Run Quality Validation
```powershell
python src/data_quality_validator.py
```

**Expected output:**
```
[QUALITY CHECK] Validating: ./data/raw/cdr_20260107_123456.csv
============================================================
[1/7] Checking schema completeness...
[2/7] Checking for NULL values...
[3/7] Checking call_id uniqueness...
[4/7] Validating phone number formats...
[5/7] Validating call types...
[6/7] Checking duration constraints...
[7/7] Validating signal strength range...

============================================================
VALIDATION SUMMARY
============================================================
Overall Status: ✓ PASSED
Total Checks: 10
Successful: 10
Failed: 0
Success Rate: 100.0%
============================================================

[QUALITY GATE] ✓ Data quality checks PASSED!
```

**Verify:**
```powershell
# Check report exists
ls data/quality_reports/*.html

# Open report in browser
start data/quality_reports/validation_report_*.html
```

#### Step 3.3: Process with Spark
```powershell
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py
```

**Expected output:**
```
[INFO] Starting Spark Session...
[INFO] Reading data from /data/raw/*.csv...
[INFO] Calculating Billing metrics...
[INFO] Analyzing Tower Network stats...
[INFO] Saving Billing Data to /data/processed/billing_report...
[INFO] Saving Network Data to /data/processed/network_health...
[SUCCESS] ETL Job Completed.
```

**Verify:**
```powershell
# Check output directories
ls data/processed/billing_report/
ls data/processed/network_health/

# Both should contain:
# - _SUCCESS file
# - part-*.parquet files
```

#### Step 3.4: View Results
```powershell
# View billing data
python -c "import pandas as pd; df = pd.read_parquet('data/processed/billing_report'); print(df.head(10))"

# View network data
python -c "import pandas as pd; df = pd.read_parquet('data/processed/network_health'); print(df.head(10))"
```

**Expected output (billing):**
```
     caller_num  total_talk_seconds  total_calls  billable_minutes
0  +94712345678                 3456           12              57.6
1  +94787654321                 2890            8              48.2
...
```

---

### ✅ Phase 4: Test Airflow Orchestration (5 minutes)

#### Step 4.1: Access Airflow UI
1. Open browser: http://localhost:8088
2. Login: `admin` / `admin`

**Expected:**
- Should see Airflow dashboard
- DAG list should show `telecom_cdr_etl_pipeline`

#### Step 4.2: Enable and Trigger DAG
1. Click toggle next to `telecom_cdr_etl_pipeline` (turn ON)
2. Click "Trigger DAG" button (play icon)
3. Click DAG name to view details
4. Switch to "Graph" view

**Expected:**
- All tasks should turn green (success)
- Flow: generate_cdr_data → validate_data_quality → spark_etl_processing → validate_output_data → calculate_pipeline_metrics

#### Step 4.3: Check Task Logs
1. Click any task box
2. Click "Log" button

**Expected:**
- Should see detailed execution logs
- No errors

---

### ✅ Phase 5: Test Streaming Pipeline (10 minutes)

#### Step 5.1: Start Spark Streaming Consumer
```powershell
# Terminal 1 (PowerShell)
docker exec -it spark-master /spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 /src/streaming_consumer.py
```

**Expected output:**
```
[STREAMING] Starting Spark Structured Streaming...
[STREAMING] Connecting to Kafka: kafka:9092
[STREAMING] Setting up real-time billing analytics...
[STREAMING] Setting up real-time network monitoring...
[STREAMING] ✓ All streaming queries started successfully!
[STREAMING] Processing real-time CDR events...
```

#### Step 5.2: Start Kafka Producer
```powershell
# Terminal 2 (new PowerShell window)
docker exec -it spark-master python /src/streaming_producer.py --rate 10 --broker kafka:9092 --duration 5
```

**Expected output:**
```
[STREAMING] Starting CDR event stream...
[CONFIG] Rate: 10 events/sec | Topic: cdr-events
[STREAMING] Sent 100 events...
[STREAMING] Sent 200 events...
[STREAMING] Sent 300 events...
...
[STREAMING] Total events sent: 3000
```

#### Step 5.3: Monitor in Kafka UI
1. Open browser: http://localhost:8082
2. Click "Topics"
3. Click "cdr-events"

**Expected:**
- Should see topic with messages
- Message count increasing
- Partitions balanced

#### Step 5.4: Verify Streaming Output
```powershell
# Wait 2 minutes for data to accumulate
Start-Sleep -Seconds 120

# Check streaming output
ls data/streaming/billing_realtime/
ls data/streaming/network_realtime/

# Should contain parquet files
```

**View streaming data:**
```powershell
python -c "import pandas as pd; df = pd.read_parquet('data/streaming/billing_realtime'); print(df.head())"
```

---

### ✅ Phase 6: Performance Monitoring (5 minutes)

#### Step 6.1: Check Spark UI
1. Open: http://localhost:8080
2. Check "Running Applications" or "Completed Applications"
3. Click on application ID

**Expected:**
- Shows stages, tasks, executors
- Job execution timeline
- No failed tasks

#### Step 6.2: Check Resource Usage
```powershell
# Container stats
docker stats --no-stream

# Disk usage
docker system df
```

#### Step 6.3: Check Logs for Errors
```powershell
# Check all containers
docker-compose logs | Select-String -Pattern "ERROR|FATAL"

# Should be minimal or none
```

---

### ✅ Phase 7: Data Quality Validation (5 minutes)

#### Test 7.1: Inject Bad Data
```powershell
# Create invalid data
@"
call_id,caller_num,receiver_num,call_type,duration_sec,timestamp,tower_id,signal_strength
123,INVALID_PHONE,+94712345678,VOICE,100,2026-01-07 12:00:00,TOWER_001,5
456,+94712345678,+94787654321,INVALID_TYPE,50,2026-01-07 12:05:00,TOWER_002,3
789,+94712345678,+94787654321,VOICE,8000,2026-01-07 12:10:00,TOWER_003,10
"@ | Out-File -FilePath "data/raw/cdr_bad_data.csv" -Encoding ASCII

# Run validator
python src/data_quality_validator.py
```

**Expected output:**
```
Overall Status: ✗ FAILED
Total Checks: 10
Successful: 5
Failed: 5
Success Rate: 50.0%

FAILED VALIDATIONS:
✗ expect_column_values_to_match_regex
  Column: caller_num
  Details: 1 unexpected values
✗ expect_column_values_to_be_in_set
  Column: call_type
  Details: 1 unexpected value (INVALID_TYPE)
✗ expect_column_values_to_be_between
  Column: duration_sec
  Details: 1 value exceeds max (8000 > 7200)
...

[QUALITY GATE] ✗ Data quality checks FAILED!
```

**Verify quality gate works:**
- Pipeline should block
- HTML report shows failures
- Exit code: 1 (failure)

#### Test 7.2: Clean Up Bad Data
```powershell
Remove-Item data/raw/cdr_bad_data.csv
```

---

### ✅ Phase 8: End-to-End Integration Test (5 minutes)

#### Run complete workflow:
```powershell
# 1. Clean previous data
Remove-Item data/raw/cdr_*.csv
Remove-Item -Recurse data/processed/*

# 2. Generate fresh data
python src/generator.py

# 3. Validate quality
python src/data_quality_validator.py
# Should PASS

# 4. Process with Spark
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py
# Should complete successfully

# 5. Verify outputs
Test-Path data/processed/billing_report/_SUCCESS
Test-Path data/processed/network_health/_SUCCESS
# Both should return True
```

---

### ✅ Phase 9: Cleanup (2 minutes)

```powershell
# Stop all containers
docker-compose down

# Optional: Remove volumes (deletes data)
docker-compose down -v

# Optional: Clean Docker system
docker system prune -f
```

---

## 🎯 Test Coverage Summary

| Component | Test Type | Status |
|-----------|-----------|--------|
| Data Generator | Functional | ✅ |
| Quality Validator | Functional | ✅ |
| Quality Validator | Negative Test | ✅ |
| Spark Batch ETL | Functional | ✅ |
| Airflow DAG | Integration | ✅ |
| Kafka Producer | Functional | ✅ |
| Spark Streaming | Integration | ✅ |
| End-to-End | Full Pipeline | ✅ |

---

## 🐛 Common Issues & Solutions

### Issue 1: "Port already in use"
**Error:** `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8080

# Kill process
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Issue 2: "No module named 'great_expectations'"
**Solution:**
```powershell
pip install great-expectations
```

### Issue 3: Airflow shows "Broken DAG"
**Solution:**
```powershell
docker logs airflow-scheduler
# Check for Python errors

# Install missing packages
docker exec -it airflow-webserver pip install great-expectations kafka-python
docker-compose restart airflow-scheduler
```

### Issue 4: Kafka connection timeout
**Solution:**
```powershell
# Check Kafka is running
docker logs kafka

# Wait 60 seconds after docker-compose up
Start-Sleep -Seconds 60
```

### Issue 5: Spark job memory error
**Solution:**
- Docker Desktop → Settings → Resources → Memory → 8GB
- Restart Docker Desktop

---

## 📊 Performance Benchmarks

**Expected timings (on 8GB RAM, 4 CPU cores):**

| Operation | Expected Time |
|-----------|---------------|
| Docker startup | 60-90 seconds |
| Data generation (5K records) | 2-5 seconds |
| Quality validation | 5-10 seconds |
| Spark ETL processing | 30-60 seconds |
| Airflow DAG execution | 2-3 minutes |
| Streaming (100 events) | 5-10 seconds |

**If slower:** Increase Docker resources or reduce data volume

---

## ✅ Final Checklist

Before demoing or interviewing:

- [ ] All 10 containers running
- [ ] All 5 UIs accessible
- [ ] Batch pipeline runs successfully
- [ ] Quality validation passes
- [ ] Airflow DAG executes
- [ ] Streaming producer/consumer work
- [ ] Quality reports generate
- [ ] No errors in container logs
- [ ] README.md reviewed
- [ ] QUICK_REFERENCE.md bookmarked

**You're ready to demo! 🎉**
