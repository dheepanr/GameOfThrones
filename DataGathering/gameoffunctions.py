# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 20:46:55 2015

@author: dheepan.ramanan
"""

from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from selenium import webdriver
import requests as rq
import sys


#sys.setrecursionlimit(1500)

def gotThrones(season):
    url = 'http://genius.com/albums/Game-of-thrones/Season-'+str(season)+'-scripts'
    r = rq.get(url)
    b = bs(r.text)
    episodedict={}    

    episodecontainer = b.find('ul', attrs={'class':'song_list primary_list has_track_order'})
    eplinks = episodecontainer.findAll('a')
    for link in eplinks:
        if re.search('\(.*\)',link['title']): #avoid unedited scripts
            pass
        else:
            epurl = link['href']
            eptitle = link['title']
            episodedict[eptitle] = epurl
    return episodedict
    
    
        

def episodeScraper(ep):
	driver = webdriver.PhantomJS('/Users/dheepan.ramanan/Documents/Resources/phantomjs-2.1.1-macosx/bin/phantomjs')
	driver.get(ep)
	b = bs(driver.page_source,'html.parser')
	charactercollection=[]
	body = b.find('div', attrs={'class' : 'lyrics'})
	dialogue = re.split('\n', body.text)
	episode = re.sub('by.*','',ep)
	pattern = re.complile(r'[^A-Z.\s:]')
	state = 0
	count = 0
	for line in dialogue:
                if line == '':
                    pass
                else:
		         m = re.search(pattern,line)
			if m == None:
                        setting = line
                        state = 1
                        count +=1									
                    else:
                        if state:
                            character = re.sub('\(.*\)','', line.split(':',1)[0])
                            sentences = line.split(':')[1]
                            charactercollection.append([episode,character,sentences,len(sentences),setting,count])                        
                    except IndexError:
                        character = "ACTION"
                        if re.match(r'(\[)(.*)(\])$',line):
                            try:
                                regexline = re.match(r'(\[)(.*)(\])$',line)
                                sentences = regexline.group(2)
                                charactercollection.append([episode,character,sentences,len(sentences)])
                                
                            except Exception:
                                regexline = re.match(r'(\[)(.*)',line)
                                sentences = regexline.group(2)
                                charactercollection.append([episode,character,sentences,len(sentences)])
	return charactercollection									
																																
	
            
