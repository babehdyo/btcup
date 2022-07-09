
import math
from datetime import datetime
import pandas
import numpy as np
import structlog

class HeikinAshi():

#     # def heikin_ashi(historical_data):
#     #     dataframe = pd.DataFrame(index=historical_data.index.values, columns=['open', 'high', 'low', 'close'])
        
#     #     dataframe['close'] = (historical_data['open'] + historical_data['high'] + historical_data['low'] + historical_data['close']) / 4
        
#     #     for i in range(len(historical_data)):
#     #         if i == 0:
#     #             dataframe.iat[0, 0] = historical_data['open'].iloc[0]
#     #         else:
#     #             dataframe.iat[i, 0] = (dataframe.iat[i-1, 0] + dataframe.iat[i-1, 3]) / 2
            
#     #     dataframe['high'] = dataframe.loc[:, ['open', 'close']].join(historical_data['high']).max(axis=1)
        
#     #     dataframe['low'] = dataframe.loc[:, ['open', 'close']].join(historical_data['low']).min(axis=1)
        
#     #     return dataframe

    def __init__(self):
        self.logger = structlog.get_logger()

    def heikin_ashi(self, historical_data):

        df = pandas.DataFrame(historical_data)
        df.transpose()

        df.columns = ['timestamp', 'Open',
                             'High', 'Low', 'Close', 'volume']
        df['datetime'] = df.timestamp.apply(
            lambda x: pandas.to_datetime(
                datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

        

        df.set_index('datetime', inplace=True, drop=True)
        df.drop('timestamp', axis=1, inplace=True)
        df['HA_Close']=(df['Open']+ df['High']+ df['Low']+df['Close'])/4
        idx = df.index.name
        df.reset_index(inplace=True)

        ha_close_values = df['HA_Close']

        length = len(df)
        ha_open = np.zeros(length, dtype=float)
        ha_open[0] = (df['Open'][0] + df['Close'][0]) / 2

        for i in range(0, length - 1):
            ha_open[i + 1] = (ha_open[i] + ha_close_values[i]) / 2

        df['HA_Open'] = ha_open

        df['HA_High']=df[['HA_Open','HA_Close','High']].max(axis=1)
        df['HA_Low']=df[['HA_Open','HA_Close','Low']].min(axis=1)
        d = {'datetime': df['datetime'],'open': df['HA_Open'], 'high': df['HA_High'], 'low': df['HA_Low'], 'close': df['HA_Close'], 'volume': df['volume']}
        # d = {'datetime': df['datetime'], 'open': df['Open'], 'high': df['High'], 'low': df['Low'], 'close': df['Close'], 'volume': df['volume'],
        # 'HA_Open': df['HA_Open'], 'HA_High': df['HA_High'], 'HA_Low': df['HA_Low'], 'HA_Close': df['HA_Close']}
        heikindf = pandas.DataFrame(data=d)
        pandas.set_option("display.max_columns", None)
        return heikindf