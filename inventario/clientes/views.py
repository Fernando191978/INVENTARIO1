# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin



class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10
    permission_required = 'clientes.view_cliente'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(apellido__icontains=busqueda) |
                Q(numero_documento__icontains=busqueda) |
                Q(email__icontains=busqueda)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        return context

class ClienteDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'
    #Restriccion de permisos para grupo ventas
    permission_required = 'clientes.view_cliente'
    

class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')
    #Restriccion de permisos para grupo ventas
    permission_required = 'clientes.add_cliente'
    
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cliente "{self.object.nombre_completo}" creado exitosamente.') # type: ignore
        return response

class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'

    #Restriccion de permisos para grupo ventas
    permission_required = 'clientes.change_cliente'
    
    

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cliente "{self.object.nombre_completo}" actualizado exitosamente.') # type: ignore
        return response
    
    def get_success_url(self):
        return reverse_lazy('clientes:cliente_detail', kwargs={'pk': self.object.pk}) # type: ignore

class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente_list')

    #Restriccion de permisos para grupo ventas
    permission_required = 'clientes.delete_cliente'
    
   
    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()
        messages.success(self.request, f'Cliente "{cliente.nombre_completo}" eliminado exitosamente.') # type: ignore
        return super().delete(request, *args, **kwargs)