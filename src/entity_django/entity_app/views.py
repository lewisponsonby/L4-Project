from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
# Create your views here.


def home(request):
    template = loader.get_template('home.html')
    documents = Document.objects.all().values()
    context = {
        'documents': documents,
    }
    return HttpResponse(template.render(context, request))

def upload(request):
    template = loader.get_template('upload.html')
    context = {}
    return HttpResponse(template.render(context, request))

def add_document(request):
    if request.method == 'POST':
        file2=request.FILES['file']
        file = File.objects.create(txtfile=file2)
        file.save()
    with file.txtfile.open('r') as f:
        lines = f.readlines()
    text=""
    for line in lines:
        text+=line.replace("\n"," ")
    document = Document.objects.create(filename=file2, text=text)
    document.save()


    return HttpResponseRedirect(reverse(home))
