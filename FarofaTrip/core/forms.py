from django import forms
from .models import Perfil, Evento
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.ModelForm):
    """
    Formulário de login baseado no modelo User, usando e-mail e senha.

    A validação de credenciais é feita no método clean(),
    que autentica o usuário a partir do e-mail informado.
    """
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
        """
        Normaliza o e-mail (trim + lower) e garante que não esteja vazio.
        """
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise ValidationError('Informe o e-mail.')
        self.cleaned_data['email'] = email
        return email

    def clean(self):
        """
        Valida o par (email, password):
        - verifica se existe usuário com o e-mail informado
        - autentica a senha
        - salva o usuário autenticado em self.user
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                # Busca o usuário por e-mail, ignorando maiúsculas/minúsculas
                user_obj = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise ValidationError("Usuário com esse e-mail não encontrado.")
            except User.MultipleObjectsReturned:
                raise ValidationError("Há mais de um usuário com este e-mail. Contate o suporte.")

            # Autentica usando o username do usuário encontrado
            user = authenticate(username=user_obj.username, password=password)
            if user is None:
                raise ValidationError("Senha incorreta para o e-mail informado.")

            # Guarda o usuário autenticado para uso posterior na view
            self.user = user


class PerfilForm(forms.ModelForm):
    """
    Formulário para criação/edição de Perfil.
    Inclui validações de formato para CPF e telefone.
    """
    class Meta:
        model = Perfil
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
        """
        Valida se o CPF está no formato esperado (14 caracteres com pontos e traço).
        Obs.: aqui é validação de formato, não de CPF real.
        """
        cpf = self.cleaned_data.get('cpf')
        if len(cpf) != 14:
            raise forms.ValidationError("O CPF deve estar no formato 000.000.000-00.")
        return cpf

    def clean_telefone(self):
        """
        Valida se o telefone está no formato (00) 00000-0000 (15 caracteres).
        """
        telefone = self.cleaned_data.get('telefone')
        if len(telefone) != 15:
            raise forms.ValidationError("O telefone deve estar no formato (00) 00000-0000.")
        return telefone


class EventoForm(forms.ModelForm):
    """
    Formulário para criação/edição de Evento.
    Usa widgets de texto simples para facilitar o preenchimento.
    """
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
            'ingresso': 'Preço do ingress0',
            'excursao': 'Preço da excursão',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do evento'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local do evento'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade do evento'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Data do evento'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Decrição'}),
            'imagem': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Banner do evento'}),
            'ingresso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preço do ingresso'}),
            'excursao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preço da excursão'}),
        }
