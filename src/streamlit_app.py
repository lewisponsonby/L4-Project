import spacy
from spacy_streamlit import visualize_ner

nlp = spacy.load("en_core_web_sm")
doc = nlp("Sundar Pichai is the CEO of Google.")
visualize_ner(doc, labels=nlp.get_pipe("ner").labels)
