"""entity_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from entity_app import views

urlpatterns = [
    path('home/', views.home, name='home.html'),
    path('user_study/', views.user_study, name='user_study.html'),
    path('upload_document/', views.upload_document, name='upload.html'),
    path('upload_document/add_document/', views.add_document, name='add_document'),
    path('delete_document/<str:docid>/', views.delete_document, name='docid'),
    path('delete_entity/<str:entid>/', views.delete_entity, name='entid'),
    path('regenerate_lda/', views.regenerate_lda, name='regenerate_lda'),
    path('admin/', admin.site.urls),
    path('view_document/', views.list_documents, name='list_documents.html'),
    path('view_document/<str:docid>/', views.view_document, name='docid'),
    path('upload_answers/<str:qid>/', views.add_qanswer, name='qid'),
    path('view_entity/', views.list_entities, name='list_entities.html'),
    path('view_entity/<str:entid>/', views.view_entity, name='entid'),
    path('corpus_analytics/', views.corpus_analytics, name='corpus_analytics.html')
]
