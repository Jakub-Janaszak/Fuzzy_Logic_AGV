# -*- coding: utf-8 -*-
import socket
import time
import numpy as np
import pandas as pd

from Stage1 import Stage1Controller
from Stage2 import Stage2Controller
from Stage3 import Stage3Controller

class MotorSensorController:
    def __init__(self, motorsHost, motorsPort, sensorsHost, sensorsPort):
        self.motorsHost = motorsHost
        self.motorsPort = motorsPort
        self.sensorsHost = sensorsHost
        self.sensorsPort = sensorsPort
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        
        self.speed_L = 0
        self.speed_R = 0
        self.iteration = 0
        self.mode = 1
        self.record = []
        
        self.d1_list = []
        self.d2_list = []
        self.d3_list = []

        self.stage1 = Stage1Controller()
        self.stage2 = Stage2Controller()
        self.stage3 = Stage3Controller()

    def motorSend(self):

        left_f = 0xFF
        left_b = 0xFF
        right_f = 0xFF
        right_b = 0xFF

        if self.speed_L >= 0:
            left_f = 255 - (self.speed_L + 80)
        else:
            left_b = 255 - (abs(self.speed_L) + 80)

        if self.speed_R >= 0:
            right_f = 255 - (self.speed_R + 80)
        else:
            right_b = 255 - (abs(self.speed_R) + 80)


        if left_b > 170:
            left_b = 255
        if left_f > 170:
            left_f = 255
        if right_b > 170:
            right_b = 255
        if right_f > 170:
            right_f = 255


        message = bytes([int(left_b), int(left_f), int(right_b), int(right_f)])
        self.client.sendto(message, (self.motorsHost, self.motorsPort))

    def motorReceiveResponse(self):
        try:
            data, addr = self.client.recvfrom(1024)
            # print(f"Otrzymano odpowiedź od {addr}: {data}")
        except socket.timeout:
            print("Brak odpowiedzi, przekroczono czas oczekiwania")

    def sensorSend(self):
        message = bytes([0x00, 0x00, 0x00, 0x00])
        self.client.sendto(message, (self.sensorsHost, self.sensorsPort))

    def sensorReciveResponse(self):
        try:
            data, addr = self.client.recvfrom(1024)
            data_str = data.decode('utf-8')
            values = data_str.split(";")
            d1 = int(values[1])
            d2 = int(values[2])
            d3 = int(values[3])

            print(f"{d1}, {d2}, {d3}")
            self.record.append([d1, d2, d3, self.speed_L, self.speed_R])
            return d1, d2, d3
        except socket.timeout:
            print("Brak odpowiedzi, przekroczono czas oczekiwania")
            return None, None, None

    def updateSpeeds(self, d1, d2, d3):
        if d1 is not None and d2 is not None and d3 is not None:
            
            #print("AVG: ")
            #print(d1, d2, d3)
            if self.mode == 1:
                print("Mode: 1")
                speedL, speedR = self.stage1.calculateWheelSpeeds(d1, d2, d3)
                if d2 < 280 or d3 < 280:
                    self.mode = 2
            elif self.mode == 2:
                print("Mode: 2")
                speedL, speedR = self.stage2.calculateWheelSpeeds(d1, d2, d3)
                if abs((d1-40) - d2)<70:
                    self.mode = 3
            elif self.mode == 3:
                print("Mode: 3")
                speedL, speedR = self.stage3.calculateWheelSpeeds(d1, d2, d3)
                if d3<350:
                    self.mode = 4
                    self.speed_L = 0
                    self.speed_L = 0
            
            self.speed_L = speedL
            self.speed_R = speedR


    def run(self, iterations):
        while (self.mode != 4):
            time.sleep(0.001)
            self.motorSend()
            self.motorReceiveResponse()
            self.sensorSend()
            d1, d2, d3 = self.sensorReciveResponse()
            self.d1_list.append(d1)
            self.d2_list.append(d2)
            self.d3_list.append(d3)
            d1_avg_last5 = sum(self.d1_list[-5:]) / len(self.d1_list[-5:])
            d2_avg_last5 = sum(self.d2_list[-5:]) / len(self.d2_list[-5:])
            d3_avg_last5 = sum(self.d3_list[-5:]) / len(self.d3_list[-5:])
            self.updateSpeeds(d1,d2,d3)
        self.motorSend()
        self.client.close()
        print("AGV arived!")
        df = pd.DataFrame(self.record, columns=['d1','d2','d3', 'speed_L', 'speed_R'])
        df.to_excel('110+0_1.xlsx')

if __name__ == "__main__":
    motorsHost = "192.168.0.101"
    motorsPort = 4000
    sensorsHost = "192.168.0.100"
    sensorsPort = 4000

    controller = MotorSensorController(motorsHost, motorsPort, sensorsHost, sensorsPort)
    controller.run(1000)
