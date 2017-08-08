// Required for i2c connection
#include <Wire.h>
// Required for OneWire
#include <OneWire.h> 
#include <DallasTemperature.h>

// Define i2c slave address
#define SLAVE_ADDRESS 0x04
// Pin 2 for DS18B20 
#define ONE_WIRE_BUS 2 
// Floats being sent
#define FLOATS_SENT 2

// Define variable for data received
// 1 = DS18B20 reading
int indata = 0;
// Variable for temperature
float temperature = 0.0;
// Variable for output data
// index 0 will be sensor code (1.0 = DS18B20)
// index 1 will be the value
float data[FLOATS_SENT];

// Setup a oneWire instance to communicate with any OneWire devices  
OneWire oneWire(ONE_WIRE_BUS); 
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

void setup()
{
 Serial.begin(9600);
 Wire.begin(SLAVE_ADDRESS);
 Wire.onReceive(receiveData);
 Wire.onRequest(sendData);
 Serial.println("Ready!");
 // Start up the onewire library
 sensors.begin();
}

void loop()
{
 delay(100);
}

// callback for received data
void receiveData(int byteCount)
{
 while(Wire.available())
 {
  indata = Wire.read();
  if (indata == 1)
  {
   sensors.requestTemperatures();
   temperature = sensors.getTempCByIndex(0);
   data[0] = 1.0;
   data[1] = temperature;
  }
  else
  {
  }
 }
}

void sendData()
{
 Wire.write((byte*) &data[0], FLOATS_SENT*sizeof(float));
 data[0] = 0.0;
 data[1] = 0.0;
}

