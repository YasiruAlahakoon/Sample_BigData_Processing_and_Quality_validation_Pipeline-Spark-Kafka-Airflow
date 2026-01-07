# 🚀 GETTING STARTED - 5 Minutes to Running Pipeline

## ⚡ Ultra-Quick Start

### Step 1: Run Setup Script (Automated)
```powershell
.\setup.ps1
```
**This script does everything:**
- ✅ Checks Docker & Python
- ✅ Installs dependencies
- ✅ Creates directories
- ✅ Starts all 10 containers

**Wait 90 seconds for initialization**

---

### Step 2: Access Web Dashboards

Open these in your browser:

| What | URL | Login |
|------|-----|-------|
| **Airflow** (Main UI) | http://localhost:8088 | admin/admin |
| **Spark Master** | http://localhost:8080 | - |
| **Kafka UI** | http://localhost:8082 | - |

---

### Step 3: Run Your First Pipeline (Choose One)

#### **Option A: Manual Batch Pipeline** (3 commands)
```powershell
# Generate data
python src/generator.py

# Validate quality
python src/data_quality_validator.py

# Process with Spark
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py
```

#### **Option B: Automated with Airflow** (Click buttons)
1. Go to http://localhost:8088
2. Login: `admin` / `admin`
3. Find DAG: `telecom_cdr_etl_pipeline`
4. Click toggle to enable (turn ON)
5. Click play button to trigger
6. Watch it run!

---

### Step 4: View Results
```powershell
# See billing data
python -c "import pandas as pd; print(pd.read_parquet('data/processed/billing_report').head())"

# See network health
python -c "import pandas as pd; print(pd.read_parquet('data/processed/network_health').head())"
```

---

## 📚 What to Read Next

**For Understanding:**
1. [README.md](README.md) - Complete project overview
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Visual diagrams
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command cheatsheet

**For Testing:**
4. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Step-by-step validation

**For Interviews:**
5. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complexity analysis & talking points

---

## 🎯 30-Second Elevator Pitch

> "I built a production-grade telecom data pipeline with **batch and real-time processing**. It uses **Apache Spark** for distributed processing, **Kafka** for streaming, **Airflow** for orchestration, and **Great Expectations** for automated data quality validation. All components run in **Docker** with **5 monitoring dashboards**. The pipeline processes call detail records with **7 automated quality checks** that block bad data, then generates customer billing and network health analytics."

---

## 🐛 Quick Troubleshooting

**Docker containers won't start?**
```powershell
docker-compose down
docker-compose up -d
```

**Port already in use?**
```powershell
# Find and kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Python package missing?**
```powershell
pip install -r requirements.txt
```

**Airflow UI not loading?**
```powershell
# Wait 90 seconds after docker-compose up
# Then check logs:
docker logs airflow-webserver
```

---

## 📊 What You Built (Technical Specs)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Storage** | Hadoop HDFS | Distributed file system |
| **Batch Processing** | Apache Spark | Parallel data processing |
| **Streaming** | Kafka + Spark Streaming | Real-time event processing |
| **Orchestration** | Apache Airflow | Workflow automation |
| **Quality** | Great Expectations | Data validation |
| **Infrastructure** | Docker Compose | Container orchestration |
| **Monitoring** | 5 Web UIs | Observability |

**Total Containers:** 10  
**Total Lines of Code:** ~1,500  
**Features:** Batch + Streaming + Quality + Orchestration  
**Skill Level:** Intermediate to Advanced  

---

## 🎓 Skills You Can Claim

✅ Distributed systems (Hadoop, Spark)  
✅ Stream processing (Kafka, Spark Structured Streaming)  
✅ Workflow orchestration (Airflow)  
✅ Data quality engineering (Great Expectations)  
✅ ETL pipeline design  
✅ Docker containerization  
✅ Big data formats (Parquet)  
✅ SQL aggregations  
✅ Python data engineering  
✅ Microservices architecture  

---

## 🚀 Advanced Usage (After Basics)

### Start Streaming Pipeline
```powershell
# Terminal 1: Start consumer
docker exec -it spark-master /spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 /src/streaming_consumer.py

# Terminal 2: Start producer
docker exec -it spark-master python /src/streaming_producer.py --rate 10 --broker kafka:9092
```

### Monitor in Kafka UI
http://localhost:8082 → Topics → cdr-events

### Test Data Quality Gates
```powershell
# Create bad data
echo "call_id,caller_num" > data/raw/bad.csv
echo "123,INVALID" >> data/raw/bad.csv

# Run validator (should fail)
python src/data_quality_validator.py
```

---

## 🎉 Success Checklist

After setup, you should have:

- [ ] 10 containers running (`docker ps`)
- [ ] 5 web UIs accessible
- [ ] Batch pipeline runs successfully
- [ ] Quality validation passes
- [ ] Airflow DAG visible and runnable
- [ ] Parquet files in `data/processed/`
- [ ] No errors in container logs

**If all checked, you're ready to demo! 🎉**

---

## 📞 What's Next?

**For Resume:**
- Add this project to LinkedIn/GitHub
- Highlight: "Built production-grade data pipeline with Spark, Kafka, Airflow, and quality automation"

**For Interviews:**
- Practice the 5-minute demo
- Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for talking points
- Be ready to explain architecture diagrams

**To Go Further:**
- Deploy to AWS/GCP
- Add unit tests (pytest)
- Create ML pipeline
- Add monitoring (Grafana)

---

## 💡 Remember

**This project demonstrates:**
- ✅ Production thinking (quality gates, orchestration, monitoring)
- ✅ Modern data engineering stack
- ✅ Real-world patterns (streaming + batch)
- ✅ DevOps skills (Docker, containerization)

**You're not just building a demo - you're showing engineering maturity! 🚀**
