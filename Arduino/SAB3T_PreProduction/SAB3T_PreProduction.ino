// SAB3T - PID Loop Educational Tool
// Follow my project on Hackaday.io: https://hackaday.io/project/6917-sab3t-pid-loop-educational-tool
// by Tim Giles 
//    www.wildcircuits.com
//    @wildcircuits
//    https://www.etsy.com/shop/timogiles

//7-26-2015: This is a mess, will clean up later

//8-5-2015: Changes preparing for HackadayPrize Best Product entry.
// - I haven't cleaned anything up yet.  
// - Swapping location of the X and Y servos to make wiring more logical using new interface board.
// - Adding EEPROM storage of servo center values.


#include <Servo.h> 
#include <math.h>
#include <stdint.h>
#include "TouchScreen.h"
#include <EEPROM.h>

#define YP A3  // must be an analog pin, use "An" notation! rec
#define XM A0  // must be an analog pin, use "An" notation! black
#define YM A1  // can be a digital pin                      green
#define XP A2  // can be a digital pin                      white

// For better pressure precision, we need to know the resistance
// between X+ and X- Use any multimeter to read it
// For the one we're using, its 300 ohms across the X plate
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 230);

//declare 2 servos 
Servo ServoA;  
Servo ServoB;  
int ServoAval = 1400;
int ServoBval = 1400;
int ServoA_Center = 1400;
int ServoB_Center = 1400;
int ResetCounter = 0;
int Xerror_last;
int Yerror_last;
double Xerror_int;
double Yerror_int;
double Xave;
double Yave;
double aveCount;
int   angle = 0;
int Target_X;
int Target_Y;
int Target_X_last;
int Target_Y_last;
int Target_X_Clast;
int Target_Y_Clast;
int Xdiff;
int Ydiff;
int Xpos;
int Ypos;
int XposLast;
int YposLast;
unsigned long time_millis;
unsigned long update_millis;
int phase = 1;
int dataValid;

//serial interace variables
char SerialBuffer[24];
int SerialBufferIndex = 0;
int inByte = 0;
int LoopWaitTime = 0;
int Kp;
int Kd;
int Ki;
int Kf;

boolean RunCircle = false;

void setup() 
{ 
  //assign the pins that the servos are connected to
  ServoA.attach(10);
  ServoB.attach(9);

  //initialize serial communications
  Serial.begin(38400);
  
  //check the EEPROM to see if a valid servo center exists
  dataValid = EEPROM.read(0);
  if (dataValid == 1){
    ServoA_Center = 10* EEPROM.read(1);
    ServoAval = ServoA_Center;
    ServoB_Center = 10* EEPROM.read(2);
    ServoBval = ServoB_Center;
  }else{
    //init servo values
    ServoAval = 1500;//1630;
    ServoA_Center = 1500;//1630;
    ServoBval = 1500;//1670;
    ServoB_Center = 1500;//1670;  
  }
  angle = 0;
  
  //init target for center
  Target_X = 500;
  Target_Y = 500;
  Xerror_last = 0;
  Yerror_last = 0;
  Xerror_int = 0;
  Yerror_int = 0;
  time_millis = millis();
  update_millis = millis();
  phase = 1;
  
  //default PID settings
  Kp = 10;
  Kd = 10;
  Ki = 2;
  Kf = 1;

  Xave = 0;
  Yave = 0;
  aveCount = 0;
  LoopWaitTime = 5000;

  RunCircle = false;
//print serial headers  
/*
    Serial.print('aveCount');
    Serial.print(',');
    Serial.print('Target_X');
    Serial.print(',');
    Serial.print('Target_Y');
    Serial.print(',');
    Serial.print('int(Xave/aveCount)');
    Serial.print(',');
    Serial.print('int(Yave/aveCount)');
    Serial.print(',');
    Serial.print('Xerror');
    Serial.print(',');
    Serial.print('Yerror');
    Serial.print(',');
    Serial.print('Xdiff');
    Serial.print(',');
    Serial.print('Ydiff');
    Serial.print(',');
    Serial.print('Xerror_int');
    Serial.print(',');
    Serial.print('Yerror_int');
    Serial.print(',');
    Serial.print('Xangle');
    Serial.print(',');
    Serial.print('Yangle');
    Serial.print(',');
    Serial.print('Xshift');
    Serial.print(',');
    Serial.println('Yshift');
    */
} 
 
void loop() 
{ 
  //manage the serial communications
  while(Serial.available() > 0) {

    //read character
    inByte = Serial.read();
    
    //is CR or LF?
    if ((inByte == 10) || (inByte == 13)){
      //Execute whatever command has been recieved
      int Valid = SerialCommander();
      Serial.println(" ");
      //if it was a valid command return the prompt, otherwise ? prompt
      if (Valid == 1){
        Serial.print(">");      
      }else{
        Serial.print("?>");      
      }
      //clear buffer
      SerialBufferIndex = 0;
      SerialBuffer[0] = ' ';
      SerialBuffer[1] = ' ';      
      SerialBuffer[2] = ' ';
      SerialBuffer[3] = ' ';
      SerialBuffer[4] = ' ';
      SerialBuffer[5] = ' ';
      SerialBuffer[6] = ' ';
      SerialBuffer[7] = ' ';
      SerialBuffer[8] = ' ';
      SerialBuffer[9] = ' ';
      SerialBuffer[10] = ' ';
      SerialBuffer[11] = ' ';
      SerialBuffer[12] = ' ';      
      SerialBuffer[13] = ' ';
      SerialBuffer[14] = ' ';      
      SerialBuffer[15] = ' ';      
      SerialBuffer[16] = ' ';
      SerialBuffer[17] = ' ';
      SerialBuffer[18] = ' ';
      SerialBuffer[19] = ' ';
      SerialBuffer[20] = ' ';      
      SerialBuffer[21] = ' ';
      SerialBuffer[22] = ' ';      
      SerialBuffer[23] = ' ';      
    }
    //store the recieved character
    else{
      SerialBuffer[SerialBufferIndex] = inByte;
      SerialBufferIndex += 1;
      Serial.print(char(inByte));
    }
  }
  
  //if Servo Center values are valid in EEPROM or have been updated to EEPROM, light the Arduino's LED for indication
  if (dataValid ==1){
    digitalWrite(13,HIGH);
  }else{
    digitalWrite(13,LOW);
  }
  
  //read touchscreen
  // a point object holds x y and z coordinates
  TSPoint p = ts.getPoint();
  if (p.z > ts.pressureThreshhold){
    Xave += p.x;
    Yave += p.y;
    aveCount += 1;
  }
    
// we have some minimum pressure we consider 'valid'
// pressure of 0 means no pressing!
  if ((p.z > ts.pressureThreshhold) and ((millis() -update_millis) > 33)){
    update_millis = millis();
    
    //CALCULATE THE TABLE ANLGE
    double Yangle = (ServoAval - ServoA_Center + ServoBval - ServoB_Center)/11;
    double Xangle = double(ServoAval - ServoA_Center - ServoBval + ServoB_Center)/11;
    double screenliftradius = 0.635;
    //    x axis is 58% of Y axis
    //x active area = 3.5"
    int Xshift = int(181*sin(radians(Xangle)));
    int Yshift = int(97*sin(radians(Yangle)));
    //balance!
//    Serial.print(Xshift);
//    Serial.print(" ");
//    Serial.println(Xangle);
    XposLast = Xpos;
    YposLast = Ypos;
    Xpos = int(Xave/aveCount);
    Ypos = int(Yave/aveCount);
    int Xvel = Xpos - XposLast;
    int Yvel = Ypos - YposLast;
    int Xerror = (Xpos - Target_X)*.6 + Xshift/3;
    int Yerror = Ypos - Target_Y - Yshift/3;
    Xdiff = Xerror-Xerror_last + (Target_X-Target_X_last);
    Ydiff = Yerror-Yerror_last + (Target_Y-Target_Y_last)  ;
    int FutureX = int((Xvel * Kf) + Xpos);
    int FutureY = int((Yvel * Kf) + Ypos);
    int XerrorFut = (FutureX - Target_X)*.6 + Xshift/3;
    int YerrorFut = FutureY - Target_Y - Yshift/3;
    
    
//  if xerror is >0 then servoa-, servob-
//  if yerror is >0 then servoa-, servob+
//    int Kp = 48; 0x30
//    int Kd = 20; 0x14
//    int Ki = 02; 0x02
    ServoAval = ServoA_Center + ((Kp*XerrorFut)/60 + (Xdiff*Kd)/5 + int((Xerror_int*Ki)/500)) - ((Kp*YerrorFut)/60 + (Ydiff*Kd)/5 + int((Yerror_int*Ki)/500));
    ServoBval = ServoB_Center - ((Kp*XerrorFut)/60 + (Xdiff*Kd)/5 + int((Xerror_int*Ki)/500)) - ((Kp*YerrorFut)/60 + (Ydiff*Kd)/5 + int((Yerror_int*Ki)/500));
    ResetCounter = 0; 
    Xerror_last = Xerror;
    Yerror_last = Yerror;
    Xerror_int += double(Xerror)/2;
    Yerror_int += double(Yerror)/2;
    Target_X_last = Target_X;
    Target_Y_last = Target_Y;
    
    Serial.print(aveCount);
    Serial.print(',');
    Serial.print(Target_X);
    Serial.print(',');
    Serial.print(Target_Y);
    Serial.print(',');
    Serial.print(Xpos);
    Serial.print(',');
    Serial.print(Ypos);
    Serial.print(',');
    Serial.print(FutureX);
    Serial.print(',');
    Serial.print(FutureY);
    Serial.print(',');
    Serial.print(Xerror);
    Serial.print(',');
    Serial.print(Yerror);
    Serial.print(',');
    Serial.print(Xdiff);
    Serial.print(',');
    Serial.print(Ydiff);
    Serial.print(',');
    Serial.print(Xerror_int);
    Serial.print(',');
    Serial.print(Yerror_int);
    Serial.print(',');
    Serial.print(int(Xangle));
    Serial.print(',');
    Serial.print(int(Yangle));
    Serial.print(',');
    Serial.print(Xshift);
    Serial.print(',');
    Serial.println(Yshift);
    
/*
    Serial.print(aveCount);
    Serial.print(',');
    Serial.print(Target_X);
    Serial.print(',');
    Serial.print(Target_Y);
    Serial.print(',');
    Serial.print(int(Xave/aveCount));
    Serial.print(',');
    Serial.print(int(Yave/aveCount));
    Serial.print(',');
    Serial.print(int(Xerror));
    Serial.print(',');
    Serial.print(int(Yerror));
    Serial.print(',');
    Serial.print(int(Xdiff));
    Serial.print(',');
    Serial.print(int(Ydiff));
    Serial.print(',');
    Serial.print(int(Xerror_int));
    Serial.print(',');
    Serial.println(int(Yerror_int));
*/
    aveCount = 0;
    Xave = 0;
    Yave = 0;
    

  }


  SetServoA(ServoAval);
  SetServoB(ServoBval);  
  
  if ((millis() - time_millis) > LoopWaitTime){
    time_millis = millis();

        if (RunCircle == true)
        {
          if (phase != 5)
          {
            Target_X_Clast = 0;
            Target_Y_Clast = 0;
          }
          phase = 5;
        }
//        else
//        {
//          phase = 1;
//        }

    
    switch (phase){
      case 1:
        //this logic will wait and find the servo centers before moving along
        if (dataValid != 1){
          LoopWaitTime = 5000;
          Target_X = 500;
          Target_Y = 500;
          phase =1;
          
          if ((Xerror_last < 3) and (Yerror_last < 3)){
            EEPROM.write(0,1);
            EEPROM.write(1, byte(ServoAval/10));
            EEPROM.write(2, byte(ServoBval/10));
            dataValid = 1;
          }
        }else{
          LoopWaitTime = 5000;
          Target_X = 500;
          Target_Y = 500;
          phase =2;
        }
        break;
      case 2:
        LoopWaitTime = 5000;
        Target_X = 500;
        Target_Y = 600;
        phase = 3;
        break;
      case 3:
        LoopWaitTime = 5000;
        Target_X = 500;
        Target_Y = 500;
        phase = 4;
        break;
      case 4:
        LoopWaitTime = 5000;
        Target_X = 500;
        Target_Y = 400;
        phase = 1;
        break;
      case 5:
        //if we are closer to the next point than the last point, load the next point
        double DistNew = pow((Xpos - Target_X),2) + pow((Ypos - Target_Y),2);
        double DistOld =  pow((Xpos - Target_X_Clast),2) + pow((Ypos - Target_Y_Clast),2);
        if (DistNew < DistOld)
        {
          Target_X_Clast = Target_X;
          Target_Y_Clast = Target_Y;
          angle = angle +30;
          LoopWaitTime = 10;
          if (angle > 360){ 
            angle = 0;
            phase = 1;
          }
          Target_X = 500 + 100*sin(radians(angle));
          Target_Y = 500 + 50*cos(radians(angle));
        }
        break;
    }
   
  }
    
}

//Check if a valid serial command has been recieved and do something about it  
int SerialCommander(){
  char invalA[2] = {SerialBuffer[2],SerialBuffer[3]};
  switch (SerialBuffer[0]){
    //list of valid commands
    case 'Q':  //A +
      ServoAval += 5;
      Serial.print("Aval = ");
      Serial.println(ServoAval);
      return  1;
      break;
    case 'A':  //A-
      ServoAval -= 5;
      Serial.print("Aval = ");
      Serial.println(ServoAval);
      return 1;
      break;
    case 'P':  //B+
      ServoBval += 5;
      Serial.print("Bval = ");
      Serial.println(ServoBval);
      return 1;
      break;
    case 'L':  //B-
      ServoBval -= 5;
      Serial.print("Bval = ");
      Serial.println(ServoBval);
      return 1;
      break;
    case 'p':  //move vector command
      //set proportional
      Kp = int(Hex2Dec8(invalA));
      return  1;
      break;
    case 'i':  //move vector command
      //set integral
      Ki = int(Hex2Dec8(invalA));
      return  1;
      break;
    case 'd':  //move vector command
      //set differential
      Kd = int(Hex2Dec8(invalA));
      return  1;
      break;
    case 'f':  //move vector command
      //set differential
      Kf = int(Hex2Dec8(invalA));
      return  1;
      break;
    case 's':  //move vector command
        if (RunCircle == true)
        {
          RunCircle = false;
        }
        else
        {
          RunCircle = true;
        }
      return  1;
      break;
    case 'e':
      //write current servo position as the new center to EEPROM
      EEPROM.write(0,1);
      EEPROM.write(1, byte(ServoAval/10));
      EEPROM.write(2, byte(ServoBval/10));
      dataValid = 1;

      return  1;
      break; 
    case 'c':
      //clear servo position data in eeprom
      EEPROM.write(0,0);
      EEPROM.write(1, byte(1500/10));
      EEPROM.write(2, byte(1500/10));
      dataValid = 0;

      return  1;
      break; 
      
  }
//a valid command was not recieved
  return 0;
}  

int Hex2Dec8(char Hex[2]){
  return 16*Char2Int(Hex[0]) + Char2Int(Hex[1]);
}  

int Char2Int(char in){
  switch (in){
    case '0':
      return 0;
      break;
    case '1':
      return 1;
      break;
    case '2':
      return 2;
      break;
    case '3':
      return 3;
      break;
    case '4':
      return 4;
      break;
    case '5':
      return 5;
      break;
    case '6':
      return 6;
      break;
    case '7':
      return 7;
      break;
    case '8':
      return 8;
      break;
    case '9':
      return 9;
      break;
    case 'a':
      return 10;
      break;
    case 'b':
      return 11;
      break;
    case 'c':
      return 12;
      break;
    case 'd':
      return 13;
      break;
    case 'e':
      return 14;
      break;
    case 'f':
      return 15;
      break;

    case 'A':
      return 10;
      break;
    case 'B':
      return 11;
      break;
    case 'C':
      return 12;
      break;
    case 'D':
      return 13;
      break;
    case 'E':
      return 14;
      break;
    case 'F':
      return 15;
      break;
  }
}  

void oldloop(){
  int ServoAval = 1400;
  int ServoBval = 1400;
  int   angle = 0;

  while (1){
    while(Serial.available() > 0) {
      
      
      
    }
    
    // a point object holds x y and z coordinates
    TSPoint p = ts.getPoint();
    
  // we have some minimum pressure we consider 'valid'
  // pressure of 0 means no pressing!
  if (p.z > ts.pressureThreshhold) {
     Serial.print("X = "); Serial.print(p.x);
     Serial.print("\tY = "); Serial.print(p.y);
     Serial.print("\tPressure = "); Serial.println(p.z);
  }
    
    SetServoA(1500+100*sin(radians(angle)));
    SetServoB(1500+100*cos(radians(angle)));
    delay(2);
    //ServoAval += 1;
    //ServoBval += 1;
    angle += 1;

    if (angle >359){
      angle = 0;
    }
  }
}

void SetServoA(int value){
  ServoA.writeMicroseconds(3000-value);
}
void SetServoB(int value){
  ServoB.writeMicroseconds(value);
}
