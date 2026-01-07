"""
Airflow DAG for Telecom CDR ETL Pipeline
Orchestrates: Data Generation → Quality Validation → Spark Processing → Monitoring
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

# Add project path
sys.path.insert(0, '/opt/airflow/src')

default_args = {
    'owner': 'data-engineering-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'telecom_cdr_etl_pipeline',
    default_args=default_args,
    description='End-to-End Telecom CDR Data Pipeline with Quality Checks',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    start_date=days_ago(1),
    catchup=False,
    tags=['telecom', 'etl', 'data-quality'],
)

# ===== TASK 1: Generate CDR Data =====
def generate_cdr_data():
    """Generate synthetic CDR data"""
    import subprocess
    result = subprocess.run(['python', '/opt/airflow/src/generator.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Data generation failed: {result.stderr}")
    return "CDR data generated successfully"

task_generate_data = PythonOperator(
    task_id='generate_cdr_data',
    python_callable=generate_cdr_data,
    dag=dag,
)

# ===== TASK 2: Data Quality Validation =====
task_validate_quality = BashOperator(
    task_id='validate_data_quality',
    bash_command='python /opt/airflow/src/data_quality_validator.py',
    dag=dag,
)

# ===== TASK 3: Spark ETL Processing =====
task_spark_etl = BashOperator(
    task_id='spark_etl_processing',
    bash_command='docker exec spark-master /spark/bin/spark-submit /src/process_cdr.py',
    dag=dag,
)

# ===== TASK 4: Data Quality Check on Output =====
def validate_output_data():
    """Verify output data was created"""
    import os
    billing_path = "/opt/airflow/data/processed/billing_report/_SUCCESS"
    network_path = "/opt/airflow/data/processed/network_health/_SUCCESS"
    
    if not os.path.exists(billing_path):
        raise Exception("Billing report not generated!")
    if not os.path.exists(network_path):
        raise Exception("Network health report not generated!")
    
    print("✓ All output files validated successfully")
    return "Output validation passed"

task_validate_output = PythonOperator(
    task_id='validate_output_data',
    python_callable=validate_output_data,
    dag=dag,
)

# ===== TASK 5: Generate Metrics =====
def calculate_pipeline_metrics():
    """Calculate and log pipeline metrics"""
    import glob
    import pandas as pd
    
    # Count records processed
    raw_files = glob.glob("/opt/airflow/data/raw/cdr_*.csv")
    latest_file = max(raw_files, key=os.path.getctime)
    
    df_raw = pd.read_csv(latest_file)
    total_records = len(df_raw)
    
    # Read processed data
    df_billing = pd.read_parquet("/opt/airflow/data/processed/billing_report")
    df_network = pd.read_parquet("/opt/airflow/data/processed/network_health")
    
    metrics = {
        'total_records_processed': total_records,
        'unique_customers': len(df_billing),
        'active_towers': len(df_network),
        'total_billable_minutes': df_billing['billable_minutes'].sum(),
        'avg_traffic_per_tower': df_network['traffic_load'].mean(),
    }
    
    print("\n" + "=" * 60)
    print("PIPELINE METRICS")
    print("=" * 60)
    for key, value in metrics.items():
        print(f"{key}: {value:.2f}")
    print("=" * 60)
    
    return metrics

task_calculate_metrics = PythonOperator(
    task_id='calculate_pipeline_metrics',
    python_callable=calculate_pipeline_metrics,
    dag=dag,
)

# ===== TASK DEPENDENCIES (Pipeline Flow) =====
task_generate_data >> task_validate_quality >> task_spark_etl >> task_validate_output >> task_calculate_metrics
