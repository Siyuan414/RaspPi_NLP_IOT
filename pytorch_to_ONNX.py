import torch 
from transformers import MobileBertForSequenceClassification, MobileBertTokenizer

#load model
model_name = "google/mobilebert-uncased"
model = MobileBertForSequenceClassification.from_pretrained(model_name)
tokenizer = MobileBertTokenizer.from_pretrained(model_name)

input_text = "This is a sample input"
inputs = tokenizer(input_text,return_tensors="pt")

#convert to ONNX
onnx_file = "C:\\Users\\siyua\\Desktop\\RaspPi_NLP_IOT\\mobilebert-uncased.onnx"

torch.onnx.export(model,
		(inputs['input_ids'],),
		onnx_file,
		input_names=['input_ids'],
		output_names=['output'])
print("model converted to onnx file")
