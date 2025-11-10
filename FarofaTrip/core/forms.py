from django import forms
from .models import Usuario, Evento
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password')
        labels = {
            'email': 'E-Mail:',
            'password': 'Senha:',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu e-mail'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite sua senha'
            }),
        }
        error_messages = {
            'email': {
                'required': ("Informe o e-mail."),
            },
        }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise ValidationError('Informe o e-mail.')
        self.cleaned_data['email'] = email
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user_obj = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise ValidationError("Usuário com esse e-mail não encontrado.")
            except User.MultipleObjectsReturned:
                raise ValidationError("Há mais de um usuário com este e-mail. Contate o suporte.")

            user = authenticate(username=user_obj.username, password=password)
            if user is None:
                raise ValidationError("Senha incorreta para o e-mail informado.")

            self.user = user

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
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if len(telefone) != 15:
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