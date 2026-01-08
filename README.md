# Telecom Data Pipeline

A data engineering pipeline for processing telecom call detail records (CDR) using Apache Spark, Kafka, and Airflow with automated data quality validation.

## Architecture

```
Data Sources → Quality Validation → Processing → Storage
                                    ↓
                            Batch (Spark)
                            Stream (Kafka)
                            Orchestration (Airflow)
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Storage | Hadoop HDFS | Distributed file system |
| Batch Processing | Apache Spark | Parallel data processing |
| Streaming | Kafka + Spark Streaming | Real-time event processing |
| Orchestration | Apache Airflow | Workflow automation |
| Quality Validation | Great Expectations | Data validation framework |
| Infrastructure | Docker Compose | Container orchestration |

### Data Flow

**Batch Pipeline:**
```
CSV Files → Great Expectations → Spark ETL → Parquet Output
```

**Streaming Pipeline:**
```
Producer → Kafka → Spark Streaming → Parquet Output
```

**Orchestrated Pipeline:**
```
Airflow DAG: Generate → Validate → Process → Report
```

## Quick Start

### Prerequisites

- Docker Desktop
- Python 3.9+
- 8GB RAM minimum

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Wait 90 seconds for initialization
```

### Run Batch Pipeline

```bash
# Generate data
python src/generator.py

# Validate quality
python src/data_quality_validator.py

# Process with Spark
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py

# View results
python -c "import pandas as pd; print(pd.read_parquet('data/processed/billing_report'))"
```

### Run Streaming Pipeline

```bash
# Terminal 1: Start consumer
docker exec -it spark-master /spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 \
  /src/streaming_consumer.py

# Terminal 2: Start producer
docker exec -it spark-master python /src/streaming_producer.py \
  --rate 10 --broker kafka:9092
```

### Run with Airflow

1. Access Airflow UI: http://localhost:8088 (admin/admin)
2. Enable DAG: `telecom_cdr_etl_pipeline`
3. Trigger execution

## Web Interfaces

| Service | URL | Purpose |
|---------|-----|---------|
| Airflow | http://localhost:8088 | Workflow monitoring |
| Spark Master | http://localhost:8080 | Job execution |
| Kafka UI | http://localhost:8082 | Stream monitoring |
| Hadoop HDFS | http://localhost:9870 | Storage browser |

## Project Structure

```
├── src/
│   ├── generator.py                   # Data generation
│   ├── process_cdr.py                 # Spark batch ETL
│   ├── data_quality_validator.py      # Quality checks
│   ├── streaming_producer.py          # Kafka producer
│   └── streaming_consumer.py          # Spark streaming
│
├── airflow/
│   └── dags/
│       └── telecom_etl_dag.py         # Workflow definition
│
├── data/
│   ├── raw/                           # Input CSV files
│   ├── processed/                     # Batch output
│   ├── streaming_output/              # Stream output
│   └── quality_reports/               # Validation reports
│
├── docker-compose.yml                 # Infrastructure
├── requirements.txt                   # Python dependencies
└── supporting_docs/                   # Additional documentation
```
## Documentations

- [Architecture](supporting_docs/Architecture.md) - Detailed Architecture Block Diagrams
- [Setup Guide](supporting_docs/Setup.md) - Detailed installation and configuration
- [Testing Guide](supporting_docs/Testing.md) - Validation and testing procedures

## Data Quality Validation

The pipeline includes 7 automated quality checks:

1. Schema validation (required columns exist)
2. Null value detection
3. Uniqueness constraints (call_id)
4. Format validation (phone numbers: +947XXXXXXXX)
5. Enum validation (call_type: VOICE/SMS/DATA)
6. Range checks (duration: 0-7200 sec, signal: 1-5)
7. Business rules validation

Quality gates block processing if checks fail. Reports generated in HTML format.

## Technical Details

### Batch Processing

- Input: CSV files in `data/raw/`
- Processing: Spark aggregations (groupBy, sum, avg)
- Output: Parquet format in `data/processed/`
- Jobs: Customer billing, Network health analytics

### Streaming Processing

- Input: Kafka topic `cdr-events`
- Processing: 5-minute tumbling windows
- Output: Parquet format in `data/streaming_output/`
- Features: Watermarking (10 min), checkpointing, exactly-once semantics

### Orchestration

- Scheduler: Every 6 hours
- Tasks: Generate → Validate → Process → Report → Archive
- Retries: 2 attempts with 5-minute delay
- Monitoring: Web UI with task logs

## Common Commands

```bash
# View running containers
docker ps

# Check container logs
docker logs spark-master
docker logs airflow-webserver

# Restart service
docker-compose restart spark-master

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Troubleshooting

**Containers won't start:**
```bash
docker-compose down
docker-compose up -d
```

**Port conflicts:**
Check if ports 8080, 8081, 8082, 8088, 9092 are available.

**Memory errors:**
Increase Docker memory allocation to 8GB (Docker Desktop → Settings → Resources).

**Module not found:**
```bash
pip install -r requirements.txt
```



## Technology Stack

- Apache Spark 3.0.0
- Apache Kafka 7.4.0
- Apache Airflow 2.7.3
- Hadoop 3.2.1
- Great Expectations 0.18.8
- Docker Compose 3.8
- Python 3.9

## License

MIT License
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


