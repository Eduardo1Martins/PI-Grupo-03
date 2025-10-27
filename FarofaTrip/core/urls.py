from django.urls import path

from . import views

urlpatterns = [
    path('', views.aplication),
    path('cadastro', views.cadastro),
 ]