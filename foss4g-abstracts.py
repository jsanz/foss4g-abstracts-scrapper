# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

URL='https://talks.osgeo.org/foss4g-2022/p/voting/talks'
PAGES=21

def is_checked(tag):
  return tag.has_attr('checked')

def processPage(foss4gid, page):
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
