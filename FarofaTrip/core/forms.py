from django import forms
from .models import Usuario
from .models import Evento


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        labels = {
            'nome': 'Nome Completo:',
            'cpf': 'CPF:',
            'telefone': 'Telefone:',
            'endereco': 'Endereço:',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, número, bairro'})
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if len(cpf) != 14:
            raise forms.ValidationError("O CPF deve estar no formato 000.000.000-00.")
        return cpf
    
    def clean_fone(self):
        telefone = self.cleaned_data.get('telefone')
        if len(telefone) != 11:
            raise forms.ValidationError("O telefone deve estar no formato (00) 00000-0000.")
        return telefone
    

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = '__all__'
        labels = {
            'nome': 'Nome do envento:',
            'local': 'Local do envento:',
            'cidade': 'Cidade do eneveto:',
            'data': 'Data do evento:',
            'descricao': 'Descrição',
            'imagem': 'Imgagem',
            'preco': 'Preço',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do evento'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local do evento'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade do evento'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Data do evento'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Decrição'}),
            'imagem': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Banner do evento'}),
            'preco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preço do ingresso'}),
        }