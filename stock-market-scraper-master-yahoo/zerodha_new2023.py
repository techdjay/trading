import requests
import pandas as pd
import datetime
import threading
import os

filePath = 'C:\ZerodhaHistoricalData\eoddata.csv'

if os.path.exists(filePath):
    os.remove(filePath)
else:
    print("Cannot delete the file as it doesn't exist")

start_date = datetime.date(2022, 8, 22)
end_date = datetime.date(2023, 9, 12)
day = 1
dy = 1
userid = 'ZG7393'
timeframe = 'day'

auth_token = 'enctoken uf+hEsxRAxAiQlf5vbOwoD+qsGrV6NjXyCf+u1N1Tq+YoMANHicuq3qqS9IPVJNdM2Amze5qzQAxlnJ/ms/Nna++cH8FG4c8FwrPYwXHnrWWvi/PZ5+Nfg=='  # Replace with your actual auth token
headers = {
    'authorization': auth_token,
    'User-Agent': 'Your User Agent',
    "Authority": "kite.zerodha.com",
    "method": 'method',
    "path": 'path',
    "scheme": "https",
    "Accept": '*/*',
    "Accept-Encoding": "utf-8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Cookie": 'cookie',
    "Host": "kite.zerodha.com",
    "Referer": 'referer',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\zerodha_ins_for_eod_ami.xlsx')  # Replace with the actual path


def get_data(token):
    columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'V', 'OI']
    final_df = pd.DataFrame(columns=columns)
    from_date = start_date

    while from_date < end_date:
        to_date = from_date + datetime.timedelta(days=day)

        url = f'https://kite.zerodha.com/oms/instruments/historical/{token}/{timeframe}?user_id={userid}&oi=1&from={from_date}&to={to_date}'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            try:
                resJson = response.json()
                candelinfo = resJson['data']['candles']
                df = pd.DataFrame(candelinfo, columns=columns)
                final_df = final_df.append(df, ignore_index=True)
            except ValueError as e:
                print(f"Error parsing JSON response: {e}")
        else:
            print(f"Request failed with status code: {response.status_code}")

        from_date = from_date + datetime.timedelta(days=dy)

    final_df['timestamp'] = [datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z') for d in final_df['timestamp']]
    final_df['date'] = [datetime.datetime.date(d) for d in final_df['timestamp']]
    final_df['time'] = [datetime.datetime.time(d) for d in final_df['timestamp']]
    final_df['ticker'] = token_df.loc[i]['SYMBOL']
    final_df.drop('timestamp', axis=1, inplace=True)
    final_df = final_df[['ticker', 'date', 'Open', 'High', 'Low', 'Close', 'V', 'OI', 'time']]

    final_df.to_csv(filePath, mode='a', header=False, index=False)
    print(f"Data for token {token} imported successfully")


if __name__ == '__main__':
    threads = []

    for i in range(len(token_df)):
        token = token_df.loc[i]['TOKEN']
        thread = threading.Thread(target=get_data, args=(token,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Done!")


def get_data(token):
    columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'V', 'OI']
    final_df = pd.DataFrame(columns=columns)
    from_date = start_date

    while from_date < end_date:
        to_date = from_date + datetime.timedelta(days=day)

        url = f'https://kite.zerodha.com/oms/instruments/historical/{token}/{timeframe}?user_id={userid}&oi=1&from={from_date}&to={to_date}'

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                print("Rate limit exceeded. Waiting before retrying...")
                time.sleep(60)  # Wait for 60 seconds before retrying
                continue  # Skip the rest of the loop and retry

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
        except Exception as e:
            print(f"An error occurred for token {token}: {e}")

        # If the response doesn't contain the expected data, break the loop
        if not isinstance(candelinfo, list):
            print(f"No data found for token {token} between {from_date} and {to_date}")
            break

        from_date = from_date + datetime.timedelta(days=dy)

    # ... Rest of your data processing ...


if __name__ == '__main__':
    for i in range(len(token_df)):
        token = token_df.loc[i]['TOKEN']
        get_data(token)

    print("Done!")