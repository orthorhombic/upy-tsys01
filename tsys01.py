# based on: https://github.com/bluerobotics/BlueRobotics_TSYS01_Library/blob/master/TSYS01.cpp

import utime


class TSYS01(object):

    TSYS01_ADDR = const(0x77)
    TSYS01_RESET = const(0x1E)
    TSYS01_PROM_READ = const(0xA0)
    TSYS01_ADC_TEMP_CONV = const(0x48)
    TSYS01_ADC_READ = const(0x00)

    def __init__(self, i2c=None):
        try:
            self._bus = i2c
        except:
            print("Bus %d is not available.") % bus
            print("Available busses are listed as /dev/i2c*")

        self.reset()

        self.calibration = self.getCalibration()

    def writeto(self, address, value):
        temp = bytearray(1)
        temp[0] = value
        self._bus.writeto(address, temp)

    def readfrom_mem_2(self, address, register):
        data = self._bus.readfrom_mem(address, register, 2)
        value = data[0] << 8 | data[1]
        return value

    def getCalibration(self):
        C = []
        for i in range(0, 8):
            register = TSYS01_PROM_READ + i * 2
            C.append(self.readfrom_mem_2(TSYS01_ADDR, register))
        return C

    def readfrom_3(self, address):
        data = self._bus.readfrom(address, 3)
        value = 0
        value = data[0]
        value = (value << 8) | data[1]
        value = (value << 8) | data[2]
        return value

    def calcTemp(self, C, D1):
        adc = D1 / 256.0

        TEMP = (
            (-2) * float(C[1]) / 1000000000000000000000.0 * (adc ** 4)
            + 4 * float(C[2]) / 10000000000000000.0 * (adc ** 3)
            + (-2) * float(C[3]) / 100000000000.0 * (adc ** 2)
            + 1 * float(C[4]) / 1000000.0 * adc
            + (-1.5) * float(C[5]) / 100
        )
        return TEMP

    def reset(self):
        self.writeto(TSYS01_ADDR, TSYS01_RESET)
        utime.sleep_ms(10)

    def convert(self):
        self.writeto(TSYS01_ADDR, TSYS01_ADC_TEMP_CONV)
        utime.sleep_ms(10)
        self.writeto(TSYS01_ADDR, TSYS01_ADC_READ)

    def getTemp(self):
        self.convert()

        D1 = self.readfrom_3(TSYS01_ADDR)

        t = self.calcTemp(self.calibration, D1)

        return t

    def serialnum(self):
        # 2^8 * SN23...8 + SN7...0

        # sn23-8
        part1 = self.calibration[7]
        # part1 = 0x0005

        intermediate = (self.calibration[7]).to_bytes(2, "big")
        # intermediate = (0x96D9).to_bytes(2, "big")
        # sn 7-0
        part2 = intermediate[0]
        # part2 = 0x96D9 >> 8 # same as 0x96D9 // 2**8

        checksum = intermediate[1]

        serial = 2 ** 8 * part1 + part2

        # testcal = [ # example from datasheet (does not make sense)
        #     0,
        #     28446,
        #     24926,
        #     36016,
        #     32791,
        #     40781,
        #     0x0005,
        #     0x96D9,
        # ]

        val = 0
        for i in testcal:
            # bytewise addition of PROM
            # unclear if this is appropriate algorithm to use checksum
            temp = i.to_bytes(2, "big")
            val += temp[0]
            val += temp[1]
            print(i, temp[0], temp[1], val.to_bytes(2, "big")[1])
            # may need to add checksum to total sum?

        # val = sum(testcal) + checksum
        # print (val,val.to_bytes(3, "big")[-1])

        if val.to_bytes(2, "big")[1] == 0:
            print("checksum success")

        # bytes to int
        # int.from_bytes('\x05\x7f', "big")
        return serial


# import tsys01
# from machine import I2C
# from machine import Pin

# SCL=22
# SDA=23

# i2c = I2C(-1, Pin(SCL), Pin(SDA))

# t=tsys01.TSYS01(i2c)
# print(t.getTemp())

