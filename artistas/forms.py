from django import forms
from .models import RedSocial, ImagenPortafolio

class RedSocialForm(forms.ModelForm):
    class Meta:
        model = RedSocial
        fields = ['nombre', 'url']
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

class ImagenPortafolioForm(forms.ModelForm):
    class Meta:
        model = ImagenPortafolio
        fields = ['imagen', 'descripcion']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción de la imagen'}),
        }

class BusquedaForm(forms.Form):
    ubicacion = forms.CharField(
        max_length=100, 
        required=False, 
        label='¿Dónde lo buscas?',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipio o ciudad'})
    )
    categoria = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subcategoria = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todas las subcategorías",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nombre = forms.CharField(
        max_length=100, 
        required=False, 
        label='Nombre del artista',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre artístico'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Categoria, Subcategoria
        self.fields['categoria'].queryset = Categoria.objects.all()
        self.fields['subcategoria'].queryset = Subcategoria.objects.all()