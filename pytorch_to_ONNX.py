import torch 
from transformers import AutoModelForSequenceClassification, AutoTokenizer

#load model
model_name = "facebook/bart-large-mnli"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

input_text = "This is a sample input"
inputs = tokenizer(input_text,return_tensors="pt")

#convert to ONNX
onnx_file = "bart-large-mnli.onnx"
torch.onnx.export(model,
		(inputs['input_ids'],),
		onnx_file,
		input_names=['input_ids'],
		output_names=['output'])
print("model converted to onnx file")
