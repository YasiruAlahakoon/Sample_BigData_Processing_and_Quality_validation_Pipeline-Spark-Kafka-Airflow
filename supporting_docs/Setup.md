# Setup Guide

## System Requirements

- Docker Desktop 20.x or higher
- Python 3.9 or higher
- 8GB RAM minimum
- 20GB disk space

## Installation

### 1. Install Docker

Download and install Docker Desktop:
- Windows/Mac: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

Verify installation:
```bash
docker --version
docker-compose --version
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Verify installations:
```bash
python -c "import pandas; print('OK')"
python -c "import great_expectations; print('OK')"
python -c "import kafka; print('OK')"
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

Wait 90 seconds for all services to initialize.

Verify all containers are running:
```bash
docker ps
```

Expected output: 10 containers running (namenode, datanode, spark-master, spark-worker, zookeeper, kafka, kafka-ui, postgres, airflow-webserver, airflow-scheduler)

### 4. Verify Web Interfaces

Open in browser:
- Airflow: http://localhost:8088 (admin/admin)
- Spark Master: http://localhost:8080
- Kafka UI: http://localhost:8082
- Hadoop HDFS: http://localhost:9870

## Configuration

### Docker Memory

If jobs fail with memory errors:
1. Open Docker Desktop
2. Settings → Resources → Memory
3. Increase to 8GB
4. Click "Apply & Restart"

### Airflow Configuration

Located in `airflow/dags/telecom_etl_dag.py`:
- Schedule interval: `0 */6 * * *` (every 6 hours)
- Retries: 2
- Retry delay: 5 minutes

### Spark Configuration

Located in `docker-compose.yml`:
- Driver memory: 366MB (default)
- Executor memory: 366MB (default)

To increase:
```yaml
spark-master:
  environment:
    - SPARK_DRIVER_MEMORY=2g
    - SPARK_EXECUTOR_MEMORY=2g
```

### Kafka Configuration

Topic: `cdr-events`
- Partitions: Auto-created
- Replication factor: 1
- Retention: 7 days

## Directory Structure

The following directories are created automatically:

```
data/
├── raw/              # Input CSV files
├── processed/        # Batch processing output
├── streaming_output/ # Streaming output
├── archive/          # Archived files
├── quality_reports/  # Validation reports
└── reports/          # Summary reports
```

## Network Configuration

All services communicate via Docker network `telecom_network`.

Internal hostnames:
- `namenode:9000` (HDFS)
- `spark-master:7077` (Spark)
- `kafka:9092` (Kafka broker)
- `postgres:5432` (Airflow metadata)

## Stopping Services

Stop all containers:
```bash
docker-compose down
```

Stop and remove all data:
```bash
docker-compose down -v
```

Restart specific service:
```bash
docker-compose restart spark-master
```

## Troubleshooting

### Port Conflicts

Check if ports are in use:
```bash
netstat -ano | findstr :8080
netstat -ano | findstr :8088
```

Kill process using port (Windows):
```bash
taskkill /PID <PID> /F
```

### Container Logs

View logs for debugging:
```bash
docker logs spark-master
docker logs airflow-webserver
docker logs kafka
```

### Airflow DAG Not Appearing

```bash
docker logs airflow-scheduler
docker-compose restart airflow-scheduler
```

### Kafka Connection Timeout

Ensure Kafka has fully started (takes 60-90 seconds):
```bash
docker logs kafka | grep "started"
```
