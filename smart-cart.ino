#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <MFRC522v2.h>
#include <MFRC522DriverSPI.h>
#include <MFRC522DriverPinSimple.h>
#include <MFRC522Debug.h>

const char* ssid = "<YOUR_WIFI_SSID>";
const char* password = "<YOUR_WIFI_PASSWORD>";

const char* serverUrl = "<SERVER_URL>";

MFRC522DriverPinSimple ss_pin(15);
MFRC522DriverSPI driver{ss_pin};
MFRC522 mfrc522{driver};

void setup() {
  Serial.begin(115200);
  while (!Serial);

  WiFi.begin(ssid, password);
  Serial.print("\nConnecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
  Serial.print("ESP8266 MAC Address: ");
  Serial.println(WiFi.macAddress());

  mfrc522.PCD_Init();
  Serial.println(F("Scan PICC to see UID and send to server...\n"));
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uidStr = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uidStr += String(mfrc522.uid.uidByte[i], HEX);
  }

  String macAddr = WiFi.macAddress();

  Serial.println("Card(item) detected!");
  Serial.println("UID(item_id): " + uidStr);
  Serial.println("MAC(cart_id): " + macAddr);

  sendPostRequest(uidStr, macAddr);

  Serial.println();

  delay(2000);
}

void sendPostRequest(String uid, String mac) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"item_id\":\"" + uid + "\",\"cart_id\":\"" + mac + "\"}";
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("POST request sent, response code: ");
      Serial.println(httpResponseCode);
      Serial.println(http.getString());
    } else {
      Serial.print("Error sending POST request: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}
