import sounddevice as sd
import numpy as np
import wave
import whisper
import paho.mqtt.client as mqtt

# 1. Record audio
def record_audio(filename="recorded.wav", duration=5, samplerate=16000):
    print("Recording... Speak now!")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    
    # Save to file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())

    print(f"Recording saved as {filename}")

# 2. Transcribe audio with Whisper
def transcribe_audio(audio_file="recorded.wav"):
    model = whisper.load_model("base")
    print("Transcribing...")
    result = model.transcribe(audio_file)
    return result["text"]

# 3. Process the command
def process_command(text):
    text = text.lower()

    if "red led" in text and "on" in text:
        return "RED_ON"
    elif "red led" in text and "off" in text:
        return "RED_OFF"
    elif "blue led" in text and "on" in text:
        return "BLUE_ON"
    elif "blue led" in text and "off" in text:
        return "BLUE_OFF"
    elif "temperature" in text:
        return "TEMP"
    else:
        return "UNKNOWN"

# 4. Send command to ESP32 via MQTT
def send_mqtt_command(command):
    broker = "your_jetson_ip"  # Replace with Jetson Nano IP
    port = 1883  # MQTT port
    topic = "home/led_control"  # MQTT topic for controlling LEDs

    client = mqtt.Client()
    client.connect(broker, port, 60)

    client.publish(topic, command)
    print(f"Sent command: {command}")
    client.disconnect()

# Main flow
def main():
    record_audio()  # Record audio
    text = transcribe_audio()  # Transcribe speech to text
    print("You said:", text)

    command = process_command(text)  # Process the command
    print("Detected command:", command)

    if command != "UNKNOWN":
        send_mqtt_command(command)  # Send command to ESP32
    else:
        print("Command not recognized.")

if __name__ == "__main__":
    main()
