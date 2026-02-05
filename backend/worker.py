import pika
import os
import json
import time
from app import app, db, ClickLog 


time.sleep(10)

def callback(ch, method, properties, body):
    with app.app_context():
        data = json.loads(body)
        print(f" [Worker] Got the task: {data}")
        

        new_log = ClickLog(
            short_code=data['short_code'], 
            user_agent=data['user_agent']
        )
        db.session.add(new_log)
        db.session.commit()
        print(" [Worker] Saved to database")

def start_worker():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq')))
        channel = connection.channel()
        channel.queue_declare(queue='clicks_queue')
        
        print(' [*] Worker is running. Waiting for messages...')
        channel.basic_consume(queue='clicks_queue', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f"Worker connection error: {e}")

if __name__ == '__main__':
    start_worker()