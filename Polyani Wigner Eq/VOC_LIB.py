import openpyxl
from openpyxl import Workbook
from pathlib import Path

class VOC():

    location = "/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/VOCs signal vs time data.xlsx"
    workbook = openpyxl.load_workbook(location)
    ws = workbook.active
    __VOC_dict = {
        'IPA':(1,467),
        'Benzene':(3,444),
        'Benzaldehyde':(5,459),
        'Limonene':(7,473),
        'MEK':(9,324),
        'Toulene':(11,438),
        'Oxylene':(13,452)
    } # 'Name' : (col # , concentration in PPB)

    def __init__(self,name,concentration,heating_rate=0.5):
        self.__name = name
        self.__conc = concentration
        self.__rate = heating_rate

    def __str__(self):
        return f'{self.__name} at {self.__conc} ppb'

    def get_col_data(self,col):
        col_data = []
        for row in range (3,586):
            cell = self.ws.cell(row,col)
            col_data.append(cell.value)
        return col_data

    def get_time_data(self):
        col,conc = self.__VOC_dict[self.__name]
        return self.get_col_data(col)

    def get_conc_data(self):
        col,conc = self.__VOC_dict[self.__name]
        return self.get_col_data(col+1)

    def get_new_conc_data(self):
        conc_data = self.get_conc_data()
        new_conc = self.__conc
        _, old_conc = self.__VOC_dict[self.__name]
        k = new_conc / old_conc #k is the proportional constant
        for index,value in enumerate(conc_data):
            conc_data[index] = k * value
        return conc_data



