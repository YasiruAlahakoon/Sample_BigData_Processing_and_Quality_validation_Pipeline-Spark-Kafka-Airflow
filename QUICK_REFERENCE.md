# 🚀 Quick Reference Guide

## 📋 Essential Commands

### Start/Stop Infrastructure
```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View running containers
docker ps

# View logs
docker logs <container-name>
```

### Run Batch Pipeline (Traditional ETL)
```powershell
# 1. Generate data
python src/generator.py

# 2. Validate quality
python src/data_quality_validator.py

# 3. Process with Spark
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py

# 4. View results
python -c "import pandas as pd; print(pd.read_parquet('data/processed/billing_report'))"
```

### Run Streaming Pipeline (Real-time)
```powershell
# Terminal 1: Start Spark Streaming Consumer
docker exec -it spark-master /spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 /src/streaming_consumer.py

# Terminal 2: Start Kafka Producer
docker exec -it spark-master python /src/streaming_producer.py --rate 10 --broker kafka:9092
```

### Use Airflow (Orchestrated)
```powershell
# Access UI: http://localhost:8088 (admin/admin)

# Or use CLI:
docker exec -it airflow-webserver airflow dags trigger telecom_cdr_etl_pipeline
```

---

## 🌐 Web UI Access

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Airflow** | http://localhost:8088 | admin/admin | Workflow orchestration |
| **Spark Master** | http://localhost:8080 | - | Job monitoring |
| **Spark Worker** | http://localhost:8081 | - | Task execution |
| **Kafka UI** | http://localhost:8082 | - | Stream monitoring |
| **HDFS** | http://localhost:9870 | - | Storage browser |

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `src/generator.py` | Generate batch CDR data |
| `src/process_cdr.py` | Spark batch ETL |
| `src/data_quality_validator.py` | Quality validation |
| `src/streaming_producer.py` | Kafka event producer |
| `src/streaming_consumer.py` | Spark streaming consumer |
| `airflow/dags/telecom_etl_dag.py` | Airflow orchestration |
| `docker-compose.yml` | Infrastructure definition |

---

## 🔧 Common Tasks

### Check Data Quality Report
```powershell
# Reports saved in:
ls data/quality_reports/

# Open latest report in browser
start data/quality_reports/validation_report_*.html
```

### Monitor Kafka Topics
```powershell
# List topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# View messages
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic cdr-events --from-beginning
```

### Restart Specific Service
```powershell
docker-compose restart spark-master
docker-compose restart airflow-webserver
docker-compose restart kafka
```

---

## 🐛 Troubleshooting

### Container won't start
```powershell
# Check logs
docker logs <container-name>

# Recreate container
docker-compose up -d --force-recreate <service-name>
```

### Airflow DAG not appearing
```powershell
# Check scheduler logs
docker logs airflow-scheduler

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Python module not found
```powershell
# Install in local environment
pip install <package-name>

# Install in Airflow container
docker exec -it airflow-webserver pip install <package-name>
```

### Spark job fails with memory error
```powershell
# Increase Docker memory: Docker Desktop → Settings → Resources → Memory → 8GB
# Or reduce data volume
```

---

## 📊 Data Flow Summary

### Batch Processing Flow:
```
Generator → CSV → Quality Check → Spark ETL → Parquet
```

### Streaming Flow:
```
Producer → Kafka → Spark Streaming → Parquet
```

### Orchestrated Flow (Airflow):
```
Generate → Validate → Process → Verify → Metrics
```

---

## 🎯 Demo Script (For Interviews)

### 5-Minute Demo:

**Minute 1: Show Architecture**
- Open README.md
- Explain 3 layers: Storage (Hadoop), Processing (Spark), Streaming (Kafka), Orchestration (Airflow)

**Minute 2: Show UIs**
- Airflow UI: Show DAG graph
- Spark UI: Show cluster status
- Kafka UI: Show topics

**Minute 3: Run Batch Pipeline**
```powershell
python src/generator.py
python src/data_quality_validator.py
# Show quality report in browser
```

**Minute 4: Trigger Airflow Pipeline**
- Open Airflow UI
- Trigger DAG
- Show task execution in Graph View
- Show logs

**Minute 5: Show Results**
```powershell
python -c "import pandas as pd; print(pd.read_parquet('data/processed/billing_report').head())"
```
- Explain business metrics (billable minutes, tower traffic)

---

## 📈 Metrics to Mention

**Data Volume:**
- 5,000 records/batch
- 10 events/second streaming
- 50 cell towers
- 3 call types

**Processing:**
- Sub-minute batch processing
- 5-minute streaming windows
- 2 analytical jobs (billing + network)

**Quality:**
- 7 automated validations
- 100% data coverage
- HTML reports with pass/fail

**Infrastructure:**
- 10 Docker containers
- 5 Web UIs
- 3 processing modes (batch, stream, orchestrated)

---

## 💡 Interview Questions You Can Answer

**Q: How do you handle late-arriving data in streaming?**
A: "I use watermarking with a 10-minute threshold. Events arriving within the watermark window are included in the correct time bucket."

**Q: What happens if data quality checks fail?**
A: "The pipeline is blocked. Great Expectations generates an HTML report showing which validations failed, and Airflow marks the task as failed with automatic retries."

**Q: How do you ensure exactly-once processing?**
A: "Spark Structured Streaming uses checkpointing to track processed offsets in Kafka. If a job fails, it resumes from the last checkpoint."

**Q: How would you scale this for production?**
A: "Add more Spark workers, increase Kafka partitions, implement data partitioning by date/tower, and deploy to a managed service like Databricks or AWS EMR."

---

## 🎓 Learning Resources

**If You Want to Understand Deeper:**

- **Apache Spark:** https://spark.apache.org/docs/latest/
- **Great Expectations:** https://docs.greatexpectations.io/
- **Kafka:** https://kafka.apache.org/documentation/
- **Airflow:** https://airflow.apache.org/docs/

**Books:**
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Spark: The Definitive Guide" by Bill Chambers

**Courses:**
- Udemy: "Apache Spark with Python - Big Data Processing"
- Coursera: "Data Engineering on Google Cloud"
