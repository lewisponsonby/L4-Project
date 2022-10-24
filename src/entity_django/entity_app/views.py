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
        print(file2)
        document = Document.objects.create(text=file2)
        document.save()
        return HttpResponse("File Uploaded")
    return HttpResponseRedirect(reverse(home))
