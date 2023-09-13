/* This Java Script will import EOD in CSV format as defined in Zerodhaieoddata.format.
	   It will get the EOD data from Amibroker_Ouput_file folder and verify the current 
	   database. */
	   
	/* Create AmiBroker app object */
	
	var AmiBroker = new ActiveXObject( "Broker.Application" );
	
	/* OLE Import */
	/* AmiBroker.Import(0,filename, "Zerodhaieoddata.format"); */
	/* AmiBroker.SaveDatabase(); */
	
	/* Check is the current database is Data */

	if (AmiBroker.DatabasePath == "C:\\AmiFeeds\\Amibroker\\AFData" ) {
		WScript.echo( "Updating NSE data in progress" );
		AmiBroker.Import(0,"C:\\ZerodhaHistoricalData\\eoddata.csv", "Zerodhaieoddata.format");
		WScript.echo( "Updating NSE data completed" );
		}

	AmiBroker.RefreshAll();