from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models.functions import Length
from .models import *
from .utils import *
from .EntityTagger import *
import gzip
import json
import shutil
import codecs
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import nltk
from nltk.corpus import stopwords
import re
import gensim.corpora as corpora
import random
import gensim
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime

global LOG_ID
LOG_ID="ServerLog.txt"



def home(request): # Homepage
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" Home\n")

    template = loader.get_template('home.html') # Retrieve template for homepage
    context = {
    }
    return HttpResponse(template.render(context, request)) # Render template & context


def user_study(request): # Homepage
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" UserStudy\n")

    template = loader.get_template('user_study.html') # Retrieve template for user study page
    context = {
    }
    return HttpResponse(template.render(context, request)) # Render template & context

def add_qanswer(request,qid): # Processing answer upload
    if request.method == 'POST':
        print(request.POST)
        try:
            global LOG_ID
            LOG_ID=request.POST["LOG_ID"]
            with open(LOG_ID, "a+") as ServerLog:
                ServerLog.write(LOG_ID+" START\n")
        except:
            answer = request.POST[qid]
            with open(LOG_ID, "a+") as ServerLog:
                ServerLog.write(str(datetime.now())[:19] + " "+qid+":"+answer+"\n")
    return HttpResponseRedirect(reverse(user_study))

def list_documents(request): # List Documents
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" ListDocuments\n")


    template = loader.get_template('list_documents.html') # Retrieve template for list documents page
    documents = Document.objects.all()[:50] # Retrieve all documents to be listed (capped at fifty during development)

    top_entities=[]
    for doc in documents: # For each document
        instances=list(Instance.objects.filter(documentID=doc).values_list('entityID', flat=True)) # Get all entity instances in document
        entities=Entity.objects.filter(entityID__in=instances).order_by('-sensitivity') # Get all distinct entities featuring in document and sort by sensitivity
        ent_urls = [entity.text for entity in entities]
        top_entities.append(zip(entities, ent_urls))


    context = {
        'documents': zip(documents,top_entities), # Pass document & corresponding top entities as context
    }
    return HttpResponse(template.render(context, request)) # Render template & context


def list_entities(request): # List Entities
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" ListEntities\n")

    template = loader.get_template('list_entities.html') # Retrieve list entities template
    entities = Entity.objects.all()[:50] # Retrieve all entities (capped at fifty during development)

    ent_docs=[]
    for entity in entities: # For each entity
        ent_docids = Instance.objects.filter(entityID=entity).values_list('documentID', flat=True) # Retrieve all documents it appears in
        ent_docs.append(list(set(Document.objects.filter(documentID__in=ent_docids)))) # Record the Document IDs

    context = {
        'entities': zip(entities,ent_docs), # Pass entity & corresponding documents as context
    }
    return HttpResponse(template.render(context, request)) # Render template & context

def view_entity(request, entid): # View Individual Entity
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" ViewEntity:"+str(entid)+"\n")

    template = loader.get_template('entity.html') # Retrieve individual entity template
    ent = Entity.objects.filter(slug=entid)[0] # Retrieve the entity's slug
    ent_docids = Instance.objects.filter(entityID=ent).values_list('documentID', flat=True)
    ent_docs=(list(set(Document.objects.filter(documentID__in=ent_docids)))) # Retrieve all IDs of the documents the entity appears in
    context = {
        'ent' : ent, # Pass the entity's slug
        'ent_docs' : ent_docs, # and its corresponding documents as context
    }
    return HttpResponse(template.render(context, request)) # Render template & context

def upload_document(request): #Upload Document
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" UploadDocument\n")

    template = loader.get_template('upload.html') # Retrieve document upload template
    context = {
    }
    return HttpResponse(template.render(context, request)) # Render template & context

def view_document(request, docid): # View Individual Entity
    global LOG_ID

    doc = Document.objects.filter(documentID=docid)[0] # Retrieve the current document instance
    indexed = split_entities(docid,doc) # Retrieve the document split from its entities
    template = loader.get_template('documents.html') # Retrieve the view document template

    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" ViewDocument:"+str(doc.filetitle)+"\n")

    instances = Instance.objects.filter(documentID=docid) # Retrieve all entity instances for the current document
    entities = []
    colors = {}

    for instance in instances: # For each entity instance
        entity_name = instance.entityID.text
        entities.append(entity_name) # Record distinct entities
        colors[entity_name] = instance.entityID.sensitivity # and their sensitivities

    counter = dict(Counter(entities)) # Record the most common entities
    color = [colors[key] for key in counter.keys()] # Create a list of sensitivities of the most common entities
    for i in range(len(color)):
        if color[i] == 1:
            color[i] = 'green'

        if color[i] == 2:
            color[i] = 'orange'

        if color[i] == 3:
            color[i] = 'red'
        ## Change sensitivities for colours


    # Bar chart entity frequency calculations
    counter_ = dict(Counter(entities))
    color_ = [colors[key] for key in counter_.keys()]
    color_counter=dict(Counter(color_))
    color_freqs=list(color_counter.values())
    color_vals = list(map(lambda x: str(x).replace('1', 'green').replace('2','orange').replace('3','red'), list(color_counter.keys())))
    color_keys = list(map(lambda x: str(x).replace('green', 'Low Sensitivity Entites').replace('orange', 'Moderate Sensitivity Entities').replace('red', 'High Sensitivity Entities'), color_vals))

    inst_entids = Instance.objects.filter(documentID=docid).values_list('entityID', flat=True)
    inst_entids = list(set(Entity.objects.filter(entityID__in=inst_entids)))
    inst_entids = sorted(inst_entids, key=lambda ent: ent.sensitivity, reverse=True)
    inst_ents = [inst_entid.text for inst_entid in inst_entids]

    for instance in instances: # For each entity instance
        entity_name = instance.entityID.text
        entities.append(entity_name) # Record distinct entities
        colors[entity_name] = instance.entityID.sensitivity # and their sensitivities

    instances_ = Instance.objects.filter(documentID=docid)
    instances_ = [inst.entityID.text for inst in instances_]
    counter = dict(Counter(instances_))
    fig_freqs = [counter[inst_ent] for inst_ent in inst_ents ]
    color_dict = {1: 'green', 2: 'orange', 3: 'red'}
    colors = [color_dict[inst_entid.sensitivity] for inst_entid in inst_entids] # Create a list of sensitivities of the most common entities
    if len(fig_freqs)>30:
        fig_freqs=fig_freqs[:30]
        colors=colors[:30]
        inst_ents=inst_ents[:30]

    context = {
        'docid': docid,
        'doc': doc,
        'indexed' : indexed,
        'fig_ents' : inst_ents,
        'fig_freqs' : fig_freqs,
        'color' : colors,
        'color_freqs' : color_freqs,
        'color_vals' : color_vals,
        'color_keys' : color_keys,
    }
    return HttpResponse(template.render(context, request))

def corpus_analytics(request): # Corpus Analytics
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" CorpusAnalytics\n")

    template = loader.get_template('corpus_analytics.html')

    #If there are no topics, generate new topics
    if not TopicWord.objects.all():
        generateLDA()
    topics=[]

    #Retrieve the maximum number of topics
    max_topics=TopicWord.objects.all().order_by('-topicNumber')[0].topicNumber
    combined_topics=[]

    #For each topic, retrieve the topic words and topic docs
    for i in range(1,max_topics+1):
        topic_words=list(TopicWord.objects.filter(topicNumber=i).order_by('-weight'))
        topic_docs=list(TopicDocument.objects.filter(topicNumber=i).order_by('-weight'))

        combined=""
        for word in topic_words:
            combined+=word.entityID.abstract+" "
        combined_topics.append(combined)

        # Retrieve the top 8 words
        if len(topic_words)>8:
            topic_words = topic_words[:8]
        colors=[]
        weights=[]
        names=[]
        slugs=[]
        #convert sensitivities to colours
        for word in topic_words:
            if word.entityID.sensitivity==1:
                colors.append('green')
            elif word.entityID.sensitivity==2:
                colors.append('orange')
            elif word.entityID.sensitivity==3:
                colors.append('red')
            else:
                colors.append('grey')
            weights.append(word.weight)
            names.append(word.entityID.text)
            slugs.append(word.entityID.slug)



        topics.append([topic_words,weights,colors,names,slugs])
        topics.append(topic_docs)

    # Calculate the TF-IDF scores for the topic words
    tf_idf, count = c_tf_idf(combined_topics, m=len(combined_topics))

    # Get the top 3 TF-IDF scoring words for each topic
    topic_titles = extract_top_n_words_per_topic(tf_idf, count, combined_topics, n=3)

    context = {
        'topics' : zip(topics,topic_titles),
    }
    return HttpResponse(template.render(context, request))

def regenerate_lda(request): # Regenerating LDA Topics
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" RegenerateLDA\n")
    generateLDA(8,7)
    print("regenerated")
    return HttpResponseRedirect(reverse(corpus_analytics))

def delete_document(request, docid): # Delete Document
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" DeleteDocument "+str(docid)+"\n")

    Document.objects.filter(documentID=docid).delete()
    return HttpResponseRedirect(reverse(home))

def delete_entity(request, entid): # Delete Entity
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" DeleteEntity "+str(entid)+"\n")

    Entity.objects.filter(slug=entid).delete()
    return HttpResponseRedirect(reverse(home))

def add_document(request): # Processing document upload
    global LOG_ID
    with open(LOG_ID, "a+") as ServerLog:
        ServerLog.write(str(datetime.now())[:19]+" ProcessDocumentUpload\n")

    if request.method == 'POST':
        for file2 in request.FILES.getlist('file'):
            file = File.objects.create(txtfile=file2)
            file.save()
            path=str(file.txtfile)
            with gzip.open(path, 'rb') as f:
                lines=f.read()
            soup = BeautifulSoup(lines)
            text = soup.get_text().lower()


            try:
                document = Document.objects.get(filename=file2, text=text)
            except:
                document = Document.objects.create(filename=file2, text=text)
                print("about to analyse")
                analyse_document(document)
                print("analysed")
                tokens=[]
                instances = Instance.objects.filter(documentID=document)
                for instance in instances:
                    tokens.append(instance.entityID.entityID)
                document.tokens=json.dumps(tokens)
                document.save()
    return HttpResponseRedirect(reverse(home))

def analyse_document(document): # Analysing document for entities and creating instances
    fitted_model=pickle.load(open('classifier.pkl', 'rb'))
    fitted_vectorizer=pickle.load(open('vectorizer.pkl', 'rb'))

    entities=entityTagger(document.text)
    documentID=document.documentID
    for entity_instance in entities: #For each entity instance, get its details
        URL=entity_instance[0]
        start=entity_instance[1]
        stop=entity_instance[2]
        all_URLs=Entity.objects.all().values_list('entityID', flat=True)
        if URL not in all_URLs: # If entity does not exist in DB, create it
            abstract = getAbstract(URL)
            entity = Entity.objects.create(entityID=URL, abstract=abstract, text=URL.replace("http://dbpedia.org/resource/","").replace("_"," "), slug=URL.replace("http://dbpedia.org/resource/",""))
            test_feature=fitted_vectorizer.transform([entity.abstract]) # Extract features from entity abstract
            predicted=fitted_model.predict_proba(test_feature) # Predict entity sensitivity from abstract features
            print(entity.text,predicted)
            if predicted[0][1]<0.4: # Thresholds for sensitivity scoring
                entity.sensitivity=1
            elif 0.4<=predicted[0][1]<0.8:
                entity.sensitivity=2
            elif predicted[0][1]>=0.8:
                entity.sensitivity=3
            print("created entity")
            entity.save()
        else:
            entity = Entity.objects.get(entityID=URL)
            print("got entity")
        try:
            instance = Instance.objects.get(documentID=document, entityID=entity, start=start, stop=stop)
            print("got instance")
        except:
            instance = Instance.objects.create(documentID=document, entityID=entity, start=start, stop=stop)
            print("created instance")
    print("analysing in function done")
    return 1


def split_entities(docid,doc): # Splitting documents into entities for HTML display
    instances=Instance.objects.filter(documentID=docid).order_by('start')
    text=doc.text
    indexed=[]
    abstracts=[]
    colors=[]
    ent_ids=[]
    prev=0
    for instance in instances:
        ent_ids.append("")
        ent_ids.append(instance.entityID)
        abstracts.append("")
        abstracts.append(instance.entityID.abstract)
        colors.append(0)
        colors.append(instance.entityID.sensitivity)
        indexed.append(text[prev:instance.start])
        indexed.append(text[instance.start:instance.stop].upper())
        prev=instance.stop
    ent_ids.append("")
    abstracts.append("")
    indexed.append(text[prev:])
    started=False
    for item in indexed[0].split("\n"):
        #if "classified" in item or "unclassified" in item or "secret" in item or "confidential" in item:
        if not started:
            indexed[0]=""
            started=True
        elif started:
            indexed[0]+=item
    return zip(indexed, abstracts, colors, ent_ids)


def generateLDA(n_topics=8,n_words=5): # Regenerating LDA Topics
    TopicWord.objects.all().delete()
    TopicDocument.objects.all().delete() # Delete existing topics and words
    tokens = []
    docs = list(Document.objects.values_list('tokens', flat=True)) # Get all documents
    for doc in docs:
        if doc != None:
            tokens.append(doc)

    jsonDec = json.decoder.JSONDecoder()
    data_words = [jsonDec.decode(doc) for doc in tokens] # Get tokens from corpus

    id2word = corpora.Dictionary(data_words) # Convert tokens to ids

    corpus = [id2word.doc2bow(text) for text in data_words] # Create bag of words

    # Generate LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                               id2word=id2word,
                                               num_topics=n_topics,
                                               update_every=1,
                                               chunksize=10,
                                               passes=100,
                                               alpha='auto',
                                               iterations=300,
                                               per_word_topics=True)

    # Output LDA topics
    topics = lda_model.show_topics(num_topics=n_topics, num_words=50, formatted=True)

    # For each topic string, reformat it into variables
    for index, topic in enumerate(topics):
        topic_split=topic[1].split("+")
        for topic_word in topic_split:
            item=topic_word.split("*")
            score=float(item[0].replace('"',"").replace(" ",""))
            url=item[1].replace('"',"").replace(" ","")
            entity=Entity.objects.filter(entityID=url)[0]
            topicWord = TopicWord.objects.create(entityID=entity, topicNumber=index+1, weight=score)

    for i in range(1,n_topics):
        for topicWord in TopicWord.objects.filter(topicNumber=i).order_by('-weight'):
            print(topicWord.topicNumber,topicWord.entityID,topicWord.weight)



    all_topics=lda_model.print_topics()
    lda_model.print_topics()
    docs_per_topic = [[] for _ in all_topics]

    # Get topic words
    for doc_id, doc_bow in enumerate(corpus):
        doc_topics = lda_model.get_document_topics(doc_bow)
        for topic_id, score in doc_topics:
            docs_per_topic[topic_id].append((doc_id, score))

    # Get top scoring documents
    for doc_list in docs_per_topic:
        doc_list.sort(key=lambda id_and_score: id_and_score[1], reverse=True)

    for topic_num in range(n_topics):
        for doc_num in range(12):
            doc_json = json.dumps(data_words[docs_per_topic[topic_num][doc_num][0]])
            doc_weight = docs_per_topic[topic_num][doc_num][1]
            top_document = Document.objects.filter(tokens=doc_json)[0]
            topicDocument = TopicDocument.objects.create(documentID=top_document, topicNumber=topic_num+1, weight=doc_weight)


def c_tf_idf(documents, m, ngram_range=(1, 1)): # Creating TF-IDF counts for each document (entity abstract)
    count = CountVectorizer(ngram_range=ngram_range, stop_words="english").fit(documents)
    t = count.transform(documents).toarray()
    w = t.sum(axis=1)
    tf = np.divide(t.T, w)
    sum_t = t.sum(axis=0)
    idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
    tf_idf = np.multiply(tf, idf)
    return tf_idf, count

def extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n): # Extracting the top words for each topic
    words = count.get_feature_names()
    labels = [1,2,3,4,5,6,7,8]
    tf_idf_transposed = tf_idf.T
    indices = tf_idf_transposed.argsort()[:, -n:]
    top_n_words = {label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1] for i, label in enumerate(labels)}
    top_n_words=list(top_n_words.values())
    topic_titles=[]
    for topic in top_n_words:
        topic_titles.append(topic[0][0]+"-"+topic[1][0]+"-"+topic[2][0])
        topic_titles.append("")
    return topic_titles

def repredictEntities(): # Repredicting all entities (for admin use)
    fitted_model=pickle.load(open('classifier.pkl', 'rb'))
    fitted_vectorizer=pickle.load(open('vectorizer.pkl', 'rb'))

    for entity in Entity.objects.all():
        test_feature = fitted_vectorizer.transform([entity.abstract])
        predicted = fitted_model.predict_proba(test_feature)
        print(predicted)
        if predicted[0][1] < 0.4:
            entity.sensitivity = 1
        elif 0.4 <= predicted[0][1] < 0.8:
            entity.sensitivity = 2
        elif predicted[0][1] >= 0.8:
            entity.sensitivity = 3
        entity.save()