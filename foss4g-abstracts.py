# -*- coding: utf-8 -*-
from asyncio.log import logger
import os
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import logging


logging.basicConfig(level=logging.WARN,format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

URL=os.getenv('FOSS4G_URL', default='https://talks.osgeo.org/foss4g-2022/p/voting/talks')
PAGES=int(os.getenv('FOSS4G_PAGES',default='21'))

logger = logging.getLogger(__name__)

loggingLevel = logging.DEBUG if os.getenv('FLASK_ENV') == 'development' else logging.INFO
logger.setLevel(loggingLevel)

logger.debug(f'URL={URL}')
logger.debug(f'PAGES={PAGES}')

def is_checked(tag):
  return tag.has_attr('checked')

def processPage(foss4gid, page):
  logger.debug(f'Processing page {page} for {foss4gid}')
  url = f'{URL}/{foss4gid}?'
  r = requests.get(url=url,params={'page': page})
  soup = BeautifulSoup(r.text, 'html.parser')
  cards = soup.find_all('div', class_="submission-card")
  abstracts = []
  for card in cards:
    abstract = {'page': page}
    abstract['title'] = card.find('h3').text

    html_tags = filter(lambda x: x != '\n',card.find('div', class_='card-text').children)
    abstract['html'] = ''.join(map(lambda x : str(x), html_tags))

    checked = card.find_all(is_checked)
    abstract['score'] = int(checked[0]['value']) if len(checked) == 1  else  None

    abstracts.append(abstract)
  if len(abstracts) == 0:
      raise Exception("No abstracts retreived")
  return abstracts

def flatten(t):
    return [item for sublist in t for item in sublist]

def getAbstracts(foss4gid):
    return flatten([processPage(foss4gid, page) for page in range(1,PAGES)])

app = Flask(__name__)

@app.route('/')
def foss4gid():
    foss4gid = request.args.get("foss4gid")
    try:
        abstracts = getAbstracts(foss4gid) if foss4gid else None
        error = None
    except Exception:
        abstracts = None
        error = True
    return render_template('foss4g-abstracts.html', 
      url = f'{URL}/{foss4gid}',
      foss4gid=foss4gid, 
      abstracts=abstracts, 
      error=error)
