from django import forms
from django.forms import inlineformset_factory
from .models import Venta, ItemVenta
from productos.models import Producto

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control select2'}),
        }
        help_texts = {
            'cliente': 'Seleccione el cliente que realiza la compra',
            "sku": "Dejar vacío para generar automáticamente un SKU único",
        }

class ItemVentaForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        widget=forms.Select(attrs={'class': 'form-control producto-select'}),
        help_text='Solo se muestran productos con stock disponible'
    )
    
    class Meta:
        model = ItemVenta
        fields = [ 'producto', 'cantidad', 'precio_unitario']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'min': '1',
                'step': '1'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-input',
                'min': '0',
                'step': '0.01'
            }),
        }
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')
        
        if producto and cantidad:
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f'Stock insuficiente. Stock disponible: {producto.stock}'
                )
        return cantidad
    
    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return precio

# Formset para los items de venta
ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)