import os
import string
import random
import redis
import pika 
import json
import datetime
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Redis
redis_url = os.getenv('REDIS_URL')
if redis_url:
    r = redis.from_url(redis_url, decode_responses=True)
else:
    r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, decode_responses=True)

def send_to_queue(message):
    try:

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq')))
        channel = connection.channel()

        channel.queue_declare(queue='clicks_queue')

        channel.basic_publish(exchange='', routing_key='clicks_queue', body=json.dumps(message))
        connection.close()
    except Exception as e:
        print(f"Error sending to RabbitMQ: {e}")

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)


class ClickLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_agent = db.Column(db.String(200))

with app.app_context():
    db.create_all()

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')
    if not original_url: return jsonify({"error": "URL required"}), 400

    code = generate_short_code()
    new_link = Link(original_url=original_url, short_code=code)
    db.session.add(new_link)
    db.session.commit()
    r.set(f"clicks:{code}", 0)
    
    return jsonify({"short_code": code, "full_short_url": f"http://localhost:5000/{code}"})

@app.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    link = Link.query.filter_by(short_code=short_code).first()
    if link:

        r.incr(f"clicks:{short_code}")


        log_data = {
            "short_code": short_code,
            "user_agent": request.headers.get('User-Agent', 'unknown'),
            "timestamp": str(datetime.datetime.now())
        }
        send_to_queue(log_data)

        return redirect(link.original_url)
    else:
        return "URL not found", 404

@app.route('/stats/<short_code>', methods=['GET'])
def get_stats(short_code):

    link = Link.query.filter_by(short_code=short_code).first()
    if link:
        clicks = r.get(f"clicks:{short_code}")
        return jsonify({"original_url": link.original_url, "clicks": clicks if clicks else 0})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)