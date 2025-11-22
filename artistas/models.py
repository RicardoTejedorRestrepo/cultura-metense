from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=50, default='fas fa-star')
    
    def __str__(self):
        return self.nombre

class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"

class Artista(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_artistico = models.CharField(max_length=200, db_index=True)
    descripcion = models.TextField()
    precio_por_hora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    municipio = models.CharField(max_length=100, db_index=True)
    ubicacion = models.CharField(max_length=100, db_index=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    email_contacto = models.EmailField(db_index=True)
    telefono = models.CharField(max_length=20)
    pagina_web = models.URLField(blank=True, null=True)
    logotipo = models.ImageField(upload_to='logotipos/', null=True, blank=True)
    imagen_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)
    subcategorias = models.ManyToManyField(Subcategoria)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre_artistico
    
    class Meta:
        verbose_name = 'Artista'
        verbose_name_plural = 'Artistas'

class RedSocial(models.Model):
    REDES_SOCIALES_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='redes_sociales')
    nombre = models.CharField(max_length=20, choices=REDES_SOCIALES_CHOICES)
    url = models.URLField()
    
    def __str__(self):
        return f"{self.nombre} - {self.artista.nombre_artistico}"
    
    class Meta:
        verbose_name = 'Red Social'
        verbose_name_plural = 'Redes Sociales'

class ImagenPortafolio(models.Model):
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='imagenes_portafolio')
    imagen = models.ImageField(upload_to='portafolio/')
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Imagen de {self.artista.nombre_artistico}"
    
    class Meta:
        verbose_name = 'Imagen de Portafolio'
        verbose_name_plural = 'Imágenes de Portafolio'