#ifndef __HCSR094_H
#define __HCSR04_H

// initialize pins for sensor
void HCSR04_setup();

// read distance from sensor. Return distance or -1 
// for invalid measurement.
int HCSR04_get_data();

#endif
