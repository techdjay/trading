// Downloaded From https://www.WiseStockTrader.com
/* Its a jscript and hence should be run from the command prompt. Change parameters  ** before executing the script. Also take backup of your data for safety reasons.
** AmiBroker/Win32 scripting Example
**
** File:                Remove all quotations between dates .js
** Version:             0.1 beta
** Purpose:             Remove all quotations between dates for all symbols !
** Language:            JScript (Windows Scripting Host)
**
**
** CHANGE variable DataDir
** CHANGE variable DeleteFrom and DeleteTo 
**
** ENJOY :-)
*/

// where database is stored
fs = new ActiveXObject("Scripting.FileSystemObject");

DataDir = "C:\\AmiFeeds\\Amibroker\\AFData"

var oAB = new ActiveXObject("Broker.Application");
var fso = new ActiveXObject("Scripting.FileSystemObject");
file    = fso.OpenTextFile( "_remowe_xdays.log", 2, true );

oAB.LoadDatabase( DataDir );

var oStocks = oAB.Stocks;
var Qty = oStocks.Count;
var MiliSecInDay = 24 * 60 * 60 *1000;

var DeleteFrom = new Date("august 24, 2021 15:50:00");
var DeleteTo = new Date("august 25, 2021 10:10:00");

//add a day to the date
DeleteTo.setDate(DeleteTo.getDate() + 1);

// make date with time 00:00:00        
var DayDeleteFrom = new Date((Math.floor(DeleteFrom / MiliSecInDay)) * MiliSecInDay);
var DayDeleteFromNum = (Math.floor(DeleteFrom / MiliSecInDay)) * MiliSecInDay;

var DayDeleteTo = new Date((Math.floor(DeleteTo / MiliSecInDay)) * MiliSecInDay);
var DayDeleteToNum = (Math.floor(DeleteTo / MiliSecInDay)) * MiliSecInDay;

file.WriteLine( "Starting delete quotes from date:" + DeleteFrom);
file.WriteLine( "" );

for( i = 0; i < Qty; i++ )
{
        oStock = oStocks( i );
        file.Write( i + ". " + oStock.Ticker + "=" );

        for (j=oStock.Quotations.Count-1;j>=0;j--)
        {
                //file.Write( "j=" + j + "," );
                //tmpDate = new Date( oStock.Quotations( j ).Date );
                tmpDateNum = oStock.Quotations( j ).Date ;
                if (tmpDateNum >= DayDeleteFromNum) 
                {
			if (tmpDateNum <= DayDeleteToNum) 
			{
                        //file.WriteLine( "Delete data=" + tmpDateNum);
                        oStock.Quotations.Remove(j);
			}
                }
                else 
                {
                        //file.WriteLine( "Last data no to delete=" +tmpDateNum);
                        break;
                } 
        }
        file.WriteLine( "OK" );
}
oAB.SaveDatabase( );

file.Close();
WScript.Echo("Cleanup ended :-)" );