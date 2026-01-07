"""
Real-time CDR Streaming Consumer with Spark Structured Streaming
Processes CDR events from Kafka in real-time
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, window, sum, count, avg, desc, to_timestamp
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, TimestampType
)

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "cdr-events"

# Output paths for streaming results
OUTPUT_BILLING_STREAM = "/data/streaming/billing_realtime"
OUTPUT_NETWORK_STREAM = "/data/streaming/network_realtime"
CHECKPOINT_DIR = "/data/streaming/checkpoints"

def main():
    print("[STREAMING] Starting Spark Structured Streaming...")
    
    # Initialize Spark with Kafka support
    spark = SparkSession.builder \
        .appName("Telecom_CDR_Streaming") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Define schema for CDR events
    cdr_schema = StructType([
        StructField("call_id", StringType(), True),
        StructField("caller_num", StringType(), True),
        StructField("receiver_num", StringType(), True),
        StructField("call_type", StringType(), True),
        StructField("duration_sec", IntegerType(), True),
        StructField("timestamp", StringType(), True),
        StructField("tower_id", StringType(), True),
        StructField("signal_strength", IntegerType(), True),
        StructField("event_time", StringType(), True)
    ])
    
    # Read from Kafka stream
    print(f"[STREAMING] Connecting to Kafka: {KAFKA_BROKER}")
    raw_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON data
    parsed_stream = raw_stream \
        .selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), cdr_schema).alias("data")) \
        .select("data.*") \
        .withColumn("event_timestamp", to_timestamp(col("event_time")))
    
    # ===== STREAMING ANALYTICS 1: Real-time Billing (5-minute windows) =====
    print("[STREAMING] Setting up real-time billing analytics...")
    
    billing_stream = parsed_stream \
        .filter(col("call_type") == "VOICE") \
        .withWatermark("event_timestamp", "10 minutes") \
        .groupBy(
            window(col("event_timestamp"), "5 minutes", "1 minute"),
            col("caller_num")
        ) \
        .agg(
            sum("duration_sec").alias("total_talk_seconds"),
            count("call_id").alias("total_calls")
        ) \
        .withColumn("billable_minutes", col("total_talk_seconds") / 60) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            "caller_num",
            "billable_minutes",
            "total_calls"
        )
    
    # Write billing stream to Parquet (append mode)
    billing_query = billing_stream \
        .writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", OUTPUT_BILLING_STREAM) \
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/billing") \
        .trigger(processingTime='30 seconds') \
        .start()
    
    # ===== STREAMING ANALYTICS 2: Real-time Network Health =====
    print("[STREAMING] Setting up real-time network monitoring...")
    
    network_stream = parsed_stream \
        .withWatermark("event_timestamp", "10 minutes") \
        .groupBy(
            window(col("event_timestamp"), "5 minutes", "1 minute"),
            col("tower_id")
        ) \
        .agg(
            count("call_id").alias("traffic_load"),
            avg("signal_strength").alias("avg_signal_quality")
        ) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            "tower_id",
            "traffic_load",
            "avg_signal_quality"
        )
    
    # Write network stream to Parquet
    network_query = network_stream \
        .writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", OUTPUT_NETWORK_STREAM) \
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/network") \
        .trigger(processingTime='30 seconds') \
        .start()
    
    # ===== CONSOLE OUTPUT (for monitoring) =====
    console_query = parsed_stream \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='10 seconds') \
        .option("truncate", False) \
        .option("numRows", 5) \
        .start()
    
    print("[STREAMING] ✓ All streaming queries started successfully!")
    print("[STREAMING] Processing real-time CDR events...")
    print("[STREAMING] Press Ctrl+C to stop")
    
    # Wait for termination
    billing_query.awaitTermination()
    network_query.awaitTermination()
    console_query.awaitTermination()


if __name__ == "__main__":
    main()
