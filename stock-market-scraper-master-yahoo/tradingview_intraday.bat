@echo off
cls
echo -----Wait while Startig the Program ---------

"C:\Users\Jay\Desktop\Trading\stock-market-scraper-master-yahoo\venv\Scripts\python.exe" "C:\Users\Jay\Desktop\Trading\stock-market-scraper-master-yahoo\tradingview_Indraday.py"

echo Thnk You.... 
echo -------Completed Successfully ---------
echo %time%
timeout 10 > NUL
echo %time%