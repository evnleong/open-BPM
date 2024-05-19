#include <Arduino_LoRaWAN_ttn.h>
#include <lmic.h>
#include <hal/hal.h>
#include "keys.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define BUTTON_A  10
#define BUTTON_B  9
#define BUTTON_C  5
#define WIRE Wire

Adafruit_SSD1306 display = Adafruit_SSD1306(128, 32, &WIRE);

uint64_t lastTime = 0;
uint32_t bufferLength = 8;
static uint8_t messageBuffer[8] = {0, 1, 2, 3, 4, 5, 6, 7};
const int numChars =14;

struct __attribute__((__packed__)) CustomDataType {
  float systolic; 
  float diastolic; 
};

CustomDataType mydata;

#ifdef __cplusplus
extern "C"{
#endif

#ifdef __cplusplus 
}
#endif

//Callback for SendBuffer
void myStatusCallback(void * data, bool success){
  if(success){
    // Serial.println("Succeeded!");
    // display.clearDisplay();
    // display.setCursor(0,0);
    // display.println("Packet \nSent!");
    // display.display();
    // delay(500);
  }
  else{
    // display.clearDisplay();
    // display.setCursor(0,0);
    // display.println("Packet \nFailed!");
    // display.display();
    // delay(500);
    // Serial.println("Failed!");
  }
  
}

void initDisplay(){
    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    display.display();
    delay(1000);
    display.clearDisplay();
    display.display();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);
    display.display();
}


class cMyLoRaWAN : public Arduino_LoRaWAN_ttn {
public:
    cMyLoRaWAN() {};

protected:
    // you'll need to provide implementations for each of the following.
    virtual bool GetOtaaProvisioningInfo(Arduino_LoRaWAN::OtaaProvisioningInfo*) override;
    virtual void NetSaveSessionInfo(const SessionInfo &Info, const uint8_t *pExtraInfo, size_t nExtraInfo) override;
    virtual void NetSaveSessionState(const SessionState &State) override;
    virtual bool NetGetSessionState(SessionState &State) override;
    virtual bool GetAbpProvisioningInfo(Arduino_LoRaWAN::AbpProvisioningInfo*) override;

};

// set up the data structures.
cMyLoRaWAN myLoRaWAN {};

// The pinmap. This form is convenient if the LMIC library
// doesn't support your board and you don't want to add the
// configuration to the library (perhaps you're just testing).
// This pinmap matches the FeatherM0 LoRa. See the arduino-lmic
// docs for more info on how to set this up.
const cMyLoRaWAN::lmic_pinmap myPinMap = {
     .nss = 8,
     .rxtx = cMyLoRaWAN::lmic_pinmap::LMIC_UNUSED_PIN,
     .rst = 4,
     .dio = { 3, 6, cMyLoRaWAN::lmic_pinmap::LMIC_UNUSED_PIN },
     .rxtx_rx_active = 0,
     .rssi_cal = 0,
     .spi_freq = 8000000,
};

float PressureMin = 0;
float PressureMax = 140;
float Vsupply = 3;
float half = Vsupply / 2;


float volta = 0;
int i;
float maxvolt = 0;
float volt = 0;
float pressure = 0;
float MAP = 0;
float maxv = 0;
float vtotal = 0;
float vfinal;
int validated = 0;

volatile float sys;
volatile float dias;

void setup() {
  // put your setup code here, to run once:
  //lcd.begin(16, 2);
  Serial.begin(115200);
  pinMode(3, OUTPUT);
  initDisplay();
  myLoRaWAN.begin(myPinMap);
  lastTime = millis();

  if(myLoRaWAN.IsProvisioned())
      Serial.println("Provisioned for something");
  else
      Serial.println("Not provisioned.");
      //LMIC.datarate = 10;
   
  myLoRaWAN.SendBuffer((uint8_t*)&mydata, sizeof(mydata), myStatusCallback, NULL, false, 1);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(3, HIGH);
  for(i = 0; i < 40; i = i + 1){
    volta = analogRead(A0);
    volt = (volta * Vsupply) / (pow(2, 10) - 1);
    //Serial.println(volt);
    // maxv = max(abs(volt-half), maxvolt);
    // maxvolt = abs(maxv-half);
    vtotal += volt;
    delay(250);

  }
  vfinal = vtotal / 40;
  vtotal = 0;

  // Serial.print("v Average:");
  // Serial.println(vfinal);
  pressure = (((volt) - 0.1)/((1)/(PressureMax - PressureMin))) + PressureMin;

  digitalWrite(3, LOW);
  display.clearDisplay();
  display.setCursor(0,0);
  display.display();
  
  Serial.println("");
  Serial.print("MAP: ");
  Serial.println(pressure);
  Serial.print("Systolic: ");
  sys = pressure*1.1;
  display.print("Sys:"), display.println(pressure*1.1);
  Serial.println(pressure * 1.1);
  dias = pressure *.9;
  display.print("Dia:"), display.println(pressure*.9);
  Serial.print("Diastolic: ");
  Serial.println(pressure * 0.9);
  display.display();
  delay(500);


  if ((pressure*1.1 < 140 ) && (pressure*1.1 > 80)){
    validated++; 
  }
  int tries = 0;

mydata.systolic= sys;
mydata.diastolic= dias;
if (validated >2){
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("Sending..."),display.print(sys), display.print(","),display.println(dias);
  display.display();
  while (tries < 3) {
   myLoRaWAN.loop();
    //memcpy(mydata.mystring, mystring.c_str(), 6);
   if (millis() - lastTime > 8000){//waits 10 seconds between transmissions
    //block until serial message received
    messageBuffer[0]++;
    myLoRaWAN.SendBuffer((uint8_t*)&mydata, sizeof(mydata), myStatusCallback, NULL, false, 1);
    lastTime = millis();
    tries++;
   }
   validated = 0; 
  }
}
}

bool
cMyLoRaWAN::GetOtaaProvisioningInfo(
    OtaaProvisioningInfo *pInfo
    ) {
      if (pInfo){
        memcpy_P(pInfo->AppEUI, APPEUI, 8);
        memcpy_P(pInfo->DevEUI, DEVEUI, 8);
        memcpy_P(pInfo->AppKey, APPKEY, 16);
      }
    return true;
}

void
cMyLoRaWAN::NetSaveSessionInfo(
    const SessionInfo &Info,
    const uint8_t *pExtraInfo,
    size_t nExtraInfo
    ) {
    // save Info somewhere.
}

void
cMyLoRaWAN::NetSaveSessionState(const SessionState &State) {
    // save State somwwhere. Note that it's often the same;
    // often only the frame counters change.
}

bool
cMyLoRaWAN::NetGetSessionState(SessionState &State) {
    // either fetch SessionState from somewhere and return true or...
    return false;
}

bool
cMyLoRaWAN::GetAbpProvisioningInfo(Arduino_LoRaWAN::AbpProvisioningInfo* Info){
  //either get ABP provisioning info from somewhere and return true or...
  return false;
}
