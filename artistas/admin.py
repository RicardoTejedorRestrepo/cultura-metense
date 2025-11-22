from django.contrib import admin
from .models import Categoria, Subcategoria, Artista, RedSocial, ImagenPortafolio

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono']
    search_fields = ['nombre']

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria']
    list_filter = ['categoria']
    search_fields = ['nombre']

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ['nombre_artistico', 'usuario', 'municipio', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'municipio', 'subcategorias']
    search_fields = ['nombre_artistico', 'usuario__first_name', 'usuario__last_name']
    filter_horizontal = ['subcategorias']

@admin.register(RedSocial)
class RedSocialAdmin(admin.ModelAdmin):
    list_display = ['artista', 'nombre', 'url']
    search_fields = ['artista__nombre_artistico']

@admin.register(ImagenPortafolio)
class ImagenPortafolioAdmin(admin.ModelAdmin):
    list_display = ['artista', 'descripcion', 'fecha_subida']
    search_fields = ['artista__nombre_artistico']