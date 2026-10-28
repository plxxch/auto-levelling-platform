from time import sleep

import serial
import RPi.GPIO as GPIO
import numpy as np

#Signal
S1 = False
S2 = False
S3 = False
S4 = False
S1C = False
S2C = False
S3C = False
S4C = False
S1G = False
S2G = False
S3G = False
S4G = False
#Serial of inclinometer

ser = None
command_xyz = b'\x77\x04\x00\x04\x08'
feedback = ""
pattern_x = ""
pattern_y = ""
angle_x = 0
angle_y = 0
px1=0
py1=0
px2=0
py2=0

##Threshold for judging the tilt
#global thl=-0.1  
#global thh=0.1

#stroke length of each actuator


L1=0
L2=0
L3=0
L4=0
Com_index=0

Leg1_ext=0
Leg1_ret=0
Leg2_ext=0
Leg2_ret=0
Leg3_ext=0
Leg3_ret=0
Leg4_ext=0
Leg4_ret=0


Compare=False
Count_Angle=0

RL=[0,0,0,0]
Sequence_temp=[0,0,0,0]

#Define the pins of relay

#Front left
relay1 = 17 #Extend
relay2 = 27 #Retract

#Front right
relay3 = 18 #Extend
relay4 = 5  #Retract

#Back right
relay5 = 6  #Extend
relay6 = 13 #Retract

#Back left
relay7 = 19 #Extend
relay8 = 26 #Retract

#Docking
angle_test = 6
sig1 = False
sig2 = False 
sig3 = False
sig4 = False
step1 = True
step2 = False
step3 = False
step4 = False
Extended = False
started = False

#For recording the length
px1 = 0             #previous_x_1
py1 = 0
px2 = 0             #previous_y_1
py2 = 0
th_load=0.1



power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

#Control signal
balanced = False
docked = False
change = False


#Jugde load or unload condition
def recordlength():
    global L1, L2, L3, L4
    global Leg1_ext, Leg1_ret, Leg2_ext, Leg2_ret
    global Leg3_ext, Leg3_ret, Leg4_ext, Leg4_ret
    global px1, px2, py1, py2

    if abs(px2 - px1) != 0 or abs(py2 - py1) != 0:
        if Leg1_ext:
            L1 += 1
        elif Leg1_ret:
            L1 -= 1
        if Leg2_ext:
            L2 += 1
        elif Leg2_ret:
            L2 -= 1
        if Leg3_ext:
            L3 += 1
        elif Leg3_ret:
            L3 -= 1
        if Leg4_ext:
            L4 += 1
        elif Leg4_ret:
            L4 -= 1

    Leg1_ret = Leg2_ret = Leg3_ret = Leg4_ret = 0
    Leg1_ext = Leg2_ext = Leg3_ext = Leg4_ext = 0
    print(L1, L2, L3, L4)

def Sort_Length():
    global L1
    global L2
    global L3
    global L4
    global Leg1_ext
    global Leg1_ret
    global Leg2_ext
    global Leg2_ret
    global Leg3_ext
    global Leg3_ret
    global Leg4_ext
    global Leg4_ret
    global Compare
    global Count_Angle
 
    RL[0]=L1
    RL[1]=L2
    RL[2]=L3
    RL[3]=L4

    print(RL)  
    RLength=np.array(RL)
    Sequence=np.argsort(RLength)
    Sequence_temp[0]=Sequence[0]             #Ls: Length sequence
    Sequence_temp[1]=Sequence[1]            
    Sequence_temp[2]=Sequence[2]            
    Sequence_temp[3]=Sequence[3]             
    print('Length sequence is')
    print(Sequence_temp)

#Select leg according to the sequence

def Legselection():
    global L1
    global L2
    global L3
    global L4
    global Leg1_ext
    global Leg1_ret
    global Leg2_ext
    global Leg2_ret
    global Leg3_ext
    global Leg3_ret
    global Leg4_ext
    global Leg4_ret
    global Compare
    global Count_Angle
    global S1
    global S2
    global S3
    global S4 
    #if Compare==True:
    Ls = Sequence_temp[0]             #Ls: Length sequence
    print("Leg")
    print(Ls)
    print('selected')

    if Ls == 0:
       S1 = True
    if Ls == 1:
        S2 = True
    if Ls == 2:
        S3 = True
    if Ls == 3:
        S4 = True
    # remove the shortest  
    a=len(Sequence_temp)
    if a!=1:
    
        Sequence_temp.pop(0) 
    
    print('New sequence_temp is')
    print(Sequence_temp)
 
    Compare = False





def AngleXY():
    global angle_x, angle_y, pattern_x, pattern_y

    if ser is None or not ser.is_open:
        return False

    try:
        ser.reset_input_buffer()
        ser.write(command_xyz)
        word = ser.read(1000)
    except serial.SerialException:
        return False

    if not word:
        return False

    feedback = word.hex()
    if len(feedback) < 24:
        return False

    pattern_x = ""
    pattern_y = ""
    for i in range(len(feedback)):
        if 7 < i < 16:
            pattern_x += feedback[i] + ("." if i == 11 else "")
        elif 16 <= i < 24:
            pattern_y += feedback[i] + ("." if i == 19 else "")

    try:
        x_value = round(float(pattern_x[2:]))
        y_value = round(float(pattern_y[2:]))
    except ValueError:
        return False

    angle_x = x_value if pattern_x[0] == "1" else -x_value
    angle_y = -y_value if pattern_y[0] == "1" else y_value
    return True

#set all to stop
def init_GPIO():
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.HIGH)
    GPIO.output(relay3, GPIO.HIGH)
    GPIO.output(relay4, GPIO.HIGH)
    GPIO.output(relay5, GPIO.HIGH)
    GPIO.output(relay6, GPIO.HIGH)
    GPIO.output(relay7, GPIO.HIGH)
    GPIO.output(relay8, GPIO.HIGH)


#Retraction of legs
def Retract(x,y):
    global balanced
    global change
    #Retraction
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay3, GPIO.HIGH)
    GPIO.output(relay5, GPIO.HIGH)
    GPIO.output(relay7, GPIO.HIGH)
    GPIO.output(relay2, GPIO.LOW)
    GPIO.output(relay4, GPIO.LOW)
    GPIO.output(relay6, GPIO.LOW)
    GPIO.output(relay8, GPIO.LOW)
    sleep(1)
    change = True
    print("Changed")
    if(x!=0 and y!=0):
         GPIO.output(relay2, GPIO.HIGH)
         GPIO.output(relay4,GPIO.HIGH)
         GPIO.output(relay6,GPIO.HIGH)
         GPIO.output(relay8,GPIO.HIGH)

#Stop all legs
def stop():
    GPIO.output(relay1,GPIO.HIGH)
    GPIO.output(relay2,GPIO.HIGH)
    GPIO.output(relay3,GPIO.HIGH)
    GPIO.output(relay4,GPIO.HIGH)
    GPIO.output(relay5,GPIO.HIGH)
    GPIO.output(relay6,GPIO.HIGH)
    GPIO.output(relay7,GPIO.HIGH)
    GPIO.output(relay8,GPIO.HIGH)


#Docking
def Docking():
    print("Docking")
    global started
    global docked
    global S1
    global S2
    global S3
    global S4
    global S1C
    global S2C
    global S3C
    global S4C
    global S1G    #S1 GROUNDED
    global S2G
    global S3G
    global S4G
    global balanced
    global angle_x
    global angle_y
    
    global L1
    global L2
    global L3
    global L4
    global Leg1_ext
    global Leg1_ret
    global Leg2_ext
    global Leg2_ret
    global Leg3_ext
    global Leg3_ret
    global Leg4_ext
    global Leg4_ret
    global Compare
    global Count_Angle
    global px1
    global px2
    global py1
    global py2
 

## MAIN
    Sort_Length()
    Compare=True
    Legselection()
    name=input('Start Docking?')
    while docked==False:
        if ser is None or not ser.is_open:
            break

        if not AngleXY():
            sleep(0.1)
            continue

        if Count_Angle == 0:
            px1, py1 = angle_x, angle_y
        else:
            px2, py2 = angle_x, angle_y
        Count_Angle ^= 1

        x_rot = angle_x
        y_rot = angle_y
        print("X rot: {0}  Y rot:{1}".format(x_rot,y_rot))
        if S1G==False or S2G==False  or S3G==False or S4G==False:
            print("undocked!")
            print("D1: {0}\nD2: {1}\nD3: {2}\nD4: {3}".format(S1,S2,S3,S4))
            if S1==True and S3==False and S4==False and S2 == False and balanced==True: # Actuator 1 Docking
               GPIO.output(relay1,GPIO.LOW)
              # Leg1_ext=1
              # recordlength()
               if (x_rot != 0) or (y_rot > 0 or y_rot < 0):
                  init_GPIO()
                  GPIO.output(relay2,GPIO.LOW)
               #   Leg1_ret=1
               #   recordlength()
                  S1C = True
               if x_rot == 0 and y_rot == 0 and S1C == True:
                  init_GPIO()
                  S1 = False
                  S1G = True
                  Compare=True
                  Legselection()
                  
                  
                  print("Act1 Docked!")

                           
            if S1==False and S3==False and S4==False and S2 == True and balanced==True: # Actuator 2 Docking
                 GPIO.output(relay3,GPIO.LOW)
                # Leg2_ext=1
                # recordlength()
                 if (x_rot != 0) or (y_rot > 0 or y_rot < 0):
                    init_GPIO()
                    GPIO.output(relay4,GPIO.LOW)
                 #   Leg2_ret=1
                  #  recordlength()
                    S2C = True
                 if (x_rot == 0) and (y_rot == 0) and (S2C == True):
                    init_GPIO()
                    S2 = False
                    S2G = True
                    Compare=True
                    Legselection()
                    print("Act2  Docked!")

    
            if  S1==False and S3==True and S4==False and S2 == False and balanced==True: # Actuator 3 Docking
                 GPIO.output(relay5,GPIO.LOW)
                 Leg3_ext=1
                 recordlength()
                 if (x_rot != 0) or (y_rot > 0 or y_rot < 0):
                    init_GPIO()
                    GPIO.output(relay6,GPIO.LOW)
                    #Leg3_ret=1
                    #recordlength()
                    S3C = True
                 if x_rot == 0 and y_rot == 0 and S3C == True:
                    init_GPIO()
                    S3 = False
                    S3G = True
                    Compare=True
                    Legselection()
                    print("Act3  Docked!")
    
   
            if S1==False and S3==False and S4==True and S2 == False and balanced==True: # Actuator 4 Docking
                 GPIO.output(relay7,GPIO.LOW)
                 Leg4_ext=1
                 recordlength()
                 if (x_rot != 0) or (y_rot > 0 or y_rot < 0):
                    init_GPIO()
                    GPIO.output(relay8,GPIO.LOW)
                 #   Leg4_ret=1
                  #  recordlength()
                    S4C = True
                 if x_rot == 0 and y_rot == 0 and S4C == True:
                    init_GPIO()
                    S4 = False
                    S4G = True
                    Compare=True
                    Legselection()
                    print("Act4  Docked!")
                                            
        else:
               print("docked!")
               if S1G==True and S2G== True and S3G==True and S4G== True:
                  balanced = True
                  docked = True
          
                  

def run():
    global balanced, docked, change, started
    global px1, py1, px2, py2, Count_Angle
    global Leg1_ext, Leg2_ext, Leg3_ext, Leg4_ext
    global sig1, sig2, sig3, sig4

    init_GPIO()

    while not (balanced and docked):
        if ser is None or not ser.is_open:
            break
        if not AngleXY():
            sleep(0.1)
            continue

        if Count_Angle == 0:
            px1, py1 = angle_x, angle_y
        else:
            px2, py2 = angle_x, angle_y
        Count_Angle ^= 1

        x_rot = angle_x
        y_rot = angle_y
        print("X rot: {0} Y rot: {1}".format(x_rot, y_rot))

        if x_rot == 0 and y_rot == 0 and not started:
            if not balanced:
                started = True
                sleep(0.1)
                Retract(x_rot, y_rot)
                started = False
                print("Balanced!")
            if balanced:
                init_GPIO()
                Docking()
                break

        if x_rot != 0 or y_rot != 0:
            init_GPIO()
            if change:
                init_GPIO()
                balanced = True

            if x_rot > 0 and y_rot == 0 and not started:
                started = True
                GPIO.output(relay1, GPIO.LOW)
                GPIO.output(relay3, GPIO.LOW)
                Leg1_ext = 1
                Leg2_ext = 1
                recordlength()
                started = False
                print("2.1")

            elif x_rot < 0 and y_rot == 0 and not started:
                started = True
                GPIO.output(relay5, GPIO.LOW)
                GPIO.output(relay7, GPIO.LOW)
                Leg3_ext = 1
                Leg4_ext = 1
                recordlength()
                started = False
                print("2.2")

            elif y_rot > 0 and x_rot == 0 and not started:
                started = True
                GPIO.output(relay1, GPIO.LOW)
                GPIO.output(relay7, GPIO.LOW)
                Leg1_ext = 1
                Leg4_ext = 1
                recordlength()
                started = False
                if change:
                    sig2 = True
                if change and sig2:
                    sig3 = True
                print("2.3")

            elif y_rot < 0 and x_rot == 0 and not started:
                started = True
                GPIO.output(relay3, GPIO.LOW)
                GPIO.output(relay5, GPIO.LOW)
                Leg2_ext = 1
                Leg3_ext = 1
                recordlength()
                started = False
                if change:
                    sig1 = True
                print("2.4")

            elif x_rot > 0 and y_rot > 0 and not started:
                started = True
                GPIO.output(relay1, GPIO.LOW)
                Leg1_ext = 1
                recordlength()
                started = False
                if change:
                    sig3 = True
                print("1.1")

            elif x_rot > 0 and y_rot < 0 and not started:
                started = True
                GPIO.output(relay3, GPIO.LOW)
                Leg2_ext = 1
                recordlength()
                started = False
                if change:
                    sig4 = True
                print("1.2")

            elif x_rot < 0 and y_rot > 0 and not started:
                started = True
                GPIO.output(relay7, GPIO.LOW)
                Leg4_ext = 1
                recordlength()
                started = False
                if change:
                    sig2 = True
                print("1.3")

            elif x_rot < 0 and y_rot < 0 and not started:
                started = True
                GPIO.output(relay5, GPIO.LOW)
                Leg3_ext = 1
                recordlength()
                started = False
                if change:
                    sig1 = True
                print("1.4")


def main():
    global ser

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in (relay1, relay2, relay3, relay4, relay5, relay6, relay7, relay8):
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

    try:
        ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=0.5)
        run()
    finally:
        stop()
        if ser is not None and ser.is_open:
            ser.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
