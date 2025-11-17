from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.urls import reverse

class Cliente(models.Model):
    nombre = models.CharField(
        'Nombre', 
        max_length=100,
        help_text='Ingrese el nombre del cliente'
    )
    apellido = models.CharField(
        'Apellido', 
        max_length=100,
        help_text='Ingrese el apellido del cliente'
    )
    numero_documento = models.CharField(
        'Número de Documento',
        max_length=20,
        unique=True,
        help_text='DNI, CUIT, o número de identificación único'
    )
    email = models.EmailField(
        'E-mail',
        max_length=100,
        validators=[EmailValidator()],
        blank=True,
        null=True,
        help_text='Correo electrónico del cliente'
    )
    telefono = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True,
        null=True,
        help_text='Número de teléfono del cliente'
    )
    direccion = models.TextField(
        'Dirección',
        max_length=200,
        blank=True,
        null=True,
        help_text='Dirección completa del cliente'
    )
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['apellido', 'nombre']),
            models.Index(fields=['numero_documento']),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} - {self.numero_documento}"
    
    def get_absolute_url(self):
        return reverse('clientes:cliente_detail', kwargs={'pk': self.pk})
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
# Create your models here.

