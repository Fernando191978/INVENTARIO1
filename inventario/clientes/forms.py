from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'numero_documento', 'email', 'telefono', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Juan'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Ej: Pérez'}),
            'numero_documento': forms.TextInput(attrs={'placeholder': 'Ej: 12345678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ej: juan@email.com'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: +54 11 1234-5678'}),
        }
        help_texts = {
            'numero_documento': 'Este número debe ser único para cada cliente.',
        }
    
    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if Cliente.objects.filter(numero_documento=numero_documento).exists():
            if self.instance and self.instance.pk:
                # Permitir actualización del mismo cliente
                if Cliente.objects.filter(numero_documento=numero_documento).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Este número de documento ya está registrado.')
            else:
                # Nuevo cliente - no permitir duplicados
                raise forms.ValidationError('Este número de documento ya está registrado.')
        return numero_documento