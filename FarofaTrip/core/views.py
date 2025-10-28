from django.shortcuts import render

def aplication(request):
    return render(request, 'login.html')

def cadastro(request):
    return render(request, 'cadastro.html')

def index(request):
    return render(request, 'index.html')

def acesso(request):
    return render(request, 'embarque.html')

def sobre(request):
    return render(request, 'sobre.html')