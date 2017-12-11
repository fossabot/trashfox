// The value of sensor is written on V1 virtual port on Blynk.cc

#include <Arduino.h>
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <SoftwareSerial.h>
#include "hcsr04.h"
#include "wisol_sigfox.h"

#define BLYNK_PRINT Serial

BlynkTimer timer;
SoftwareSerial  wisol_serial(D7,D8);

char auth[] = "954a64676b4147f9bf4246e581877828";
char ssid[] = "CASSINIguest";
char pass[] = "Cassini2016!";
char  sigfox_send_buf[12];

#ifdef __cplusplus
extern "C" {
#endif
    
    // This function tells Arduino what to do if there is a Widget
    // which is requesting data for Virtual Pin (5)
    void myTimerEvent()
    {
        // You can send any value at any time.
        // Please don't send more that 10 values per second.
        Blynk.virtualWrite(V1, HCSR04_get_data());
    }
    
    /** initialize software serial with proper timeouts */
    void wisol_sigfox__serial_init() {
        wisol_serial.begin(9600);
        wisol_serial.setTimeout(100);
    }
    
    /** adapter function for synchronous communication with module */
    void wisol_sigfox__serial_sync(const char *cmd, char *p_response_buf, int sz_response_buf, int timeout) {
        wisol_serial.setTimeout(timeout);
        wisol_serial.print(cmd); wisol_serial.print("\n");
        String s = wisol_serial.readStringUntil('\n');
        strncpy(p_response_buf, s.c_str(), sz_response_buf);
        int i = s.length()-1;
        while(i > 0 && (p_response_buf[i] == '\n' || p_response_buf[i] == '\r')) {
            p_response_buf[i--] = 0;
        }
    }
    
#ifdef __cplusplus
}
#endif

void setup() {
    //Blynk Begin
    Blynk.begin(auth, ssid, pass);
    // Timer is set to 15 sec/uplink
    timer.setInterval(1000L*15, myTimerEvent);
    Serial.begin(9600);
    HCSR04_setup();
    
    Serial.println("Initializing SigFox module...");
    
    // initialize serial communcaiton
    wisol_sigfox__serial_init();
    
    //
    if (wisol_sigfox__ready()) {
        Serial.println("Sigfox module is ready.");
        
        char buf[32];
        wisol_sigfox__get_id(buf);
        Serial.print("ID="); Serial.println(buf);
        
        //wisol_sigfox__get_pac(buf);
        //Serial.print("PAC="); Serial.println(buf);
        
        wisol_sigfox__get_firmware_version(buf, sizeof(buf));
        Serial.print("FirmwareVersion="); Serial.println(buf);
        
        wisol_sigfox__get_firmware_vcs_version(buf, sizeof(buf));
        Serial.print("FirmwareVCSVersion="); Serial.println(buf);
        
        wisol_sigfox__get_library_version(buf, sizeof(buf));
        Serial.print("LibraryVersion="); Serial.println(buf);
        
        //wisol_sigfox__set_power_level(9);
        //Serial.print("Output Power [dBm] "); Serial.println(wisol_sigfox__get_power_level());
        
    } else {
        Serial.println("Sigfox module is NOT ready.");
    }
}

void loop() {
    Blynk.run(); // Initates Blynk
    timer.run(); // Initiates BlynkTimer
    int distance = HCSR04_get_data();
    if ( distance != -1) {
        // got valid value, format. As of now, paste big endian int into buffer
        memset(sigfox_send_buf,0,sizeof(sigfox_send_buf));
        memcpy(sigfox_send_buf, &distance, sizeof(int));
        
        // and send it.
        Serial.print(distance);
        Serial.print(">");
        if (wisol_sigfox__send_frame((const uint8_t*)sigfox_send_buf, sizeof(int), false)) {
            Serial.println("sent.");
        } else {
            Serial.println("error!");
        }
    }
    if ( distance <= 6) {
        Blynk.notify(String("The fill rate: %100. Sensor val: ") + distance);
    } else if ( distance <= 8 && distance > 6) {
        Blynk.notify(String("The fill rate: %80. Sensor val: ") + distance);
    }
    delay(15000);
    // sleep 10 minutes
    //delay(1000*60*10);
}
