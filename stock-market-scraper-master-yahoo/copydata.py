import win32com.client as wcl
from shutil import copyfile
import os
import time as tm
from win32com.client import Dispatch

ab = wcl.Dispatch("Broker.Application")
AmiBroker = Dispatch("Broker.Application")
#AmiBroker.visible = True
#AmiBroker.LoadDatabase('C:/AmiFeeds/Amibroker/AFData')
# AmiBroker.RefreshAll()
# AmiBroker.SaveDatabase()
while True:
    def save_data():
            path = 'C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test_c.txt'
            src = 'yflivequotestreamer.txt'
            dst = 'test_c.txt'
            try:
                data = copyfile(src, dst)
            except:
                print(FileNotFoundError, 'Unable to copy')
            else:
                print(data, 'file copies successfully')
            # copyfile('C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test.txt', 'C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test_c.txt')

            try:
                 ab.Import(0,'C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test_c.txt', "autouploaddata.format");

            except:
                print(FileNotFoundError, 'Unable to copy')
            #else:
             #   print('file imported to AB successfully')
            # ab.RefreshAll();
            #AmiBroker.Import(0, path, "autouploaddata.format")
            #AmiBroker.RefreshAll()
            tm.sleep(0.5)

    if __name__ == '__main__':
           save_data()