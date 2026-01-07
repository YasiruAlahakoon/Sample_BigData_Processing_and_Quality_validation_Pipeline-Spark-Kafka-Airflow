# 📡 Telecom Data Engineering Pipeline (Production-Grade)

## 🎯 Overview

**Enterprise-level Big Data pipeline** for telecom CDR (Call Detail Records) processing with:
- **Real-time & Batch Processing** (Kafka + Spark Streaming + Spark Batch)
- **Data Quality Engineering** (Great Expectations validation)
- **Workflow Orchestration** (Apache Airflow with DAG scheduling)
- **Distributed Storage** (Hadoop HDFS)
- **Interactive Dashboards** (Multiple Web UIs)

**Target Role:** Mid to Senior Data Engineer + Quality Engineering

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Sources   │
│  (CDR Events)   │
└────────┬────────┘
         │
    ┌────▼─────────────────┬─────────────────┐
    │                      │                 │
┌───▼────┐         ┌──────▼──────┐   ┌─────▼─────┐
│ Kafka  │         │  Generator  │   │  Airflow  │
│ Stream │         │  (Batch)    │   │Orchestrator│
└───┬────┘         └──────┬──────┘   └─────┬─────┘
    │                     │                 │
    │              ┌──────▼──────┐          │
    │              │   Quality   │◄─────────┘
    │              │ Validation  │
    │              └──────┬──────┘
    │                     │
    │              ┌──────▼──────┐
    └─────────────►│    Spark    │
                   │  Processing │
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │    HDFS     │
                   │  Storage    │
                   └─────────────┘
```

### Components:
| Component | Purpose | Web UI Port |
|-----------|---------|-------------|
| **Hadoop HDFS** | Distributed storage | 9870 |
| **Spark Master** | Batch processing | 8080 |
| **Spark Worker** | Task execution | 8081 |
| **Kafka** | Event streaming | - |
| **Kafka UI** | Stream monitoring | 8082 |
| **Airflow** | Workflow orchestration | 8088 |
| **PostgreSQL** | Airflow metadata | 5432 |

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

**Install Docker Desktop** (Windows/Mac/Linux)
- Download: https://www.docker.com/products/docker-desktop

**Install Python 3.9+**
```powershell
python --version  # Should be 3.9 or higher
```

**Install Python Dependencies**
```powershell
pip install -r requirements.txt
```

---

### 2️⃣ Start the Infrastructure

**Launch all services** (Hadoop, Spark, Kafka, Airflow):
```powershell
docker-compose up -d
```

**Wait 90 seconds** for initialization, then verify:
```powershell
docker ps
```

You should see 10 containers running:
- `namenode`, `datanode`
- `spark-master`, `spark-worker`
- `zookeeper`, `kafka`, `kafka-ui`
- `airflow-webserver`, `airflow-scheduler`, `airflow-postgres`

---

### 3️⃣ Access Web Dashboards

Open these URLs in your browser:

| Dashboard | URL | Login | Description |
|-----------|-----|-------|-------------|
| **Airflow UI** | http://localhost:8088 | admin/admin | Workflow orchestration & scheduling |
| **Spark Master UI** | http://localhost:8080 | - | Spark cluster status & jobs |
| **Spark Worker UI** | http://localhost:8081 | - | Worker task execution |
| **Kafka UI** | http://localhost:8082 | - | Kafka topics & messages |
| **Hadoop HDFS UI** | http://localhost:9870 | - | HDFS storage browser |

---

## 📊 Pipeline Workflows

### **WORKFLOW 1: Batch Processing (Traditional ETL)**

#### Step 1: Generate CDR Data
```powershell
python src/generator.py
```
✅ Creates `data/raw/cdr_YYYYMMDD_HHMMSS.csv` with 5,000 records

#### Step 2: Run Quality Validation
```powershell
python src/data_quality_validator.py
```
✅ Validates:
- Schema completeness
- No NULL values
- Unique call_id
- Valid phone formats (+947XXXXXXXX)
- Valid call types (VOICE/SMS/DATA)
- Duration constraints (0-7200 sec)
- Signal strength range (1-5)

**Quality Report:** `data/quality_reports/validation_report_*.html`

#### Step 3: Process with Spark
```powershell
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py
```
✅ Generates:
- `data/processed/billing_report/` (Customer billing analytics)
- `data/processed/network_health/` (Tower performance metrics)

#### Step 4: View Results
```powershell
python -c "import pandas as pd; print(pd.read_parquet('data/processed/billing_report'))"
```

---

### **WORKFLOW 2: Real-time Streaming (Advanced)**

#### Step 1: Start Spark Streaming Consumer
```powershell
docker exec -it spark-master /spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 /src/streaming_consumer.py
```
✅ Listens to Kafka topic `cdr-events`
✅ Processes events in 5-minute windows
✅ Outputs to `data/streaming/`

#### Step 2: Start Kafka Producer (in new terminal)
```powershell
# Inside Docker container
docker exec -it spark-master python /src/streaming_producer.py --rate 10 --broker kafka:9092

# OR locally (if Kafka accessible)
python src/streaming_producer.py --rate 10 --broker localhost:29092
```
✅ Generates 10 events/second
✅ Publishes to Kafka topic

#### Step 3: Monitor in Kafka UI
Open http://localhost:8082
- View topic: `cdr-events`
- See real-time messages
- Monitor consumer lag

---

### **WORKFLOW 3: Orchestrated Pipeline (Production Mode)**

#### Step 1: Enable DAG in Airflow
1. Open **Airflow UI**: http://localhost:8088
2. Login: `admin` / `admin`
3. Find DAG: `telecom_cdr_etl_pipeline`
4. Toggle **ON** (unpause)

#### Step 2: Trigger Pipeline
Click **Trigger DAG** button

**Pipeline executes:**
1. 🟢 Generate CDR data
2. 🔵 Validate data quality
3. 🟡 Spark ETL processing
4. 🟣 Validate outputs
5. ⚫ Calculate metrics

#### Step 3: Monitor Execution
- **Graph View**: Visual DAG execution
- **Task Duration**: Performance metrics
- **Logs**: Click any task to see logs

**Schedule:** Runs automatically every 6 hours (`0 */6 * * *`)

---

## 📁 Project Structure

```
Telecom_Data_Pipeline_Sample/
│
├── docker-compose.yml          # Infrastructure definition (10 services)
├── hadoop.env                  # Hadoop configuration
├── requirements.txt            # Python dependencies
│
├── airflow/
│   └── dags/
│       └── telecom_etl_dag.py  # Airflow workflow orchestration
│
├── src/
│   ├── generator.py                  # Batch CDR data generator
│   ├── process_cdr.py                # Spark batch ETL
│   ├── data_quality_validator.py     # Great Expectations validation
│   ├── streaming_producer.py         # Kafka event producer
│   └── streaming_consumer.py         # Spark Structured Streaming
│
└── data/
    ├── raw/                    # Input CSV files
    ├── processed/              # Batch output (Parquet)
    ├── streaming/              # Real-time output (Parquet)
    └── quality_reports/        # Validation reports (HTML)
```

---

## 🔍 Data Quality Checks (7 Validations)

| # | Check | Rule | Action on Fail |
|---|-------|------|----------------|
| 1 | **Schema** | All columns present | Block pipeline |
| 2 | **Nulls** | No NULL in any column | Block pipeline |
| 3 | **Uniqueness** | call_id is unique | Block pipeline |
| 4 | **Phone Format** | +947XXXXXXXX pattern | Block pipeline |
| 5 | **Call Type** | VOICE/SMS/DATA only | Block pipeline |
| 6 | **Duration** | 0-7200 seconds | Block pipeline |
| 7 | **Signal** | 1-5 range | Block pipeline |

**Reports:** Auto-generated HTML with detailed failure analysis

---

## 🛠️ Advanced Commands

### Container Management
```powershell
# View all containers
docker ps

# View logs
docker logs airflow-webserver
docker logs spark-master
docker logs kafka

# Restart specific service
docker-compose restart spark-master

# Stop all
docker-compose down

# Stop and remove volumes (CAUTION: Deletes data)
docker-compose down -v
```

### Kafka Operations
```powershell
# List topics
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Describe topic
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic cdr-events

# Consume messages (console)
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic cdr-events --from-beginning
```

### Airflow CLI
```powershell
# List DAGs
docker exec -it airflow-webserver airflow dags list

# Test task
docker exec -it airflow-webserver airflow tasks test telecom_cdr_etl_pipeline generate_cdr_data 2026-01-07

# Trigger DAG manually
docker exec -it airflow-webserver airflow dags trigger telecom_cdr_etl_pipeline
```

---

## 📈 Performance Tuning

### For Large Data Volumes:

**Increase Spark Memory:**
```yaml
# In docker-compose.yml, add to spark-master/worker:
environment:
  - SPARK_DRIVER_MEMORY=4g
  - SPARK_EXECUTOR_MEMORY=4g
```

**Optimize Parquet Writing:**
```python
# In process_cdr.py, add before .write():
.coalesce(4)  # Reduce partition count
```

**Kafka Partitions:**
```powershell
# Create topic with 10 partitions
docker exec -it kafka kafka-topics --create --topic cdr-events --partitions 10 --replication-factor 1 --bootstrap-server localhost:9092
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'great_expectations'"
**Solution:**
```powershell
pip install great-expectations
```

### Issue: Airflow UI shows "Broken DAG"
**Solution:**
```powershell
# Check logs
docker logs airflow-scheduler

# Install missing Python packages in Airflow container
docker exec -it airflow-webserver pip install great-expectations kafka-python
```

### Issue: Kafka connection refused
**Solution:**
```powershell
# Check if Kafka is running
docker ps | grep kafka

# Wait 60 seconds after docker-compose up
```

### Issue: Spark job fails with memory error
**Solution:** Reduce data volume or increase Docker memory allocation (Docker Desktop Settings → Resources → Memory → 8GB)

---


