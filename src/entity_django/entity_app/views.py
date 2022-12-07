from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models.functions import Length
from .models import *
from .utils import *
from .EntityTagger import *
import gzip
import shutil
import codecs
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
# Create your views here.



def home(request):
    template = loader.get_template('home.html')
#    fitted_model=pickle.load(open('C:/Users/User/OneDrive - University of Glasgow/University Year 4/Individual Project/2464980P-L4-Project/src/entity_django/entity_app/classifier.pkl', 'rb'))
#    fitted_vectorizer=pickle.load(open('C:/Users/User/OneDrive - University of Glasgow/University Year 4/Individual Project/2464980P-L4-Project/src/entity_django/entity_app/vectorizer.pkl', 'rb'))

    documents = Document.objects.all().values()
    entities = Entity.objects.all()

#    for entity in entities:
#        test_feature=fitted_vectorizer.transform([entity.abstract])
#        predicted=fitted_model.predict_proba(test_feature)
#        print(predicted[0])
#        if predicted[0][1]<0.5:
#            entity.sensitivity=1
#        elif 0.5<=predicted[0][1]<0.8:
#            entity.sensitivity=2
#        elif predicted[0][1]>=0.8:
#            entity.sensitivity=3
#        entity.save()

    context = {
        'documents': documents,
    }
    return HttpResponse(template.render(context, request))

def list_documents(request):
    template = loader.get_template('list_documents.html')
    documents = Document.objects.all().values()
    tempfilenames = list(Document.objects.all().values_list('filename', flat=True))
    filenames = [filename.replace(".html.gz","") for filename in tempfilenames]

    context = {
        'documents': zip(documents,filenames),
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
    docname = doc.filename.replace(".html.gz","")
    chart = get_chart(docid)
    try:
        inst_ent = Instance.objects.filter(instanceID=instid)[0].entityID
        similar_docs = list(set(Instance.objects.filter(entityID=inst_ent).values_list('documentID', flat=True)))
        similar_docs = [Document.objects.filter(documentID=docid)[0] for docid in similar_docs]
    except:
        similar_docs = []
    print(similar_docs)

    context = {
        'docid': docid,
        'doc': doc,
        'chart': chart,
        'docname' : docname,
        'indexed' : indexed,
        'documents' : documents,
        'similar_docs' : similar_docs,
    }
    return HttpResponse(template.render(context, request))

def document_analytics(request, docid):
    template = loader.get_template('document_analytics.html')
    doc = Document.objects.filter(documentID=docid)[0]
    docname = doc.filename.replace(".html.gz","")
    chart = get_chart(docid)
    context = {
        'docid': docid,
        'doc' : doc,
        'docname' : docname,
        'chart' : chart
    }
    return HttpResponse(template.render(context, request))

def delete_document(request, docid):
    Document.objects.filter(documentID=docid).delete()
    return HttpResponseRedirect(reverse(home))

def add_document(request):
    if request.method == 'POST':
        print(request.FILES.getlist('file'))
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
            entity = Entity.objects.create(entityID=URL, abstract=abstract)
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
        indexed.append(text[instance.start:instance.stop])
        prev=instance.stop
    inst_ids.append("")
    abstracts.append("")
    indexed.append(text[prev:])
    return zip(indexed, abstracts, colors, inst_ids)




