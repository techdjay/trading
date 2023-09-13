import requests
import pandas as pd
import datetime
import threading

# Define your constants and variables
start_date = datetime.date(2022, 9, 1)
end_date = datetime.date(2023, 9, 14)
day = 30
dy = 31
userid = 'ZG7393'
timeframe = 'day'

auth_token = 'enctoken VafCbGwwyfiJugA6Qnmnp+OAtUTknrPiVfwf1EJJfSK2ivBsaPVZnfHCkStE2IEIoEMA/ep/sj0hbP8SKBtJSJmjLV5H9kQONbiBkjvJSwbLaTDf3HxKOA=='
headers = {
    'authorization': auth_token,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76',
    'Authority': 'kite.zerodha.com',
    'scheme': 'https',
    'Accept': '*/*',
    'Accept-Encoding': 'utf-8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Cookie': 'kf_session=PI7b8rbk1ql4O6aN4r1n6EO3Oh3aMhhN; _cfuvid=EHeDiDNN9xJoAyvTDiiJG1Ns7x1ohAnlF8g8XHhT5xM-1694605150651-0-604800000; user_id=ZG7393; public_token=WNTYDboLij458qZNchDADlrf0vABcS2B; enctoken=VafCbGwwyfiJugA6Qnmnp+OAtUTknrPiVfwf1EJJfSK2ivBsaPVZnfHCkStE2IEIoEMA/ep/sj0hbP8SKBtJSJmjLV5H9kQONbiBkjvJSwbLaTDf3HxKOA==',
    'Host': 'kite.zerodha.com',
    'Referer': 'your_referer_here',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin'
}

#token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\zerodha_ins_for_eod_ami.xlsx')
token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\nifty50listzrodha.xlsx')

# Function to fetch data for a given token
def fetch_data(i, token):
    columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'V', 'OI']
    final_df = pd.DataFrame(columns=columns)
    from_date = start_date

    while from_date <= end_date:
        to_date = from_date + datetime.timedelta(days=day)

        url = f'https://kite.zerodha.com/oms/instruments/historical/{token}/{timeframe}?user_id={userid}&oi=1&from={from_date}&to={to_date}'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            resJson = response.json()

            if 'data' in resJson and 'candles' in resJson['data']:
                candelinfo = resJson['data']['candles']
                df = pd.DataFrame(candelinfo, columns=columns)
                final_df = final_df.append(df, ignore_index=True)
            else:
                print(f"Invalid response format for token {token}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed for token {token}: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error for token {token}: {e}")

        from_date = from_date + datetime.timedelta(days=dy)

    # Process the data, if needed
    # Save the data to a CSV file
    final_df['timestamp'] = [datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z') for d in final_df['timestamp']]
    final_df['date'] = [datetime.datetime.date(d) for d in final_df['timestamp']]
    final_df['time'] = [datetime.datetime.time(d) for d in final_df['timestamp']]
    final_df['ticker'] = token_df.loc[i]['SYMBOL']
    final_df.drop('timestamp', axis=1, inplace=True)
    final_df = final_df[['ticker', 'date', 'Open', 'High', 'Low', 'Close', 'V', 'OI', 'time']]
    final_df.to_csv('C:/ZerodhaHistoricalData/eoddata.csv', mode='a', header=False, index=False)
    print(f"Data for token {token} imported successfully")


def main():
    for i in range(len(token_df)):
        token = token_df.loc[i]['TOKEN']
        fetch_data(i, token)

    print("Done!")


if __name__ == '__main__':
    main()
