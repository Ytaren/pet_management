from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from .models import Pet, Breed
from .forms import PetForm, PetFilterForm


class PetListView(LoginRequiredMixin, ListView):
    """宠物列表视图"""
    model = Pet
    template_name = 'pets/pet_list.html'
    context_object_name = 'pets'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Pet.objects.filter(owner=self.request.user, is_deleted=False)
        
        # 应用筛选
        form = PetFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('pet_type'):
                queryset = queryset.filter(pet_type=form.cleaned_data['pet_type'])
            if form.cleaned_data.get('gender'):
                queryset = queryset.filter(gender=form.cleaned_data['gender'])
            if form.cleaned_data.get('is_neutered'):
                queryset = queryset.filter(is_neutered=form.cleaned_data['is_neutered'])
            if form.cleaned_data.get('search'):
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(breed__name__icontains=search_term) |
                    Q(custom_breed__icontains=search_term)
                )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = PetFilterForm(self.request.GET)
        context['total_pets'] = Pet.objects.filter(
            owner=self.request.user, is_deleted=False
        ).count()
        return context


class PetDetailView(LoginRequiredMixin, DetailView):
    """宠物详情视图"""
    model = Pet
    template_name = 'pets/pet_detail.html'
    context_object_name = 'pet'
    
    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user, is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = self.get_object()
        
        # 获取相关日志统计
        logs = pet.logs.filter(is_deleted=False)
        context['total_logs'] = logs.count()
        context['recent_logs'] = logs.order_by('-date')[:5]
        
        return context


class PetCreateView(LoginRequiredMixin, CreateView):
    """添加宠物视图"""
    model = Pet
    form_class = PetForm
    template_name = 'pets/pet_form.html'
    success_url = reverse_lazy('pets:pet_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f'成功添加宠物 {form.cleaned_data["name"]}！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '请检查表单信息并重新提交。')
        return super().form_invalid(form)


class PetUpdateView(LoginRequiredMixin, UpdateView):
    """编辑宠物视图"""
    model = Pet
    form_class = PetForm
    template_name = 'pets/pet_form.html'
    
    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user, is_deleted=False)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('pets:pet_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'成功更新宠物 {form.cleaned_data["name"]} 的信息！')
        return super().form_valid(form)


class PetDeleteView(LoginRequiredMixin, DeleteView):
    """删除宠物视图"""
    model = Pet
    template_name = 'pets/pet_confirm_delete.html'
    success_url = reverse_lazy('pets:pet_list')
    
    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user, is_deleted=False)
    
    def post(self, request, *args, **kwargs):
        pet = self.get_object()
        pet.soft_delete()
        messages.success(request, f'成功删除宠物 {pet.name}！')
        return redirect(self.success_url)


@login_required
def get_breeds_by_type(request):
    """根据宠物类型获取品种列表 - AJAX接口"""
    pet_type = request.GET.get('pet_type')
    breeds = Breed.objects.filter(pet_type=pet_type).order_by('name')
    
    breed_list = [{'id': '', 'name': '请选择品种'}]
    for breed in breeds:
        breed_list.append({
            'id': breed.id,
            'name': breed.name
        })
    
    return JsonResponse({'breeds': breed_list})
