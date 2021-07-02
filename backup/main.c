int id_1 = 4;
int id_2 = 10;
int id_3 = 15;
float prob_1 = 0.7;
float prob_2 = 0.25;
float prob_3 = 0.25;
int year = 21;
int month = 4;
int day = 23;
int hour = 18;
int min = 42;
int sec = 42;

#include "stdint.h"
#include "lmic.h"
#include "debug.h"
// application router ID (LSBF)
static const u1_t APPEUI[8]  = { 0x97, 0xFD, 0x03, 0xD0, 0x7E, 0xD5, 0xB3, 0x70 };

// unique device ID (LSBF)
static const u1_t DEVEUI[8]  = { 0x80, 0x7C, 0x8A, 0x32, 0x80, 0x5B, 0xDF, 0x00 };

// device-specific AES key (derived from device EUI)
static const u1_t DEVKEY[16] = { 0x7D, 0x2A, 0x30, 0xE4, 0x4C, 0x1D, 0xDF, 0x04, 0xB6, 0x8A, 0x2A, 0x6B, 0x82, 0x64, 0x04, 0x24 };

//////////////////////////////////////////////////
// APPLICATION CALLBACKS
//////////////////////////////////////////////////

// provide application router ID (8 bytes, LSBF)
void os_getArtEui (u1_t* buf) {
memcpy(buf, APPEUI, 8);
}

// provide device ID (8 bytes, LSBF)
void os_getDevEui (u1_t* buf) {
memcpy(buf, DEVEUI, 8);
}

// provide device key (16 bytes)
void os_getDevKey (u1_t* buf) {
memcpy(buf, DEVKEY, 16);
}


//////////////////////////////////////////////////
// MAIN - INITIALIZATION AND STARTUP
//////////////////////////////////////////////////

// initial job
static void initfunc (osjob_t* j) {
// intialize sensor hardware
//initsensor();
// reset MAC state
LMIC_reset();
// start joining
LMIC_startJoining();
// init done - onEvent() callback will be invoked...
}


// application entry point
int main () {
osjob_t initjob;

// initialize runtime env
os_init();
// initialize debug library
debug_init();
// setup initial job
os_setCallback(&initjob, initfunc);
// execute scheduled jobs and events
os_runloop();
// (not reached)
return 0;
}


//////////////////////////////////////////////////
// UTILITY JOB
//////////////////////////////////////////////////

static osjob_t reportjob;

// report sensor value every minute
static void reportfunc (osjob_t* j) {
// read sensor
u2_t id1 = id_1;
u2_t id2 = id_2;
u2_t id3 = id_3;
u8_t prob1 = prob_1*10;
u8_t prob2 = prob_2*10;
u8_t prob3 = prob_3*10;
u2_t year_t = year;
u2_t month_t = month;
u2_t day_t = day;
u2_t hour_t = hour;
u2_t min_t = min;
u2_t sec_t = sec;

// prepare and schedule data for transmission
LMIC.frame[0] = id1 >> 8;
LMIC.frame[1] = id1;
LMIC.frame[2] = id2 >> 8;
LMIC.frame[3] = id2;
LMIC.frame[4] = id3 >> 8;
LMIC.frame[5] = id3;
LMIC.frame[6] = prob1 >> 8;
LMIC.frame[7] = prob1;
LMIC.frame[8] = prob2 >> 8;
LMIC.frame[9] = prob2;
LMIC.frame[10] = prob3 >> 8;
LMIC.frame[11] = prob3;
LMIC.frame[12] = year_t >> 8;
LMIC.frame[13] = year_t;
LMIC.frame[14] = month_t >> 8;
LMIC.frame[15] = month_t;
LMIC.frame[16] = day_t >> 8;
LMIC.frame[17] = day_t;
LMIC.frame[18] = hour_t >> 8;
LMIC.frame[19] = hour_t;
LMIC.frame[20] = min_t >> 8;
LMIC.frame[21] = min_t;
LMIC.frame[22] = sec_t >> 8;
LMIC.frame[23] = sec_t;

//uint8_t message[4];
//uint16_t id1 = id_1;
//uint16_t id2 = id_2;
//uint16_t id3 = id_3;
//uint16_t prob1 = prob_1*10;
//uint16_t prob2 = prob_2*10;
//uint16_t prob3 = prob_3*10;
//uint8_t date_t = date;
//uint8_t time_t = time;
//message[0] = date_t >> 8;
//message[1] = date_t;
//message[2] = time_t >> 8;
//message[3] = time_t;
//message[4] = id1 >> 8;
//message[5] = id1;
//message[6] = id2 >> 8;
//message[7] = id2;
//message[8] = id3 >> 8;
//message[9] = id3;
//message[10] = prob1 >> 8;
//message[11] = prob1;
//message[12] = prob2 >> 8;
//message[13] = prob2;
//message[14] = prob3 >> 8;
//message[15] = prob3;
//message[12] = date_t >> 8;
//message[13] = date_t;
//message[14] = time_t >> 8;
//message[15] = time_t;

//LMIC_setTxData2(1, message, sizeof(message) - 1, 0);
LMIC_setTxData2(1, LMIC.frame, 24, 0); // (port 1, 2 bytes, unconfirmed)
// reschedule job in 60 seconds
os_setTimedCallback(j, os_getTime()+sec2osticks(30), reportfunc);
}


//////////////////////////////////////////////////
// LMIC EVENT CALLBACK
//////////////////////////////////////////////////

void onEvent (ev_t ev) {
debug_event(ev);

switch(ev) {

// network joined, session established
case EV_JOINED:
// switch on LED
debug_led(1);
// kick-off periodic sensor job
reportfunc(&reportjob);
break;
}
}
