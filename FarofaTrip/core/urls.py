from django.urls import path

from . import views

urlpatterns = [
    path('', views.aplication),
    path('cadastro', views.cadastro),
    path('index', views.index),
    path('acesso', views.acesso),
    path('sobre',views.sobre )
 ]