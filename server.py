from flask import Flask, request
import paho.mqtt.client as mqtt
from transformers import pipeline,AutoTokenizer
import torch
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np

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
TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
with open('bart-large-mnli.trt', 'rb') as f:
    engine_data = f.read()
    runtime = trt.Runtime(TRT_LOGGER)
    engine = runtime.deserialize_cuda_engine(engine_data)

context = engine.create_execution_context()

# Prepare input and output buffers
input_shape = (1, 512)
output_shape = (1, 3)
input_data = np.random.random(input_shape).astype(np.float32)
output_data = np.zeros(output_shape, dtype=np.float32)

d_input = cuda.mem_alloc(input_data.nbytes)
d_output = cuda.mem_alloc(output_data.nbytes)
bindings = [int(d_input), int(d_output)]
stream = cuda.Stream()

def run_inference(text):
    """Run inference using TensorRT model."""
    # Tokenize input
    inputs = tokenizer(text, return_tensors="np", padding="max_length", truncation=True, max_length=512)
    input_ids = inputs["input_ids"].astype(np.float32)

    # Copy data to GPU
    cuda.memcpy_htod_async(d_input, input_ids, stream)
    
    # Run inference
    context.execute_async_v2(bindings, stream.handle, None)
    
    # Copy results back to CPU
    cuda.memcpy_dtoh_async(output_data, d_output, stream)
    stream.synchronize()
    
    return output_data[0]  # Assuming single batch output

#Http route to receive text command
@app.route('/command',methods=['POST'])
def handle_command():
	data = request.get_json()
	print(data)
	text_command = data['command']
	#use NLP to process the command and classify it 
	labels = ["red","blue","temperature","on","off"]
	logits = run_inference(text_command)

	#get action from NLP model
	action = labels[np.argmax(logits)]

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

