# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 18:26:41 2016

@author: dheepan.ramanan
"""

import pandas as pd 
from realtimeVerbatim import realtime_request
import time
import re

GOTdf = pd.read_excel('/Users/dheepan.ramanan/Documents/GameOfThrones/DataGathering/GOTlines.xlsx')
GOTdf['EpisodeNumber'] = int()
GOTdf['SeasonSceneCount'] = int()

#getmaxes 
maxLocales = GOTdf.groupby('episode').max()
settingCounts = maxLocales.reset_index()[['episode','settingcount']]
settingCounts['episodeNumber'] = [8,3,5,10,9,7,2,4,1,6]
settingCounts = settingCounts.sort('episodeNumber',ascending=True)

episodes = settingCounts.episode.tolist()
episodecount = settingCounts['episodeNumber'].tolist()
settingcount = settingCounts.settingcount.tolist()

episodes.pop(0)
episodecount.pop(0)
settingcount.pop(9)

cumSum = pd.DataFrame(zip(episodes,settingcount,episodecount), columns=['episode','settingcount','episodecount'])
cumSum['totals'] = cumSum['settingcount'].cumsum()
Wars2come = pd.DataFrame(['The Wars to Come Script ',0,1,0]).T
Wars2come.columns=['episode','settingcount','episodecount','totals']

cumSum = cumSum.append(Wars2come)
lookup = cumSum.set_index('episode').to_dict(orient='index')

GOTdf['SeasonSceneCount'] = GOTdf['settingcount'] + GOTdf['episode'].apply(lambda x: lookup[x]['totals'])
GOTdf['EpisodeNumber'] = GOTdf['episode'].apply(lambda x: lookup[x]['episodecount'])
GOTdf.columns = ['EpisodeName','Character','Line','LineLength','Setting','SettingCountEpisode','EpisodeNumber','SeasonSceneCount']

GOTdf['EpisodeName'] = GOTdf['EpisodeName'].astype('category')
GOTdf['Source'] = 'Game Of Thrones'
GOTdf['Season'] = 5

dialogue = GOTdf['Line'].tolist()
sentiment =[]
for l in dialogue:
	try:
		sentscore = float(realtime_request('Movie Reviews','emotions',l.encode('ascii','ignore')))
		time.sleep(1)	
		print l, sentscore
		sentiment.append(sentscore)
	except Exception:
		time.sleep(3)
		sentscore = float(realtime_request('Movie Reviews','emotions',l.encode('ascii','ignore')))
		time.sleep(1)	
		print l, sentscore
		sentiment.append(sentscore)
GOTdfSentiment = pd.DataFrame(sentiment, columns=['Sentiment'])
GOTdf2 = GOTdf.copy().reset_index()

questionmark = re.compile(r'(\?)')
exclamationmark = re.compile(r'(!)')

GOTdf2['QuestionCount'] = GOTdf2['Line'].apply(lambda x: len(re.findall(questionmark,x)))
GOTdf2['ExclamationCount'] = GOTdf2['Line'].apply(lambda x: len(re.findall(exclamationmark,x)))
GOTdf2 = GOTdf.sort(columns=['EpisodeNumber','SettingCountEpisode'])
GOTdf2 = GOTdf2.join(GOTdfSentiment)

def weighted_sentiment(setting,GOTdf):
	resizeddf = GOTdf.loc[GOTdf['Setting']==setting]
	sentimentagg = resizeddf['Sentiment'] * resizeddf['LineLength']
	lineagg = resizeddf['LineLength'].sum()
	weighted_sentiment = sentimentagg.sum()/lineagg
	return weighted_sentiment

def weighted_punc_score(setting, GOTdf):
	resizeddf = GOTdf.loc[GOTdf['Setting']==setting]
	exclamationtotal = resizeddf['ExclamationCount'].sum().astype('float')
	questiontotal = resizeddf['QuestionCount'].sum().astype('float')
	if exclamationtotal == 0:
		exclamationtotal = 1
		questiontotal = questiontotal + 1
	if questiontotal == 0:
		questiontotal =1
		exclamationtotal = exclamationtotal + 1
	ratio = exclamationtotal/questiontotal
	return ratio

def scene_length(setting, GOTdf):
	resizeddf = GOTdf.loc[GOTdf['Setting']==setting]
	numLines = resizeddf['Line'].count()
	return numLines

GOTdf2['WeightedSentiment'] = GOTdf2['Setting'].apply(lambda x: weighted_sentiment(x,GOTdf2))
GOTdf2['WeightedPuncRatio'] = GOTdf2['Setting'].apply(lambda x: weighted_punc_score(x,GOTdf2))
GOTdf2['SceneLength'] = GOTdf2['Setting'].apply(lambda x: scene_length(x,GOTdf2))
GOTdf2 = GOTdf2.sort(['EpisodeNumber','SettingCountEpisode'])
GOTdf2.to_excel('GOTlinesDF.xlsx')
