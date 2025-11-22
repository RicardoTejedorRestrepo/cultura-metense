from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from .models import Artista, Categoria, Subcategoria, RedSocial, ImagenPortafolio
from .forms import BusquedaForm, RedSocialForm, ImagenPortafolioForm
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory

def home(request):
    form = BusquedaForm(request.GET or None)
    artistas = Artista.objects.filter(activo=True).select_related('usuario').prefetch_related('subcategorias')
    
    if form.is_valid():
        ubicacion = form.cleaned_data.get('ubicacion')
        categoria = form.cleaned_data.get('categoria')
        subcategoria = form.cleaned_data.get('subcategoria')
        nombre = form.cleaned_data.get('nombre')
        
        if ubicacion:
            artistas = artistas.filter(
                Q(municipio__icontains=ubicacion) | 
                Q(ubicacion__icontains=ubicacion)
            )
        
        if categoria:
            artistas = artistas.filter(subcategorias__categoria=categoria)
        
        if subcategoria:
            artistas = artistas.filter(subcategorias=subcategoria)
        
        if nombre:
            artistas = artistas.filter(
                Q(nombre_artistico__icontains=nombre) |
                Q(usuario__first_name__icontains=nombre) |
                Q(usuario__last_name__icontains=nombre)
            )
    
    # Paginación
    paginator = Paginator(artistas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'artistas': page_obj,
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Cultura Metense')
    }
    return render(request, 'artistas/home.html', context)

def detalle_artista(request, artista_id):
    artista = get_object_or_404(
        Artista.objects.select_related('usuario')
                      .prefetch_related('subcategorias', 'redes_sociales', 'imagenes_portafolio'),
        id=artista_id, 
        activo=True
    )
    
    # Artistas similares (misma categoría)
    subcategoria_ids = artista.subcategorias.values_list('id', flat=True)
    similares = Artista.objects.filter(
        subcategorias__id__in=subcategoria_ids,
        activo=True
    ).exclude(id=artista.id).select_related('usuario').prefetch_related('subcategorias').distinct()[:6]
    
    # Forms para redes sociales e imágenes (si es el dueño del perfil)
    red_social_form = None
    imagen_form = None
    subcategorias = None  # AGREGAR ESTO
    
    if request.user == artista.usuario:
        red_social_form = RedSocialForm()
        imagen_form = ImagenPortafolioForm()
        subcategorias = Subcategoria.objects.all()  # AGREGAR ESTO
        
        if request.method == 'POST':
            if 'agregar_red_social' in request.POST:
                red_social_form = RedSocialForm(request.POST)
                if red_social_form.is_valid():
                    red_social = red_social_form.save(commit=False)
                    red_social.artista = artista
                    red_social.save()
                    messages.success(request, 'Red social agregada exitosamente.')
                    return redirect('artistas:detalle_artista', artista_id=artista.id)
            
            elif 'agregar_imagen' in request.POST:
                imagen_form = ImagenPortafolioForm(request.POST, request.FILES)
                if imagen_form.is_valid():
                    imagen = imagen_form.save(commit=False)
                    imagen.artista = artista
                    imagen.save()
                    messages.success(request, 'Imagen agregada al portafolio exitosamente.')
                    return redirect('artistas:detalle_artista', artista_id=artista.id)
    
    context = {
        'artista': artista,
        'similares': similares,
        'red_social_form': red_social_form,
        'imagen_form': imagen_form,
        'subcategorias': Subcategoria.objects.all(),
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Cultura Metense')
    }
    return render(request, 'artistas/detalle_artista.html', context)

# Líneas finales del archivo (agrega esta función completa)
@login_required
def editar_perfil(request, artista_id):
    artista = get_object_or_404(Artista, id=artista_id, usuario=request.user)
    
    # Formulario dinámico para el modelo Artista
    ArtistaForm = modelform_factory(
        Artista, 
        fields=[
            'nombre_artistico', 'descripcion', 'precio_por_hora', 
            'municipio', 'ubicacion', 'email_contacto', 'telefono',
            'pagina_web', 'imagen_perfil', 'logotipo', 'pdf', 'subcategorias'
        ],
        widgets={
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'subcategorias': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
    )
    
    if request.method == 'POST':
        form = ArtistaForm(request.POST, request.FILES, instance=artista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('artistas:detalle_artista', artista_id=artista.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ArtistaForm(instance=artista)
    
    return render(request, 'artistas/editar_perfil.html', {
        'form': form,
        'artista': artista
    })