from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from artistas.models import Artista, Subcategoria

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Nombres',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus nombres'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Apellidos',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña segura'}),
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='La contraseña debe contener al menos una letra mayúscula, una minúscula y un número'
            )
        ]
    )
    
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite tu contraseña'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Estilos específicos para campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control password-input',
            'data-toggle': 'password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control password-input'
        })

class CompletarPerfilForm(forms.ModelForm):
    class Meta:
        model = Artista
        fields = [
            'nombre_artistico', 'descripcion', 'precio_por_hora', 
            'municipio', 'ubicacion', 'email_contacto', 'telefono',
            'pagina_web', 'logotipo', 'imagen_perfil', 'pdf', 'subcategorias'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe tu trayectoria...'
            }),
            'subcategorias': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+57 300 000 0000'
            }),
        }
    
    latitud = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitud = forms.FloatField(required=False, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar etiquetas y ayuda
        self.fields['precio_por_hora'].help_text = 'Precio aproximado por hora de servicio (opcional)'
        self.fields['email_contacto'].help_text = 'Este email será visible para posibles clientes'
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Validación básica de teléfono
        if telefono and not any(c.isdigit() for c in telefono):
            raise forms.ValidationError('Ingrese un número de teléfono válido.')
        return telefono
    
    def clean_email_contacto(self):
        email = self.cleaned_data.get('email_contacto')
        if Artista.objects.filter(email_contacto=email).exists():
            raise forms.ValidationError('Este email de contacto ya está registrado.')
        return email