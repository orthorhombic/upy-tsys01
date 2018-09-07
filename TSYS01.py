
# based on: https://github.com/bluerobotics/BlueRobotics_TSYS01_Library/blob/master/TSYS01.cpp

from machine import Pin
from machine import I2C
import time

SCL=22
SDA=23

TSYS01_ADDR = const(0x77)
TSYS01_RESET = const(0x1E)
TSYS01_PROM_READ = const(0XA0)
TSYS01_ADC_TEMP_CONV =const(0x48)
TSYS01_ADC_READ=const(0x00)


i2c = I2C(-1, Pin(SCL), Pin(SDA))

def writeto(address,value):
    temp=bytearray(1)
    temp[0]=value
    i2c.writeto(address,temp)

def readfrom_mem_2(address,register):
    data = i2c.readfrom_mem(address,register,2)
    value = data[0] << 8 | data[1]
    return value


def getCalibration():
    C=[]
    for i in range(0,8):
        register=TSYS01_PROM_READ+i*2
        C.append(readfrom_mem_2(TSYS01_ADDR,register))
    return C


def readfrom_3(address):
    data = i2c.readfrom(address,3)
    value = 0
    value = data[0]
    value = (value << 8) | data[1]
    value = (value << 8) | data[2]
    return value


def calcTemp(C,D1):
    adc = D1 / 256.

    TEMP = (-2) * float(C[1]) / 1000000000000000000000.0 * (adc**4) + 4 * float(C[2]) / 10000000000000000.0 * (adc**3) + (-2) * float(C[3]) / 100000000000.0 * (adc**2) + 1 * float(C[4]) / 1000000.0 * adc + (-1.5) * float(C[5]) / 100
    return TEMP


def reset():
    writeto(TSYS01_ADDR,TSYS01_RESET)
    time.sleep(0.01)


def convert():
    writeto(TSYS01_ADDR,TSYS01_ADC_TEMP_CONV)
    time.sleep(0.01)
    writeto(TSYS01_ADDR,TSYS01_ADC_READ)

def getTemp():
    reset()

    C=getCalibration()

    convert()

    D1=readfrom_3(TSYS01_ADDR)

    t=calcTemp(C,D1)
    
    return t


# example:

#temperature = getTemp()
#print(temperature)


