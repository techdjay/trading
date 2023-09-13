from jugaad_data.nse import NSELive
import os
import sys
import subprocess
import xlwings as xw
# this function is called on each ticker update
import datetime
import win32com.client as wcl
import time as td
wb = xw.Book('Tick Data.xlsx')
sht =wb.sheets('Sheet1')

row_no = 2


n = NSELive()
all_indices = n.all_indices()
#dataa =all_indices['data'][0]
#print(dataa)
def getnsedata():

           for idx in all_indices['data']:
                index = idx['index']
                last =  idx['last']
                perchng = idx['percentChange']
                time= all_indices['timestamp']
                print("{} : {} : {}".format(idx['index'], idx['last'], idx['percentChange'] ), all_indices['timestamp'])


if __name__ == '__main__':
        getnsedata()
        td.sleep(300)
        os.system("python investinglive.py")