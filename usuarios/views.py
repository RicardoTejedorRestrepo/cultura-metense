from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import RegistroForm, CompletarPerfilForm
from artistas.models import Artista
from django.db import transaction

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Ahora completa tu perfil de artista.')
            return redirect('usuarios:completar_perfil')
    else:
        form = RegistroForm()
    
    context = {
        'form': form,
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Cultura Metense')
    }
    return render(request, 'usuarios/registro.html', context)

@login_required
def completar_perfil(request):
    # Verificar si ya tiene perfil de artista
    if hasattr(request.user, 'artista'):
        messages.info(request, 'Ya tienes un perfil de artista completado.')
        return redirect('artistas:detalle_artista', artista_id=request.user.artista.id)
    
    if request.method == 'POST':
        form = CompletarPerfilForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    artista = form.save(commit=False)
                    artista.usuario = request.user
                    artista.save()
                    form.save_m2m()  # Para ManyToMany fields
                    
                    messages.success(request, '¡Perfil completado exitosamente! Ahora puedes ser encontrado en la plataforma.')
                    return redirect('artistas:detalle_artista', artista_id=artista.id)
                    
            except Exception as e:
                messages.error(request, f'Error al guardar el perfil: {str(e)}')
    else:
        # Pre-llenar email_contacto con el email del usuario
        initial_data = {'email_contacto': request.user.email}
        form = CompletarPerfilForm(initial=initial_data)
    
    context = {
        'form': form,
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'Cultura Metense')
    }
    return render(request, 'usuarios/completar_perfil.html', context)