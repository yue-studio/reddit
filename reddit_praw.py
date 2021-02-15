# Install these modules
#!pip install yfinance
#!pip install praw
#!pip install vaderSentiment

import praw
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf

reddit = praw.Reddit(
    client_id='<YOUR CLIENT ID>',
    client_secret='<YOUR_CLIENT_SECRET>',
    user_agent='<USER_AGENT>'
# Need this option to mute the warnings when running in colab
    check_for_async=False
)

print(reddit.read_only)  # Output: True

def getSIA(text):
  sia = SentimentIntensityAnalyzer()
  sentiment = sia.polarity_scores(text)
  return sentiment

symbols = set([])
d = {}
senti = {}

# get the top 20 hot topics 
for submission in reddit.subreddit("wallstreetbets").hot(limit=20):
    print(submission.title, '-', submission.url)
    submission.comments.replace_more(limit=0)
    for top_level_comment in submission.comments:
# get the senitment of the comment
        s = getSIA(top_level_comment.body.strip())
  
# using regex( findall() ) to extract words from string 
# Assuming word in caps or starts with $ is most likely to be a stock symbol
        res = re.findall(r'\$*[A-Z]{2,4}\s+', top_level_comment.body) 
        for i in res:
            w = i.strip().replace("$","")
            symbols.add(w)
            if w in d.keys():
               d[w] += 1
               senti[w]['neg'] += s['neg']
               senti[w]['neu'] += s['neu']
               senti[w]['pos'] += s['pos']
               senti[w]['compound'] += s['compound']
            else:
               d[w] = 1
               senti[w] = {}
               senti[w]['neg'] = s['neg']
               senti[w]['neu'] = s['neu']
               senti[w]['pos'] = s['pos']
               senti[w]['compound'] = s['compound']

    print('*******************===========================*********************************')

# list of words that are not stock symbols
junkWords = ['WSB','YOLO','TO','RH','AM','ER','OP','GO','CEO','SEC','YOU','AND','HAVE','THEY','FOMO','TAKE','FUD','USA','CNBC','BUY','FIRE','WE', \
             'THE','ON','IS','IN','IM','BUT','FOR', 'ARE','BE','KING', 'HF', 'DFV', 'DD', 'IT', 'HOLD','OF','US','MY','LETS','GET','BACK','WEED', \
             'STOP','THAT','THIS','DO','NOT','FUCK','GANG','ALL']

print("cnt symbol   neg   neu   pos  comp       bid/ask         52wks Low-Hi     volume today/avg/ratio")
for w in sorted(d, key=d.get, reverse=True):
    if ((w not in junkWords) and (d[w] > 5)):
# get the stock quote from yahoo finance 
       quote = yf.Ticker(w)
       try:
           print("%3d  %4s  %5.2f %5.2f %5.2f %5.2f  %7.2f -%7.2f  %7.2f -%7.2f  %d/%d//%f" % \
                 (d[w], w, senti[w]['neg'],senti[w]['neu'],senti[w]['pos'],senti[w]['compound'], \
                  quote.info['bid'], quote.info['ask'], quote.info['fiftyTwoWeekLow'], \
                  quote.info['fiftyTwoWeekHigh'],quote.info['volume'], \
                  quote.info['averageDailyVolume10Day'], \
                  (quote.info['volume']/quote.info['averageDailyVolume10Day'])))
# Prints the symbol and its no of occurances whenever these errors are raised 
       except (KeyError, ValueError, ZeroDivisionError, IndexError) :
           print(w, d[w])
