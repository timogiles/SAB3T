import serial
import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib import animation
import pygame
from pygame.locals import *

BLACK = [0,0,0]
WHITE = [255,255,255]
BLUE =  [0,0,255]
GREEN = [0,255,0]
RED =   [255,0,0]
MAGENTA =   [212,0,140]
ORANGE = [255,148,22]
CYAN =   [0,231,217]
LBLUE =  [127,127,255]
LGREEN = [127,255,127]
LRED =   [255,127,127]
LMAGENTA =   [212,127,140]
LCYAN =   [127,231,217]
LORANGE = [255,200,127]

port = serial.Serial("/dev/ttyAMA0", baudrate=38400, timeout = 3.0)
##for windows grab the serial port as shown here:
#port = serial.Serial("COM8", baudrate=38400, timeout = 3.0)

StringOut = ""
w=1280
h=800
#w = 800
#h = 480
pygame.init()
screen=pygame.display.set_mode((w,h),pygame.FULLSCREEN)
screen2 = screen
screen2 = screen2.convert_alpha()
screen3 = screen2
screen2.fill([255,255,255,20])
screen3.fill([255,255,255,20])
screen.fill(WHITE)
pygame.display.flip()

DataLen = 50

XtargetBuffer = []
YtargetBuffer = []
XposBuffer = []
YposBuffer = []
XerrBuffer = []
YerrBuffer = []
XfutBuffer = []
YfutBuffer = []
XdiffBuffer = []
YdiffBuffer = []
XintBuffer = []
YintBuffer = []
XangleBuffer = []
YangleBuffer = []
XshiftBuffer = []
YshiftBuffer = []

TextOverlay = True
GraphIndex = 1
GraphIndexMax = 3
Graph_err = 1
Graph_diff = 1
Graph_int = 1
Graph_angle = 1
Graph_shift = 1
pygame.font.init()
basicFont = pygame.font.SysFont(None, 15)
ActiveAdjust = 1 #set which PID value is active for Key up / Key down adjustment
Kp = 10
Kd = 10
Ki = 2
Kf = 10
AdjustBy = 1

while True:
    for e in pygame.event.get():
        if e.type==KEYUP:
            if e.key == K_t:
                #toggle text overlay
                if TextOverlay == False:
                    TextOverlay = True
                else:
                    TextOverlay = False
            elif e.key == K_g:
                #toggle text overlay
                GraphIndex += 1
                if GraphIndex > GraphIndexMax:
                    GraphIndex = 1
            elif e.key == K_1:
                Graph_err += 1
                if Graph_err == 2:
                    Graph_err = 0
            elif e.key == K_2:
                Graph_diff += 1
                if Graph_diff == 2:
                    Graph_diff = 0
            elif e.key == K_3:
                Graph_int += 1
                if Graph_int == 2:
                    Graph_int = 0
            elif e.key == K_4:
                Graph_angle += 1
                if Graph_angle == 2:
                    Graph_angle = 0
            elif e.key == K_5:
                Graph_shift += 1
                if Graph_shift == 2:
                    Graph_shift = 0
            elif e.key == K_p:
                ActiveAdjust = 1
            elif e.key == K_d:
                ActiveAdjust = 2
            elif e.key == K_i:
                ActiveAdjust = 3
            elif e.key == K_f:
                ActiveAdjust = 4
            elif e.key == K_s:
                #send a command that will cause the arduino to hang
                #this is test if it is hearing the PI talk to it.
                port.write("s\r")
            elif e.key == K_c:
                if AdjustBy == 1:
                    AdjustBy = 5
                else:
                    AdjustBy = 1
            elif e.key == K_UP:
                if ActiveAdjust == 1:
                    Kp += AdjustBy
                    if Kp > 255:
                        Kp = 255
                    text = hex(Kp).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "p " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                elif ActiveAdjust == 2:
                    Kd += AdjustBy
                    if Kd > 255:
                        Kd = 255
                    text = hex(Kd).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "d " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                elif ActiveAdjust == 3:
                    Ki += AdjustBy
                    if Ki > 255:
                        Ki = 255
                    text = hex(Ki).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "i " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                elif ActiveAdjust == 4:
                    Kf += AdjustBy
                    if Kf > 255:
                        Kf = 255
                    text = hex(Kf).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "f " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                print text

            elif e.key == K_DOWN:
                if ActiveAdjust == 1:
                    Kp -= AdjustBy
                    if Kp < 0:
                        Kp = 0
                    text = hex(Kp).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "p " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                elif ActiveAdjust == 2:
                    Kd -= AdjustBy
                    if Kd < 0:
                        Kd = 0
                    text = hex(Kd).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "d " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                elif ActiveAdjust == 3:
                    Ki -= AdjustBy
                    if Ki < 0:
                        Ki = 0
                    text = hex(Ki).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "i " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                elif ActiveAdjust == 4:
                    Kf -= AdjustBy
                    if Kf < 0:
                        Kf = 0
                    text = hex(Kf).lstrip("0x")
                    text = text.swapcase()
                    text = "00" + text
                    text = "f " + text[len(text)-2] + text[len(text)-1]
                    port.write(text + "\r")
                print text
            else:
                pygame.quit()
                exit()

    ReadBack = port.read(1)
    #print "read a character"
    StringOut = StringOut + ReadBack
    if ReadBack == "\r":
        #port.flush()
        ##print StringOut
        ##StringOut = ""
        StringOutExpanded =   StringOut.split(',')
        if len(StringOutExpanded) == 17:
            [aveCount,Xtarget,Ytarget,Xpos,Ypos,Xfut,Yfut,Xerr,Yerr,Xdiff,Ydiff,Xint,Yint,Xangle,Yangle,Xshift,Yshift] = StringOutExpanded
            print Xpos + "," + Ypos + "," + Xtarget + "," + Ytarget
            #print len(StringOut.split(','))
            StringOut = ""

            if len(XtargetBuffer) < DataLen:
                XtargetBuffer.append(h-(int(int(Xtarget)/1000.0*h)))
                YtargetBuffer.append(int(int(Ytarget)/1000.0*w))
                XposBuffer.append(h-(int(int(Xpos)/1000.0*h)))
                YposBuffer.append(int(int(Ypos)/1000.0*w))
                XerrBuffer.append(int(Xerr))
                YerrBuffer.append(int(Yerr))
                XfutBuffer.append(int(Xfut))
                YfutBuffer.append(int(Yfut))
                XdiffBuffer.append(int(Xdiff))
                YdiffBuffer.append(int(Ydiff))
                XintBuffer.append(float(Xint)/50)
                YintBuffer.append(float(Yint)/50)
                XangleBuffer.append(int(Xangle))
                YangleBuffer.append(int(Yangle))
                XshiftBuffer.append(int(Xshift))
                YshiftBuffer.append(int(Yshift))
            else:
                XtargetBuffer.pop(0)
                YtargetBuffer.pop(0)
                XposBuffer.pop(0)
                YposBuffer.pop(0)
                XerrBuffer.pop(0)
                YerrBuffer.pop(0)
                XfutBuffer.pop(0)
                YfutBuffer.pop(0)
                XdiffBuffer.pop(0)
                YdiffBuffer.pop(0)
                XintBuffer.pop(0)
                YintBuffer.pop(0)
                XangleBuffer.pop(0)
                YangleBuffer.pop(0)
                XshiftBuffer.pop(0)
                YshiftBuffer.pop(0)
                XtargetBuffer.append(h-int(int(Xtarget)/1000.0*h))
                YtargetBuffer.append(int(int(Ytarget)/1000.0*w))
                XposBuffer.append(h-int(int(Xpos)/1000.0*h))
                YposBuffer.append(int(int(Ypos)/1000.0*w))
                XerrBuffer.append(int(Xerr))
                YerrBuffer.append(int(Yerr))
                XfutBuffer.append(h-int(int(Xfut)/1000.0*h))
                YfutBuffer.append(int(int(Yfut)/1000.0*w))
                XdiffBuffer.append(int(Xdiff))
                YdiffBuffer.append(int(Ydiff))
                XintBuffer.append(float(Xint)/50)
                YintBuffer.append(float(Yint)/50)
                XangleBuffer.append(int(Xangle))
                YangleBuffer.append(int(Yangle))
                XshiftBuffer.append(int(Xshift))
                YshiftBuffer.append(int(Yshift))
            

            #print len(XtargetBuffer)
            if len(XtargetBuffer) >= 6:
                CurLen = len(XtargetBuffer)
                #screen2.blit(screen3,(0,0))
                screen.fill(WHITE)
                    
                    
                if GraphIndex == 1:
                    #Draw current position as fading blue circles
                    pygame.draw.circle(screen, BLACK, [YtargetBuffer[CurLen-1],XtargetBuffer[CurLen-1]],10)
                    for i in range(CurLen-1):
                        val = 255-(255/CurLen*i)
                        pygame.draw.circle(screen, [val,val,255], [YposBuffer[i],XposBuffer[i]],6)
                    pygame.draw.circle(screen, GREEN, [YfutBuffer[CurLen-1],XfutBuffer[CurLen-1]],6)
                    
                if GraphIndex == 2:
                    #make grid
                    for i in range(9):
                        pygame.draw.line(screen, [64,64,64], [int((i+1)*w/10),0], [int((i+1)*w/10),h],1)
                    for i in range(9):
                        pygame.draw.line(screen, [64,64,64], [0,int((i+1)*h/10)], [w,int((i+1)*h/10)],1)

                    #GraphData
                    for i in range(CurLen-1):
                        if Graph_err == 1:
                            pygame.draw.line(screen, RED, [int((i)*w/CurLen),XerrBuffer[i]+h/2], [int((i+1)*w/CurLen),XerrBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LRED, [int((i)*w/CurLen),YerrBuffer[i]+h/2], [int((i+1)*w/CurLen),YerrBuffer[i+1]+h/2],3)
                        if Graph_diff == 1:
                            pygame.draw.line(screen, GREEN, [int((i)*w/CurLen),XdiffBuffer[i]+h/2], [int((i+1)*w/CurLen),XdiffBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LGREEN, [int((i)*w/CurLen),YdiffBuffer[i]+h/2], [int((i+1)*w/CurLen),YdiffBuffer[i+1]+h/2],3)
                        if Graph_int == 1:
                            pygame.draw.line(screen, ORANGE, [int((i)*w/CurLen),XintBuffer[i]+h/2], [int((i+1)*w/CurLen),XintBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LORANGE, [int((i)*w/CurLen),YintBuffer[i]+h/2], [int((i+1)*w/CurLen),YintBuffer[i+1]+h/2],3)
                        if Graph_angle == 1:
                            pygame.draw.line(screen, MAGENTA, [int((i)*w/CurLen),XangleBuffer[i]+h/2], [int((i+1)*w/CurLen),XangleBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LMAGENTA, [int((i)*w/CurLen),YangleBuffer[i]+h/2], [int((i+1)*w/CurLen),YangleBuffer[i+1]+h/2],3)
                        if Graph_shift == 1:
                            pygame.draw.line(screen, CYAN, [int((i)*w/CurLen),XshiftBuffer[i]+h/2], [int((i+1)*w/CurLen),XshiftBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LCYAN, [int((i)*w/CurLen),YshiftBuffer[i]+h/2], [int((i+1)*w/CurLen),YshiftBuffer[i+1]+h/2],3)
                if GraphIndex == 3:
                    #make grid
                    for i in range(9):
                        pygame.draw.line(screen, [64,64,64], [int((i+1)*w/10),0], [int((i+1)*w/10),h],1)
                    for i in range(9):
                        pygame.draw.line(screen, [64,64,64], [0,int((i+1)*h/10)], [w,int((i+1)*h/10)],1)

                    #GraphData
                    for i in range(CurLen-1):
                        if Graph_err == 1:
                            pygame.draw.line(screen, RED, [int((i)*w/CurLen),XerrBuffer[i]+h/2], [int((i+1)*w/CurLen),XerrBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LRED, [int((i)*w/CurLen),YerrBuffer[i]+h/2], [int((i+1)*w/CurLen),YerrBuffer[i+1]+h/2],3)
                        if Graph_diff == 1:
                            pygame.draw.line(screen, GREEN, [int((i)*w/CurLen),XdiffBuffer[i]+h/2], [int((i+1)*w/CurLen),XdiffBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LGREEN, [int((i)*w/CurLen),YdiffBuffer[i]+h/2], [int((i+1)*w/CurLen),YdiffBuffer[i+1]+h/2],3)
                        if Graph_int == 1:
                            pygame.draw.line(screen, ORANGE, [int((i)*w/CurLen),XintBuffer[i]+h/2], [int((i+1)*w/CurLen),XintBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LORANGE, [int((i)*w/CurLen),YintBuffer[i]+h/2], [int((i+1)*w/CurLen),YintBuffer[i+1]+h/2],3)
                        if Graph_angle == 1:
                            pygame.draw.line(screen, MAGENTA, [int((i)*w/CurLen),XangleBuffer[i]+h/2], [int((i+1)*w/CurLen),XangleBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LMAGENTA, [int((i)*w/CurLen),YangleBuffer[i]+h/2], [int((i+1)*w/CurLen),YangleBuffer[i+1]+h/2],3)
                        if Graph_shift == 1:
                            pygame.draw.line(screen, CYAN, [int((i)*w/CurLen),XshiftBuffer[i]+h/2], [int((i+1)*w/CurLen),XshiftBuffer[i+1]+h/2],3)
                            pygame.draw.line(screen, LCYAN, [int((i)*w/CurLen),YshiftBuffer[i]+h/2], [int((i+1)*w/CurLen),YshiftBuffer[i+1]+h/2],3)

                    #overlay position
                    pygame.draw.circle(screen, BLACK, [YtargetBuffer[CurLen-1],XtargetBuffer[CurLen-1]],10)
                    for i in range(CurLen-1):
                        val = 255-(255/CurLen*i)
                        pygame.draw.circle(screen, [val,val,255], [YposBuffer[i],XposBuffer[i]],6)
                    pygame.draw.circle(screen, GREEN, [YfutBuffer[CurLen-1],XfutBuffer[CurLen-1]],6)
                    
                if TextOverlay == True:
                    offset = 0

                    CurColor = BLACK

                    if GraphIndex == 1 or GraphIndex == 3:
                        CurColor = BLUE
                    else:
                        CurColor = BLACK
                    text = basicFont.render("X pos: " + str(Xpos), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15

                    text = basicFont.render("Y pos: " + str(Ypos), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_err == 1:
                        CurColor = RED
                    else:
                        CurColor = BLACK
                    text = basicFont.render("X err: " + str(Xerr), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_err == 1:
                        CurColor = LRED
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Y err: " + str(Yerr), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK
                    
                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_diff == 1:
                        CurColor = GREEN
                    else:
                        CurColor = BLACK
                    text = basicFont.render("X diff: " + str(Xdiff), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_diff ==1:
                        CurColor = LGREEN
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Y diff: " + str(Ydiff), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_int == 1:
                        CurColor = ORANGE
                    else:
                        CurColor = BLACK
                    text = basicFont.render("X int: " + str(float(Xint)/50), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15


                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_int == 1:
                        CurColor = LORANGE
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Y int: " + str(float(Yint)/50), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK


                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_angle == 1:
                        CurColor = MAGENTA
                    else:
                        CurColor = BLACK
                    text = basicFont.render("X angle: " + str(Xangle), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_angle == 1:
                        CurColor = LMAGENTA
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Y angle: " + str(Yangle), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_shift == 1:
                        CurColor = CYAN
                    else:
                        CurColor = BLACK
                    text = basicFont.render("X shift: " + str(Xshift), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15

                    if (GraphIndex == 2 or GraphIndex == 3) and Graph_shift == 1:
                        CurColor = LCYAN
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Y shift: " + str(Yshift), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK

                    offset += 15
                    if ActiveAdjust ==  1:
                        CurColor = RED
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Kp: " + str(Kp), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK
                    if ActiveAdjust ==  2:
                        CurColor = RED
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Kd: " + str(Kd), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK
                    if ActiveAdjust ==  3:
                        CurColor = RED
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Ki: " + str(Ki), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK
                    if ActiveAdjust ==  4:
                        CurColor = RED
                    else:
                        CurColor = BLACK
                    text = basicFont.render("Kf: " + str(Kf), True, CurColor)
                    screen.blit(text,(0,offset))
                    offset += 15
                    CurColor = BLACK


                pygame.display.flip()
        else:
            print "Wrong number of terms: " + str(len(StringOutExpanded))
            print StringOutExpanded
            StringOutExpanded = ""
            #pygame.quit()
            #exit()
