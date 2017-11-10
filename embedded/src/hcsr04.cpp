#include <Arduino.h>

// HC-SR04 ultra sound sensor pin definitions
const int trigPin = D6;
const int echoPin = D5;

int HCSR04_get_data();

void HCSR04_setup() {
  // attach a ultrasonic sensor
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
}

int HCSR04_get_data(){
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Reads the echoPin, returns the sound wave travel time in microseconds
  int duration = pulseIn(echoPin, HIGH);
  // invalid value? return -1;
  if ( duration > 10000) {
    return -1;
  }
  // Calculating the distance
  int distance= duration*0.034/2;
  return distance;
}
