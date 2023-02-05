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
import gensim
# Create your views here.




def home(request):
    template = loader.get_template('home.html')
    documents = Document.objects.all().values()

    context = {
        'documents': documents,
    }
    return HttpResponse(template.render(context, request))

def list_documents(request):
    template = loader.get_template('list_documents.html')
    documents = Document.objects.all()[:50]

    top_entities=[]
    for doc in documents:
        instances=list(Instance.objects.filter(documentID=doc).values_list('entityID', flat=True))
        entities=Entity.objects.filter(entityID__in=instances).order_by('-sensitivity')

        if len(entities)>=3:
            entities=entities[:3]
            ent_urls = [entity.entityID.replace("http://dbpedia.org/resource/","") for entity in entities]
            top_entities.append(zip(entities, ent_urls))
        else:
            ent_urls = [entity.entityID.replace("http://dbpedia.org/resource/","") for entity in entities]
            top_entities.append(zip(entities, ent_urls))


    context = {
        'documents': zip(documents,top_entities),
    }
    return HttpResponse(template.render(context, request))

def upload_document(request):
    template = loader.get_template('upload.html')
    documents = Document.objects.all().values()
    context = {
        'documents' : documents,
    }
    return HttpResponse(template.render(context, request))

def view_document(request, docid, instid=""):
    documents = Document.objects.all().values()
    doc = Document.objects.filter(documentID=docid)[0]
    indexed = split_entities(docid,doc)
    template = loader.get_template('documents.html')

    instances = Instance.objects.filter(documentID=docid)
    entities = []
    colors = {}

    for instance in instances:
        entity_name = instance.entityID.text
        entities.append(entity_name)
        colors[entity_name] = instance.entityID.sensitivity

    counter = dict(Counter(entities).most_common(7))
    color = [colors[key] for key in counter.keys()]
    for i in range(len(color)):
        if color[i] == 1:
            color[i] = 'green'

        if color[i] == 2:
            color[i] = 'orange'

        if color[i] == 3:
            color[i] = 'red'

    counter_ = dict(Counter(entities))
    color_ = [colors[key] for key in counter_.keys()]
    color_counter=dict(Counter(color_))
    color_freqs=list(color_counter.values())
    color_vals = list(map(lambda x: str(x).replace('1', 'green').replace('2','orange').replace('3','red'), list(color_counter.keys())))
    color_keys = list(map(lambda x: str(x).replace('green', 'Low Sensitivity Entites').replace('orange', 'Moderate Sensitivity Entities').replace('red', 'High Sensitivity Entities'), color_vals))

    fig_ents=list((counter.keys()))
    fig_freqs=list((counter.values()))
    colors=list((color))

    print(color_freqs,color_vals,color_keys)
    print(color_counter)



    context = {
        'docid': docid,
        'doc': doc,
        'indexed' : indexed,
        'fig_ents' : fig_ents,
        'fig_freqs' : fig_freqs,
        'color' : colors,
        'color_freqs' : color_freqs,
        'color_vals' : color_vals,
        'color_keys' : color_keys,
    }
    return HttpResponse(template.render(context, request))

def corpus_analytics(request):
    template = loader.get_template('corpus_analytics.html')
    if not TopicWord.objects.all():
        generateLDA()
    topics=[]

    max_topics=TopicWord.objects.all().order_by('-topicNumber')[0].topicNumber

    for i in range(1,max_topics+1):
        topic_words=list(TopicWord.objects.filter(topicNumber=i).order_by('-weight'))
        topic_docs=list(TopicDocument.objects.filter(topicNumber=i).order_by('-weight'))
        topics.append(zip(topic_words,topic_docs))



    context = {
        'topics' : topics,
    }
    return HttpResponse(template.render(context, request))

def regenerate_lda(request):
    generateLDA(8,7)
    print("regenerated")
    return HttpResponseRedirect(reverse(corpus_analytics))

def delete_document(request, docid):
    Document.objects.filter(documentID=docid).delete()
    return HttpResponseRedirect(reverse(home))

def add_document(request):
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

def analyse_document(document):
    fitted_model=pickle.load(open('C:/Users/User/OneDrive - University of Glasgow/University Year 4/Individual Project/2464980P-L4-Project/src/entity_django/entity_app/classifier.pkl', 'rb'))
    fitted_vectorizer=pickle.load(open('C:/Users/User/OneDrive - University of Glasgow/University Year 4/Individual Project/2464980P-L4-Project/src/entity_django/entity_app/vectorizer.pkl', 'rb'))

    entities=entityTagger(document.text)
    documentID=document.documentID
    for entity_instance in entities:
        URL=entity_instance[0]
        start=entity_instance[1]
        stop=entity_instance[2]
        all_URLs=Entity.objects.all().values_list('entityID', flat=True)
        if URL not in all_URLs:
            abstract = getAbstract(URL)
            entity = Entity.objects.create(entityID=URL, abstract=abstract, text=URL.replace("http://dbpedia.org/resource/","").replace("_"," "))
            test_feature=fitted_vectorizer.transform([entity.abstract])
            predicted=fitted_model.predict_proba(test_feature)
            if predicted[0][1]<0.5:
                entity.sensitivity=1
            elif 0.5<=predicted[0][1]<0.8:
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


def split_entities(docid,doc):
    instances=Instance.objects.filter(documentID=docid).order_by('start')
    text=doc.text
    indexed=[]
    abstracts=[]
    colors=[]
    inst_ids=[]
    prev=0
    for instance in instances:
        inst_ids.append("")
        inst_ids.append(str(instance).split(" ")[-1].replace("(","").replace(")",""))
        abstracts.append("")
        abstracts.append(instance.entityID.abstract)
        colors.append(0)
        colors.append(instance.entityID.sensitivity)
        indexed.append(text[prev:instance.start])
        indexed.append(text[instance.start:instance.stop].upper())
        prev=instance.stop
    inst_ids.append("")
    abstracts.append("")
    indexed.append(text[prev:])
    started=False
    for item in indexed[0].split("\n"):
        if "classified" in item or "unclassified" in item or "secret" in item:
            if not started:
                indexed[0]=""
                started=True
            elif started:
                indexed[0]+=item
    return zip(indexed, abstracts, colors, inst_ids)


def generateLDA(n_topics=8,n_words=5):
    TopicWord.objects.all().delete()
    tokens = []
    docs = list(Document.objects.values_list('tokens', flat=True))
    for doc in docs:
        if doc != None:
            tokens.append(doc)



    jsonDec = json.decoder.JSONDecoder()
    data_words = [jsonDec.decode(doc) for doc in tokens]

    id2word = corpora.Dictionary(data_words)

    corpus = [id2word.doc2bow(text) for text in data_words]

    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                               id2word=id2word,
                                               num_topics=n_topics,
                                               update_every=1,
                                               chunksize=10,
                                               passes=100,
                                               alpha='auto',
                                               iterations=200,
                                               per_word_topics=True)

    topics = lda_model.show_topics(num_topics=n_topics, num_words=n_words, formatted=True)

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
    docs_per_topic = [[] for _ in all_topics]

    for doc_id, doc_bow in enumerate(corpus):
        doc_topics = lda_model.get_document_topics(doc_bow)
        for topic_id, score in doc_topics:
            docs_per_topic[topic_id].append((doc_id, score))

    for doc_list in docs_per_topic:
        doc_list.sort(key=lambda id_and_score: id_and_score[1], reverse=True)

    for topic_num in range(n_topics):
        for doc_num in range(n_words):
            print(topic_num,doc_num)
            doc_json = json.dumps(data_words[docs_per_topic[topic_num][doc_num][0]])
            doc_weight = docs_per_topic[topic_num][doc_num][1]
            top_document = Document.objects.filter(tokens=doc_json)[0]
            topicDocument = TopicDocument.objects.create(documentID=top_document, topicNumber=topic_num+1, weight=doc_weight)





