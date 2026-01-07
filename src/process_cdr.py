from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, avg, desc
import sys

# --- CONFIG ---
# Inside Docker, the local './data' folder is mounted at '/data'
INPUT_PATH = "/data/raw/*.csv" 
OUTPUT_BILLING = "/data/processed/billing_report"
OUTPUT_NETWORK = "/data/processed/network_health"

def main():
    # 1. Initialize Spark Session (The Engine)
    print("[INFO] Starting Spark Session...")
    spark = SparkSession.builder \
        .appName("Telecom_CDR_ETL") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN") # Reduce console spam

    # 2. Extract (Read Data)
    # Using .format() instead of f-strings for Python 2.7 compatibility
    print("[INFO] Reading data from {}...".format(INPUT_PATH))
    try:
        # inferSchema=True allows Spark to guess that 'duration' is a number
        df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)
    except Exception as e:
        print("[ERROR] Could not read data: {}".format(e))
        sys.exit(1)

    # Check if data frame is empty
    if df.rdd.isEmpty():
        print("[ERROR] No data found! Run the generator.py locally first.")
        sys.exit(1)

    # 3. Transform (Business Logic)
    
    # JOB A: Customer Billing (Sum of duration for VOICE calls)
    print("[INFO] Calculating Billing metrics...")
    billing_df = df.filter(col("call_type") == "VOICE") \
        .groupBy("caller_num") \
        .agg(
            sum("duration_sec").alias("total_talk_seconds"),
            count("call_id").alias("total_calls")
        ) \
        .withColumn("billable_minutes", col("total_talk_seconds") / 60) \
        .orderBy(desc("billable_minutes"))

    # JOB B: Network Health (Traffic load per tower)
    print("[INFO] Analyzing Tower Network stats...")
    network_df = df.groupBy("tower_id") \
        .agg(
            count("call_id").alias("traffic_load"),
            avg("signal_strength").alias("avg_signal_quality")
        ) \
        .orderBy(desc("traffic_load"))

    # 4. Load (Save Data)
    # We save as 'Parquet' because it is highly efficient for big data querying
    
    print("[INFO] Saving Billing Data to {}...".format(OUTPUT_BILLING))
    billing_df.write.mode("overwrite").parquet(OUTPUT_BILLING)
    
    print("[INFO] Saving Network Data to {}...".format(OUTPUT_NETWORK))
    network_df.write.mode("overwrite").parquet(OUTPUT_NETWORK)

    print("[SUCCESS] ETL Job Completed.")
    spark.stop()

if __name__ == "__main__":
    main()