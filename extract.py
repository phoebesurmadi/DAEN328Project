from pytrends.request import TrendReq
import pandas as pd

# Initialize Pytrends with a retry session
pytrends = TrendReq(hl='en-US', tz=360)

# test words
kw_list = ["Excel", "Microsoft"]
pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')

#test
data = pytrends.interest_over_time()


data.head()












