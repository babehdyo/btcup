import math
import pandas
import talib
from talib import abstract

from analyzers.utils import IndicatorUtils
from analyzers.heikinAshi import HeikinAshi
import pandas
class Donchian(IndicatorUtils, HeikinAshi):
    
    def analyze(self, historical_data, signal=['SHORT','END SHORT'], hot_thresh=None, cold_thresh=None, period_count=30):
        heikinDF = self.heikin_ashi(historical_data)

        heikinDF2 = self.heikin_ashi(historical_data)
        heikinDF2 = heikinDF2[::-1].reset_index(drop=True)

        # ema8, length - 1 je current svicka
        ema = abstract.EMA(heikinDF['close'], 8)

        # heikin_ema_values = abstract.EMA(heikinDF2, 8).to_frame()
        # heikin_ema_values.dropna(how='all', inplace=True)
        # heikin_ema_values.rename(columns={0: 'ema'}, inplace=True)

        # candle_ema_values = abstract.EMA(candleDF, 8).to_frame()
        # candle_ema_values.dropna(how='all', inplace=True)
        # candle_ema_values.rename(columns={0: 'ema'}, inplace=True)
        
        # avg (mid-line), 0 je current svicka
        basis = [0] * 30
        upper = [0] * 30
        lower = [0] * 30
        for index, val in enumerate(basis):
            
            currentHighHead = heikinDF2['high'].head(index+30)
            currHighTail = currentHighHead.tail(30)
            currentLowHead = heikinDF2['low'].head(index+30)
            currLowTail = currentLowHead.tail(30)
            upper[index] = currHighTail.max()
            lower[index] = currLowTail.min()
            basis[index] = (upper[index] + lower[index]) / 2

# array of breaks above for last 30 values, used for higherheights
# 0 is current candle
        breaks_Above = [0] * 30

        for index, val in enumerate(breaks_Above):
            if index == 29:
                break
            if heikinDF2['high'][index] > upper[index+1]:
                breaks_Above[index] = 1

# array of breaks below for last 30 values, used for higherheights
        breaks_Below = [0] * 30
        for index, val in enumerate(breaks_Below):
            if index == 29:
                break
            if heikinDF2['low'][index] < lower[index+1]:
                breaks_Below[index] = 1



# array of breaks above B for last 30 values, used for higherheights
        breaks_Above_B = [0] * 30
        for index, val in enumerate(breaks_Above_B):
            if index == 29:
                break
            if heikinDF2['close'][index] > basis[index+1]:
                breaks_Above_B[index] = 1


# array of breaks below B for last 30 values, used for higherheights
        breaks_Below_B = [0] * 30
        for index, val in enumerate(breaks_Below_B):
            if index == 29:
                break
            if heikinDF2['close'][index] < basis[index+1]:
                breaks_Below_B[index] = 1


#  higherheights - if current break_Above is > 1,
#  set current HH to 1. If previous BA was > 1 too,
#  set current HH to previous HH value +1. Otherwise 0

        higherhigh = [0] * 30
        index = 29
        while index >= 0:
            if index == 29:
                if breaks_Above[index] > 0:
                    higherhigh[index] = 1
                else:
                    higherhigh[index] = 0
                index -= 1
                continue
            if breaks_Above[index] > 0:
                if  breaks_Above[index+1] > 0: 
                    higherhigh[index] = higherhigh[index+1] + 1
                else:
                    higherhigh[index] = 1
            else:
                higherhigh[index] = 0
            index -= 1


        lowerlow = [0] * 30
        index = 29
        while index >= 0:
            if index == 29:
                if breaks_Below[index] > 0:
                    lowerlow[index] = 1
                else:
                    lowerlow[index] = 0
                index -= 1
                continue
            if breaks_Below[index] > 0:
                if  breaks_Below[index+1] > 0: 
                    lowerlow[index] = lowerlow[index+1] + 1
                else:
                    lowerlow[index] = 1
            else:
                lowerlow[index] = 0
            index -= 1




        pa = [0] * 30
        index = 27
        while index >= 0:
            if (heikinDF2['close'][index] > heikinDF2['open'][index]) and ((breaks_Above_B[index] == 1 and (breaks_Above_B[index+1] == 0 or breaks_Above_B[index+2] == 0)) or higherhigh[index] > 1):
                pa[index] = 1
            elif (heikinDF2['close'][index] < heikinDF2['open'][index]) and ((breaks_Below_B[index] == 1 and (breaks_Below_B[index+1] == 0 or breaks_Below_B[index+2] == 0)) or lowerlow[index] > 1):
                pa[index] = -1
            else:
                pa[index] = 0
            index -= 1

        
        ma = [0] * 30
        index = 29
        while index >= 0:
            if heikinDF2['close'][index] > ema[len(ema)-index-1]:
                ma[index] = 1
            elif heikinDF2['close'][index] < ema[len(ema)-index-1]:
                ma[index] = -1
            else:
                ma[index] = 0
            index -= 1


        long = [0] * 30
        short = [0] * 30
        index = 0
        while index < 30:
            if pa[index] == 1 and ma[index] == 1:
                long[index] = 1
            if pa[index] == -1 and ma[index] == -1:
                short[index] = 1
            index += 1
        


        exitLong = [0] * 30
        exitShort = [0] * 30
        index = 0
        while index < 30:
            # long
            if ma[index] < 0:
                exitLong[index] = 1
            elif ma[index] > 0:
                exitLong[index] = 0
            else:
                exitLong[index] = 0
            # short
            if ma[index] > 0:
                exitShort[index] = 1
            elif ma[index] < 0:
                exitShort[index] = 0
            else:
                exitShort[index] = 0
            index += 1
      

        olong = [0] * 30
        oshort = [0] * 30
        index = 28
        while index >= 0:
            # print("long: ", long[index])
            # print("exit: ", exitLong[index])
            # print("olng: ", olong[index])

            if olong[index+1] > 0:
                if exitLong[index] == 1:
                    olong[index] = 0
                else:
                    olong[index] =  olong[index+1] + 1
            elif long[index] > 0:
                olong[index] = 1
            else:
                olong[index] = 0

            if oshort[index+1] > 0:
                if exitShort[index] == 1:
                    oshort[index] = 0
                else:
                    oshort[index] = oshort[index+1] + 1
            elif short[index] > 0:
                oshort[index] = 1
            else:
                oshort[index] = 0

            index -= 1

        data = [{'SHORT': False, 'END SHORT': False, 'is_hot': False, 'is_cold': False}]
        sign = pandas.DataFrame(data)

        if oshort[0] == 1:
            sign['SHORT'] = True
            sign['is_hot'] = True
        if oshort[1] > 0 and oshort[0] == 0:
            sign['END SHORT'] = True
            sign['is_cold'] = True


        return sign