from django.db import models

# Create your models here.
from django.db import models
import os
import uuid
from django.core.exceptions import ValidationError
from PIL import Image
from django.utils import timezone
import random
import string

def validate_image_size(image):
   filesize = image.file.size
   megabyte_limit = 5.0
   if filesize > megabyte_limit * 1024 * 1024:
       raise ValidationError(f"El tamaño maximo permitido es {megabyte_limit} MB.")

def get_image_path(instance, filename):
   ext = filename.split('.')[-1]
   filename = f"{uuid.uuid4()}.{ext}"
   return os.path.join('productos', filename)

class Producto(models.Model):
    sku = models.CharField('sku', max_length=20, unique=True, editable=True,  help_text="Código único de identificación del producto", blank=True, null=True)
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = models.TextField('Descripción', max_length=200)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    stock = models.IntegerField('Stock', default=0)
    stock_minimo = models.IntegerField(verbose_name='Stock Mínimo', default=5)
    imagen = models.ImageField(
       'Imagen', 
       upload_to=get_image_path, 
       validators=[validate_image_size], 
       blank=True, 
       null=True,
       help_text='Formatos permitidos: JPG, PNG, GIF, WEBP, AVIF. Tamaño máximo: 5 MB.')
    fecha_creacion = models.DateTimeField('Fecha de creación',
       auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', 
       auto_now=True)
    
    class Meta:
       verbose_name = 'Producto'
       verbose_name_plural = 'Productos'
       ordering = ['nombre']
       
    def save(self, *args, **kwargs):
       if not self.sku:
            self.sku = self.generar_sku_unico()
       super().save(*args, **kwargs)
       if self.imagen:
           try:
               img = Image.open(self.imagen.path)
               if img.height > 300 or img.width > 300:
                   output_size = (300, 300)
                   img.thumbnail(output_size)
                   img.save(self.imagen.path)
           except Exception as e:
               print(f"Error al procesar la imagen: {e}")
    
    def generar_sku_unico(self):
       """Genera un SKU único automáticamente"""
       while True:
           sku = f"PROD-{random.randint(10000, 99999)}"
           if not Producto.objects.filter(sku=sku).exists():
                return sku
    
    def __str__(self):
       return f"{self.sku} - {self.nombre}"
    
    @property
    def necesita_reposicion(self):
       return self.stock < self.stock_minimo
    
class MovimientoStock(models.Model):
    TIPO_CHOICES = [
       ('entrada', 'Entrada'),
       ('salida', 'Salida'),
       ('ajuste', 'Ajuste'),
    ]
    producto = models.ForeignKey(Producto,
    on_delete=models.CASCADE, 
    related_name='movimientos')

    tipo = models.CharField('Tipo', max_length=50, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField('Fecha', default=timezone.now)
    motivo = models.TextField('Motivo', max_length=200, blank=True, null=True)
    usuario = models.CharField('Usuario', max_length=50)
    class Meta:
       verbose_name = 'Movimiento de Stock'
       verbose_name_plural = 'Movimientos de Stock'
       ordering = ['-fecha']
       
    def __str__(self):
       return f" {self.producto.nombre} - {self.tipo} - {self.cantidad}"