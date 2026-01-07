"""
Real-time CDR Streaming Producer
Simulates real-time call events and sends to Kafka
"""
from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker()

class CDRStreamProducer:
    """Produces real-time CDR events to Kafka"""
    
    def __init__(self, kafka_broker='kafka:9092', topic='cdr-events'):
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_broker],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None
        )
        self.topic = topic
        self.tower_ids = ["TOWER_{:03d}".format(i) for i in range(1, 51)]
        
    def generate_event(self):
        """Generate a single CDR event"""
        call_type = random.choice(['VOICE', 'VOICE', 'VOICE', 'SMS', 'DATA'])
        
        event = {
            'call_id': fake.uuid4(),
            'caller_num': "+947{}".format(random.randint(10000000, 99999999)),
            'receiver_num': "+947{}".format(random.randint(10000000, 99999999)),
            'call_type': call_type,
            'duration_sec': random.randint(5, 1200) if call_type == 'VOICE' else 0,
            'timestamp': datetime.now().isoformat(),
            'tower_id': random.choice(self.tower_ids),
            'signal_strength': random.randint(1, 5),
            'event_time': datetime.now().isoformat()
        }
        return event
    
    def start_streaming(self, events_per_second=10, duration_minutes=None):
        """
        Start streaming CDR events
        Args:
            events_per_second: Number of events to generate per second
            duration_minutes: How long to stream (None = infinite)
        """
        print("[STREAMING] Starting CDR event stream...")
        print("[CONFIG] Rate: {} events/sec | Topic: {}".format(events_per_second, self.topic))
        
        start_time = time.time()
        event_count = 0
        
        try:
            while True:
                # Check duration
                if duration_minutes:
                    elapsed = (time.time() - start_time) / 60
                    if elapsed >= duration_minutes:
                        break
                
                # Generate and send event
                event = self.generate_event()
                
                # Use tower_id as partition key for better distribution
                self.producer.send(
                    self.topic,
                    key=event['tower_id'],
                    value=event
                )
                
                event_count += 1
                
                # Log progress every 100 events
                if event_count % 100 == 0:
                    print("[STREAMING] Sent {} events...".format(event_count))
                
                # Control rate
                time.sleep(1.0 / events_per_second)
                
        except KeyboardInterrupt:
            print("\n[STREAMING] Stopped by user")
        finally:
            self.producer.flush()
            self.producer.close()
            print("[STREAMING] Total events sent: {}".format(event_count))


def main():
    """Run streaming producer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CDR Streaming Producer')
    parser.add_argument('--rate', type=int, default=10, help='Events per second')
    parser.add_argument('--duration', type=int, default=None, help='Duration in minutes')
    parser.add_argument('--broker', type=str, default='localhost:9092', help='Kafka broker')
    
    args = parser.parse_args()
    
    producer = CDRStreamProducer(kafka_broker=args.broker)
    producer.start_streaming(
        events_per_second=args.rate,
        duration_minutes=args.duration
    )


if __name__ == "__main__":
    main()
