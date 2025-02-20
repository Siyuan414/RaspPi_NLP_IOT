import requests
import json

url = "http://192.168.4.46:8000/command"
headers = {'Content-Type': 'application/json'}
data = {'command': 'turn off red LED'}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
