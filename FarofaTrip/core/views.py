from django.shortcuts import render

def aplication(request):
    return render(request, 'login.html')

def cadastro(request):
    return render(request, 'cadastro.html')
