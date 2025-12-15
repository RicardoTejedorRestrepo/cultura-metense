from django import forms
from .models import RedSocial, ImagenPortafolio, Categoria, Subcategoria


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
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Municipio o ciudad'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-control', 
            'id': 'id_categoria',
            'onchange': 'cargarSubcategorias(this.value);'
        })
    )
    subcategoria = forms.ModelChoiceField(
        queryset=Subcategoria.objects.none(),  # Inicialmente vacío
        required=False,
        empty_label="Selecciona una categoría primero",
        widget=forms.Select(attrs={
            'class': 'form-control', 
            'id': 'id_subcategoria',
            'disabled': True
        })
    )
    nombre = forms.CharField(
        max_length=100, 
        required=False, 
        label='Nombre del artista',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nombre artístico'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si ya hay datos en el formulario (GET), cargar las subcategorías correspondientes
        if 'categoria' in self.data and self.data['categoria']:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                    categoria_id=categoria_id
                ).order_by('nombre')
                self.fields['subcategoria'].widget.attrs['disabled'] = False
            except (ValueError, TypeError):
                pass