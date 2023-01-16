# run this script once a month to download data incrementally

from defillama2 import DefiLlama
from datetime import date, datetime,  timedelta
import os

obj = DefiLlama()

# get the prices of the following tokens from the corresponding chains/sources
# note that token address can be in either lower or upper case. 
dd = {'0xE5417Af564e4bFDA1c483642db72007871397896':'polygon',  # GNS on polygon
      '0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a':'arbitrum', # GMX on arbitrum
      '0x62edc0692BD897D2295872a9FFCac5425011c661':'avax',  # GMX on avalanche
      }

# use today as the end of data download period.
# use the last date of download + 1 day as start if we ran this script before 
# otherwise, use '2021-11-02' as start since that's the earliest available date 
# for GNS and GMX was available earlier.
date_format = '%Y-%m-%d'
today = date.today().strftime(date_format)
if os.path.exists('data'):
    fnames = os.listdir('data')
    dates = [
        datetime.strptime(fnm.replace('open_prices_', '').replace('.pkl', ''),
                          date_format) 
        for fnm in fnames if fnm != '.DS_Store']
    start = max(dates) + timedelta(days=1)
    start = start.strftime(date_format)
else: 
    start = '2021-11-02'

# much faster now, but still will save downloaded data on disk and have the app call it. 
df = obj.get_daily_open_close(dd, start, today, 'open')

# show price data
df = df.dropna()
# df.head()
# df.tail()

# save
os.makedirs('data', exist_ok=True)
last_avail_date = df.index[-1].strftime(date_format)
fname = 'open_prices_' + last_avail_date + '.pkl'
df.to_pickle("data/" + fname)