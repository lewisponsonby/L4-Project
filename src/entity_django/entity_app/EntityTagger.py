import spacy
import spacy_dbpedia_spotlight
import numpy as np
from bs4 import BeautifulSoup
import requests

nlp = spacy.load('en_core_web_lg')
nlp.add_pipe('dbpedia_spotlight',last=True)

def entityTagger(text):
    doc=nlp(text)
    entities = []
    for ent in doc.ents:
        try:
            URL = ent._.dbpedia_raw_result['@URI']
            start = int(ent._.dbpedia_raw_result['@offset'])
            end = int(ent._.dbpedia_raw_result['@offset']) + len(ent._.dbpedia_raw_result['@surfaceForm'])
            entities.append([URL, start, end])
        except:
            continue
    return entities

def getAbstract(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    abstract = soup.find('p', class_="lead").getText()
    return abstract




