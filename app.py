import queue
from flask import Flask, render_template, Response
import paho.mqtt.client as mqtt

app = Flask(__name__)

BROKER_IP = "10.2.172.120"
BROKER_PORT = 1883
DEFAULT_TOPIC = "#"

msg_queue = queue.Queue()

def on_connect(client, userdata, flags, rc):
    client.subscribe(DEFAULT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8", errors="replace")
    except Exception:
        payload = str(msg.payload)
    msg_queue.put(f"data: {msg.topic} | {payload}\n\n")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(BROKER_IP, BROKER_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Fout bij verbinden met broker: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    def event_stream():
        while True:
            message = msg_queue.get()
            yield message
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)