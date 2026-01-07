# Testing Guide

## Validation Checklist

### Infrastructure Validation

Verify all containers are running:
```bash
docker ps
```

Expected: 10 containers with status "Up"

Check container health:
```bash
docker-compose ps
```

Verify web interfaces are accessible:
- http://localhost:8088 (Airflow)
- http://localhost:8080 (Spark Master)
- http://localhost:8082 (Kafka UI)
- http://localhost:9870 (Hadoop HDFS)

### Batch Pipeline Test

**1. Generate test data:**
```bash
python src/generator.py
```

Verify file created:
```bash
ls data/raw/cdr_*.csv
```

**2. Run quality validation:**
```bash
python src/data_quality_validator.py
```

Expected output: All 7 checks pass

**3. Process with Spark:**
```bash
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py
```

Expected: Job completes without errors

**4. Verify output:**
```bash
ls data/processed/billing_report/_SUCCESS
ls data/processed/network_health/_SUCCESS
```

**5. Check results:**
```bash
python -c "import pandas as pd; print(pd.read_parquet('data/processed/billing_report').head())"
```

### Streaming Pipeline Test

**1. Start consumer (Terminal 1):**
```bash
docker exec -it spark-master /spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 \
  /src/streaming_consumer.py
```

**2. Start producer (Terminal 2):**
```bash
docker exec -it spark-master python /src/streaming_producer.py \
  --rate 10 --broker kafka:9092 --duration 2
```

**3. Monitor Kafka UI:**
- Open http://localhost:8082
- Navigate to Topics → cdr-events
- Verify messages are being published

**4. Verify streaming output:**
```bash
ls data/streaming_output/
```

### Airflow DAG Test

**1. Access Airflow UI:**
- Open http://localhost:8088
- Login: admin/admin

**2. Enable DAG:**
- Find `telecom_cdr_etl_pipeline`
- Toggle switch to ON

**3. Trigger DAG:**
- Click play button
- Select "Trigger DAG"

**4. Monitor execution:**
- Click DAG name
- Switch to Graph view
- All tasks should turn green

**5. Check task logs:**
- Click any task
- Click "Log" button
- Verify no errors

### Data Quality Test

**Test with invalid data:**

Create bad data file:
```bash
echo "call_id,caller_num,receiver_num,call_type,duration_sec,timestamp,tower_id,signal_strength" > data/raw/bad_test.csv
echo "123,INVALID,+94712345678,VOICE,100,2026-01-07,TOWER_001,5" >> data/raw/bad_test.csv
```

Run validator:
```bash
python src/data_quality_validator.py
```

Expected: Validation fails with detailed error report

Clean up:
```bash
rm data/raw/bad_test.csv
```

## Performance Testing

### Batch Processing Performance

Process 5,000 records:
```bash
time docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py
```

Expected time: 30-60 seconds

### Streaming Throughput

Test with 100 events/second:
```bash
docker exec -it spark-master python /src/streaming_producer.py \
  --rate 100 --broker kafka:9092 --duration 1
```

Monitor in Kafka UI for message throughput.

## Error Scenarios

### Test Memory Pressure

Generate large dataset:
```python
# Modify RECORDS_COUNT in src/generator.py to 50000
python src/generator.py
```

Run Spark job and monitor memory warnings.

### Test Network Failure

Stop Kafka:
```bash
docker-compose stop kafka
```

Attempt streaming (should fail):
```bash
docker exec -it spark-master python /src/streaming_producer.py \
  --rate 10 --broker kafka:9092
```

Restart Kafka:
```bash
docker-compose start kafka
```

### Test Invalid Schema

Create file with missing column:
```bash
echo "call_id,caller_num" > data/raw/schema_test.csv
echo "123,+94712345678" >> data/raw/schema_test.csv
```

Run validator (should fail):
```bash
python src/data_quality_validator.py
```

Clean up:
```bash
rm data/raw/schema_test.csv
```

## Integration Testing

End-to-end test:
```bash
# Clean previous data
rm -rf data/raw/cdr_*.csv
rm -rf data/processed/*

# Generate new data
python src/generator.py

# Validate
python src/data_quality_validator.py

# Process
docker exec -it spark-master /spark/bin/spark-submit /src/process_cdr.py

# Verify outputs exist
test -f data/processed/billing_report/_SUCCESS && echo "Billing OK"
test -f data/processed/network_health/_SUCCESS && echo "Network OK"
```

## Troubleshooting Tests

### Container Health Check

```bash
docker inspect spark-master | grep Status
docker inspect kafka | grep Status
```

### Log Analysis

Search for errors:
```bash
docker logs spark-master 2>&1 | grep -i error
docker logs airflow-scheduler 2>&1 | grep -i error
```

### Resource Usage

Monitor container resources:
```bash
docker stats --no-stream
```

### Network Connectivity

Test network between containers:
```bash
docker exec spark-master ping -c 3 kafka
docker exec airflow-webserver ping -c 3 postgres
```

## Test Data Cleanup

Remove all test data:
```bash
rm -rf data/raw/*.csv
rm -rf data/processed/*
rm -rf data/streaming_output/*
rm -rf data/archive/*
rm -rf data/quality_reports/*.html
```

Reset Docker environment:
```bash
docker-compose down -v
docker-compose up -d
```
