from django.urls import path
from . import views

app_name = 'artistas'

urlpatterns = [
    path('', views.home, name='home'),
    path('artista/<int:artista_id>/', views.detalle_artista, name='detalle_artista'),
    path('artista/<int:artista_id>/editar/', views.editar_perfil, name='editar_perfil'),
]