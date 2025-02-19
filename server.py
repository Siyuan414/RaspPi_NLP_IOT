from flask import Flask, request
import paho.mqtt.client as mqtt
from transformers import pipeline
import torch

app = Flask(__name__)

#MQTT setup 
mqtt_broker = "192.168.4.46"
mqtt_port = 1883
mqtt_topic = "home/led"
mqtt_client = mqtt.Client("jetson")

#connect to MQTT broker
mqtt_client.connect(mqtt_broker,mqtt_port,60)

#use GPU
device = 0 if torch.cuda.is_available() else -1
#load pre-trained NLP model
nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli",device=device)

#Http route to receive text command
@app.route('/command',methods=['POST'])
def handle_command():
	data = request.get_json()
	print(data)
	text_command = data['command']
	#use NLP to process the command and classify it 
	labels = ["red","blue","temperature","on","off"]
	result = nlp(text_command,candidate_labels=labels)

	#get action from NLP model
	action = result['labels']

	if "red" in action and "on" in action:
		mqtt_client.publish(f"{mqtt_topic}/red","ON")
		return "RED LED TURNED ON" ,200
	elif "red" in action and "off" in action:
		mqtt_client.publish(f"{mqtt_topic}/red","OFF")
		return "RED LED TURNED ON" ,200
	elif "blue" in action and "on" in action:
		mqtt_client.publish(f"{mqtt_topic}/blue","ON")
		return "RED LED TURNED ON" ,200
	elif "blue" in action and "off" in action:
		mqtt_client.publish(f"{mqtt_topic}/blue","OFF")
		return "RED LED TURNED ON" ,200
	elif "temperature" in action:
		mqtt_client.publish("home/temperature","GET")
		return "Requesting temperature data" ,200
	else:
		return "Invalid command",400

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=8000,debug=True)

