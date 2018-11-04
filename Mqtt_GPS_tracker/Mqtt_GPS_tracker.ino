#define TINY_GSM_MODEM_SIM900

#include <PubSubClient.h>
#include <TinyGsmClient.h>
#include <SoftwareSerial.h>
#include <TinyGPS.h>

float latitude, longitude;

// Your GPRS credentials
// Leave empty, if missing user or pass
const char apn[]  = "djezzy.internet";
const char user[] = "";
const char pass[] = "";

char data[50];

SoftwareSerial SerialAT(7, 8); // RX, TX
SoftwareSerial gpSerial(2, 3);
TinyGPS gps;
TinyGsm modem(SerialAT);
TinyGsmClient client(modem);
PubSubClient mqtt(client);

const char* broker = "broker.hivemq.com";//"iot.eclipse.org"
const char* topic_GPS = "Tracker/coord";
static char lati[10], longi[10];
int speed = 44;
int alt = 1000;

long lastReconnectAttempt = 0;
 
 
void reconnect() {
  // Loop until we're reconnected
  while (!mqtt.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (mqtt.connect("oha")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
 
void setup()
{
  // Set console baud rate
  Serial.begin(115200);
  delay(1000);

  gpSerial.begin(9600); // port de comunication avec le capteur GPS
  delay(1000);

  // Set GSM module baud rate
  SerialAT.begin(115200);
  delay(3000);

  Serial.println("Initializing modem...");
  modem.restart();

  String modemInfo = modem.getModemInfo();
  Serial.print("Modem: ");
  Serial.println(modemInfo);

  Serial.print("Waiting for network...");
  while (!modem.waitForNetwork()) {
    Serial.println(" fail");
    while (true);
  }
  Serial.println(" OK");

  Serial.print("Connecting to ");
  Serial.print(apn);

  if (!modem.gprsConnect(apn, user, pass)) {
    Serial.println("fail");
    while (true);
  }

  Serial.println("OK");
  
   
  mqtt.setServer(broker, 1883);
  delay(1500);
}
 
void loop()
{
  if (!mqtt.connected()) {
    reconnect();
  }
  mqtt.loop();
  gpSerial.listen();
  while (gpSerial.available()) {
    if (gps.encode(gpSerial.read())) {
      gps.f_get_position(&latitude, &longitude); // get latitude and longitude
      Serial.print(latitude);
      Serial.print(",");
      Serial.println(longitude);
      delay(1000);

      dtostrf(latitude, 8, 5, lati);
      dtostrf(longitude, 8, 5, longi);
      sprintf(data, "%s,%s,%d,%d", lati, longi, speed, alt);
      mqtt.publish(topic_GPS, data);
      Serial.println(data);
      Serial.println(sizeof (data));
      
  }
}
}
