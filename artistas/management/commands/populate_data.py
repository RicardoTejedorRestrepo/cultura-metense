from django.core.management.base import BaseCommand
from artistas.models import Categoria, Subcategoria

class Command(BaseCommand):
    help = 'Pobla la base de datos con categorías y subcategorías iniciales para Cultura Metense'

    def handle(self, *args, **options):
        categorias_data = {
            'Circo': {
                'icono': 'fas fa-acorn',
                'subcategorias': ['Acrobacia aérea', 'Malabares', 'Trapecio']
            },
            'Danza': {
                'icono': 'fas fa-music',
                'subcategorias': ['Danza llanera', 'Danza folclórica nacional', 'Danza urbana']
            },
            'Artes plásticas': {
                'icono': 'fas fa-palette',
                'subcategorias': ['Pintura', 'Escultura', 'Dibujo']
            },
            'Cinematografía': {
                'icono': 'fas fa-film',
                'subcategorias': ['Productores', 'Exhibidores', 'Directores']
            },
            'Teatro': {
                'icono': 'fas fa-theater-masks',
                'subcategorias': ['Teatro musical', 'Improvisación', 'Sombras']
            },
            'Musical': {
                'icono': 'fas fa-guitar',
                'subcategorias': ['Instrumentista', 'Compositor', 'Arreglista']
            },
            'Literatura': {
                'icono': 'fas fa-book',
                'subcategorias': ['Escritura', 'Editor', 'Corrector']
            },
            'Patrimonio': {
                'icono': 'fas fa-landmark',
                'subcategorias': ['Portadores de saberes', 'Artesanos', 'Otros saberes']
            },
        }

        for categoria_nombre, data in categorias_data.items():
            categoria, created = Categoria.objects.get_or_create(
                nombre=categoria_nombre,
                defaults={'icono': data['icono']}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría creada: {categoria_nombre}')
                )
            
            for subcategoria_nombre in data['subcategorias']:
                subcategoria, created = Subcategoria.objects.get_or_create(
                    categoria=categoria,
                    nombre=subcategoria_nombre
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Subcategoría creada: {subcategoria_nombre}')
                    )

        self.stdout.write(
            self.style.SUCCESS('¡Datos poblados exitosamente para Cultura Metense!')
        )