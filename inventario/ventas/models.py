
from django.db import models
from clientes.models import Cliente
from productos.models import Producto
import random
import string

class Venta(models.Model):
    sku = models.CharField('sku', max_length=20, unique=True, editable=True,  help_text="Código único de identificación del producto", blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2,)

    def save(self, *args, **kwargs):
        # Asegúrate de calcular el total antes de guardar
        if not self.total:
            self.calcular_total()
        if not self.sku:
            self.sku = self.generar_sku_unico()
        super().save(*args, **kwargs)
    def generar_sku_unico(self):
       """Genera un SKU único automáticamente"""
       while True:
           sku = f"VENT-{random.randint(10000, 99999)}"
           if not Venta.objects.filter(sku=sku).exists():
                return sku


    def calcular_total(self):
        # Lógica para calcular el total
        self.total = 0
        # Ejemplo: sumar los totales de los items relacionados
        for item in self.items.all(): # type: ignore
            self.total += item.subtotal

class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    related_name="items" 

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
   
# Create your models here.
