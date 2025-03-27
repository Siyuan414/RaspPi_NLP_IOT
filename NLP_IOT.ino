#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <DHT.h>
#include <PubSubClient.h>  // MQTT Library

#define RED_LED_PIN 13
#define BLUE_LED_PIN 12
#define DHT_PIN 27
#define DHT_TYPE DHT22

const char *ssid = "SD4418";  // Wi-Fi SSID
const char *password = "zsy1234567890";  // Wi-Fi Password

// MQTT broker details
const char *mqttServer = "192.168.4.46";  // Replace with your MQTT broker address
const int mqttPort = 1883;  // Default MQTT port
const char *mqttUser = "";  // MQTT username (if needed)
const char *mqttPassword = "";  // MQTT password (if needed)

// MQTT topics for LED control and temperature
const char *ledRedTopic = "home/led/red";
const char *ledBlueTopic = "home/led/blue";
const char *temperatureTopic = "home/temperature";

// Create instances for DHT and MQTT client
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

AsyncWebServer server(80);

// Function to reconnect to the MQTT broker
void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect("ESP32Client", mqttUser, mqttPassword)) {
      Serial.println("connected");
      mqttClient.subscribe(ledRedTopic);  // Subscribe to LED control topic
      mqttClient.subscribe(ledBlueTopic);  // Subscribe to LED control topic
      mqttClient.subscribe(temperatureTopic);
      mqttClient.subscribe("home/temperature/request");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize DHT sensor and LEDs
  dht.begin();
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);

  // Set up MQTT client
  mqttClient.setServer(mqttServer, mqttPort);
  mqttClient.setCallback(mqttCallback);

  // Define routes to control LEDs through HTTP
  server.on("/led/red/on", HTTP_GET, [](AsyncWebServerRequest *request) {
    digitalWrite(RED_LED_PIN, HIGH);
    mqttClient.publish(ledRedTopic, "ON");  // Publish status to MQTT
    request->send(200, "text/plain", "Red LED turned on");
  });

  server.on("/led/red/off", HTTP_GET, [](AsyncWebServerRequest *request) {
    digitalWrite(RED_LED_PIN, LOW);
    mqttClient.publish(ledRedTopic, "OFF");  // Publish status to MQTT
    request->send(200, "text/plain", "Red LED turned off");
  });

  server.on("/led/blue/on", HTTP_GET, [](AsyncWebServerRequest *request) {
    digitalWrite(BLUE_LED_PIN, HIGH);
    mqttClient.publish(ledBlueTopic, "ON");  // Publish status to MQTT
    request->send(200, "text/plain", "Blue LED turned on");
  });

  server.on("/led/blue/off", HTTP_GET, [](AsyncWebServerRequest *request) {
    digitalWrite(BLUE_LED_PIN, LOW);
    mqttClient.publish(ledBlueTopic, "OFF");  // Publish status to MQTT
    request->send(200, "text/plain", "Blue LED turned off");
  });

  // Define route to get temperature data
  server.on("/temperature", HTTP_GET, [](AsyncWebServerRequest *request) {
    float temp = dht.readTemperature();
    if (isnan(temp)) {
      request->send(500, "text/plain", "Failed to read temperature");
    } else {
      String tempStr = String(temp);
      mqttClient.publish(temperatureTopic, tempStr.c_str());  // Publish temperature to MQTT
      request->send(200, "text/plain", "Room Temperature: " + tempStr + " °C");
    }
  });

  // Start the server
  server.begin();
}

void loop() {
  if (!mqttClient.connected()) {
    reconnect();  // Ensure the MQTT client stays connected
  }
  mqttClient.loop();  // Continuously handle MQTT communication
}

// MQTT callback function for handling received messages
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Convert payload to string for processing
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Received message on topic: ");
  Serial.print(topic);
  Serial.print(" - Message: ");
  Serial.println(message);

  // Example: If message is "ON" or "OFF", control LEDs accordingly
  if (String(topic) == ledRedTopic) {
    if (message == "ON") {
      digitalWrite(RED_LED_PIN, HIGH);
    } else if (message == "OFF") {
      digitalWrite(RED_LED_PIN, LOW);
    }
  }
  else if (String(topic) == ledBlueTopic) {
    if (message == "ON") {
      digitalWrite(BLUE_LED_PIN, HIGH);
    } else if (message == "OFF") {
      digitalWrite(BLUE_LED_PIN, LOW);
    }
  }
  else if (String(topic) == "home/temperature/request") {  
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
      String tempStr = String(temp);
      mqttClient.publish(temperatureTopic, tempStr.c_str());  
      Serial.println("Sent temperature: " + tempStr);
    } else {
      Serial.println("Failed to read temperature");
    }
  }
}
