from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from django import forms
from django.http import JsonResponse
from .models import Artista, Categoria, Subcategoria, RedSocial, ImagenPortafolio
from .forms import BusquedaForm, RedSocialForm, ImagenPortafolioForm
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory


def obtener_subcategorias(request, categoria_id):
    """Vista para obtener subcategorías de una categoría específica en formato JSON"""
    try:
        # Obtener la categoría
        categoria = get_object_or_404(Categoria, id=categoria_id)
        
        # Obtener todas las subcategorías de esta categoría
        subcategorias = Subcategoria.objects.filter(categoria=categoria).values('id', 'nombre')
        
        # Convertir a lista y devolver JSON
        data = list(subcategorias)
        return JsonResponse(data, safe=False)
        
    except Categoria.DoesNotExist:
        return JsonResponse({'error': 'Categoría no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def home(request):
    form = BusquedaForm(request.GET or None)
    artistas = Artista.objects.filter(activo=True).select_related('usuario').prefetch_related('subcategorias')
    
    # Si el formulario es válido, aplicar filtros
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
    
    # Obtener categoría y subcategoría seleccionadas para pre-seleccionar en el template
    categoria_seleccionada = request.GET.get('categoria')
    subcategoria_seleccionada = request.GET.get('subcategoria')
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'artistas': page_obj,
        'categoria_seleccionada': categoria_seleccionada,
        'subcategoria_seleccionada': subcategoria_seleccionada,
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Portafolio Cultural del Departamento del Meta')
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
    
    if request.user == artista.usuario:
        red_social_form = RedSocialForm()
        imagen_form = ImagenPortafolioForm()
        
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
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Portafolio Cultural del Departamento del Meta')
    }
    return render(request, 'artistas/detalle_artista.html', context)


@login_required
def editar_perfil(request, artista_id):
    artista = get_object_or_404(Artista, id=artista_id, usuario=request.user)
    
    # Obtener todas las categorías con sus subcategorías
    categorias = Categoria.objects.prefetch_related('subcategorias').all()
    subcategorias_seleccionadas = artista.subcategorias.values_list('id', flat=True)
    
    # Formulario dinámico para el modelo Artista
    ArtistaForm = modelform_factory(
        Artista, 
        fields=[
            'nombre_artistico', 'descripcion', 'precio_por_hora', 
            'municipio', 'ubicacion', 'email_contacto', 'telefono',
            'pagina_web', 'imagen_perfil', 'logotipo', 'pdf', 'subcategorias',
            'latitud', 'longitud'
        ],
        widgets={
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'subcategorias': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
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
    
    context = {
        'form': form,
        'artista': artista,
        'categorias': categorias,
        'subcategorias_seleccionadas': subcategorias_seleccionadas,
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Portafolio Cultural del Departamento del Meta')
    }
    return render(request, 'artistas/editar_perfil.html', context)