from django.shortcuts import render

from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.http import JsonResponse
from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaFormSet
from productos.models import Producto, MovimientoStock
from clientes.models import Cliente
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML 
import tempfile
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin



def venta_pdf(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    items = venta.items.all() # type: ignore

    html_string = render_to_string('ventas/venta_pdf.html', {
        'venta': venta,
        'items': items,
        })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=venta_{venta.sku}.pdf'

    with tempfile.NamedTemporaryFile(delete=True) as output:
        HTML(string=html_string).write_pdf(output.name)
        output.seek(0)
        response.write(output.read())

    return response

def ventas_por_dia(request):
    data = (
        Venta.objects
        .values('fecha')
        .annotate(total=Sum('total'))
        .order_by('fecha')
        )

    return JsonResponse(list(data), safe=False)
    
    
class VentaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 10
    #Restriccion de permisos para grupo ventas
    permission_required = 'ventas.view_venta'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        cliente_id = self.request.GET.get('cliente')
        fecha = self.request.GET.get('fecha')
        
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        return queryset.select_related('cliente')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all()
        context['cliente_filtro'] = self.request.GET.get('cliente', '')
        context['fecha_filtro'] = self.request.GET.get('fecha', '')
        return context

class VentaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

    #Restriccion de permisos para grupo ventas
    permission_required = 'ventas.view_venta'

class VentaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')
    #Restriccion de permisos para grupo ventas
    permission_required = 'ventas.add_venta'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemVentaFormSet(self.request.POST)
        else:
            context['formset'] = ItemVentaFormSet()
        return context
    
    def form_valid (self, form):
        context = self.get_context_data()
        formset = context['formset']
         # Si el código está vacío, se generará automáticamente en el save() del modelo
        
        form.instance.sku = None  # Esto activará la generación automática
        with transaction.atomic():
        # NO guardar la venta todavía - usar commit=False
            self.object = form.save(commit=False)
        
            if formset.is_valid():
            # Procesar formset pero sin guardar aún
                items = formset.save(commit=False)
            
            # Validar stock antes de hacer cualquier guardado
                for item in items:
                    producto = item.producto
                    if item.cantidad <= producto.stock:
                        continue  # Stock suficiente
                    else:
                        messages.error(self.request, f'Stock insuficiente para {producto.nombre}')
                        return self.form_invalid(form)
            
            # **PRIMERO calcular el total**
                total_venta = 0
                for item in items:
                    item.subtotal = item.cantidad * item.precio_unitario
                    total_venta += item.subtotal

            # **ASIGNAR el total a la venta**
                self.object.total = total_venta
            
            # **AHORA SÍ guardar la venta con el total**
                self.object.save()
            
            # Establecer la instancia para el formset y guardar items
                formset.instance = self.object
                for item in items:
                    item.venta = self.object  # Asegurar la relación
                    item.save()
                
                # Descontar stock del producto
                    producto = item.producto
                    producto.stock -= item.cantidad
                    producto.save()
                
                # Registrar movimiento de stock
                    from productos.models import MovimientoStock
                    MovimientoStock.objects.create(
                        producto=producto,
                        tipo='salida',
                        cantidad=item.cantidad,
                        motivo=f'Venta {self.object.sku}',
                        usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
                   )
            
            # Eliminar items marcados para borrar
                for obj in formset.deleted_objects:
                    obj.delete()
            
            # **YA NO necesitas llamar a actualizar_total() aquí**
            # because ya calculaste el total arriba
            
                messages.success(self.request, f'Venta {self.object.sku} registrada exitosamente. Total: ${self.object.total}')
                return super().form_valid(form)
            else:
                return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class ProductoPrecioView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Vista para obtener el precio de un producto via AJAX"""
    #Restriccion de permisos para grupo ventas
    permission_required = 'productos.view_producto'
        
    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        return JsonResponse({
            'precio': float(producto.precio),
            'stock': producto.stock,
            'nombre': producto.nombre
            })
    

class VentaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    #Restriccion de permisos para grupo ventas
    permission_required = 'ventas.change_venta'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemVentaFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ItemVentaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            # Lógica similar a CreateView pero para actualizar
            self.object = form.save(commit=False)
            
            if formset.is_valid():
                # Calcular nuevo total
                total_venta = 0
                items = formset.save(commit=False)
                
                for item in items:
                    item.subtotal = item.cantidad * item.precio_unitario
                    total_venta += item.subtotal
                
                self.object.total = total_venta
                self.object.save()
                
                formset.instance = self.object
                for item in items:
                    item.venta = self.object
                    item.save()
                
                for obj in formset.deleted_objects:
                    obj.delete()
                
                messages.success(self.request, f'Venta {self.object.sku} actualizada exitosamente.')
                return super().form_valid(form)
            else:
                return self.form_invalid(form)

    
class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/venta_delete.html'
    success_url = reverse_lazy('ventas:venta_list')

    #Restriccion de permisos para grupo ventas
    permission_required = 'ventas.delete_venta'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        with transaction.atomic():
            # Restaurar stock de todos los productos antes de eliminar
            items = self.object.items.all() # type: ignore
            
            for item in items:
                producto = item.producto
                # Restaurar stock
                producto.stock += item.cantidad
                producto.save()
                
                # Registrar movimiento de stock (entrada por cancelación)
                MovimientoStock.objects.create(
                    producto=producto,
                    tipo='entrada',
                    cantidad=item.cantidad,
                    motivo=f'Cancelación de venta {self.object.sku}', # type: ignore
                    usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
                )
            
            # Guardar código para el mensaje antes de eliminar
            codigo_venta = self.object.sku # type: ignore
            
            # Eliminar la venta (esto eliminará también los items por CASCADE)
            self.object.delete()
            
            messages.success(request, f'Venta {codigo_venta} eliminada exitosamente. Stock restaurado.')
        
        return redirect(self.success_url)

