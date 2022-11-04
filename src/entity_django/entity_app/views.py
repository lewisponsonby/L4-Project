from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from .EntityTagger import *
import gzip
import shutil
import codecs
from bs4 import BeautifulSoup
# Create your views here.


def home(request):
    template = loader.get_template('home.html')
    documents = Document.objects.all().values()
    context = {
        'documents': documents,
    }
    return HttpResponse(template.render(context, request))

def upload_document(request):
    template = loader.get_template('upload.html')
    documents = Document.objects.all().values()
    context = {
        'documents' : documents,
    }
    return HttpResponse(template.render(context, request))

def view_document(request, docid):
    documents = Document.objects.all().values()
    doc = Document.objects.filter(documentID=docid)[0]
    indexed = split_entities(docid,doc)
    template = loader.get_template('documents.html')
    context = {
        'docid': docid,
        'doc': doc,
        'indexed' : indexed,
        'documents' : documents,
    }
    return HttpResponse(template.render(context, request))

def add_document(request):
    if request.method == 'POST':
        file2=request.FILES['file']
        file = File.objects.create(txtfile=file2)
        file.save()

    path=str(file.txtfile)

    with open(path, 'rb') as f:
        lines=f.read()

    soup = BeautifulSoup(lines)
    text = soup.get_text()


    try:
        document = Document.objects.get(filename=file2, text=text)
    except:
        document = Document.objects.create(filename=file2, text=text)
    print("about to analyse")
    analyse_document(document)
    print("analysed")
    return HttpResponseRedirect(reverse(home))

def analyse_document(document):
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
            entity.save()
        else:
            entity = Entity.objects.get(entityID=URL)
        try:
            instance = Instance.objects.get(documentID=document, entityID=entity, start=start, stop=stop)
        except:
            instance = Instance.objects.create(documentID=document, entityID=entity, start=start, stop=stop)
    return 1


def split_entities(docid,doc):
    instances=Instance.objects.filter(documentID=docid).order_by('start')
    text=doc.text
    indexed=[]
    prev=0
    for instance in instances:
        indexed.append(text[prev:instance.start])
        indexed.append(text[instance.start:instance.stop])
        prev=instance.stop
    indexed.append(text[prev:])
    return indexed




