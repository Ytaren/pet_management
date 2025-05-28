from django.contrib import admin
from .models import Breed, Pet, VaccinationRecord

# Register your models here.

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'pet_type', 'average_lifespan', 'average_weight_min', 'average_weight_max', 'created_at']
    list_filter = ['pet_type', 'created_at']
    search_fields = ['name', 'name_en']
    ordering = ['pet_type', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'name_en', 'pet_type', 'description')
        }),
        ('品种特征', {
            'fields': ('average_lifespan', 'average_weight_min', 'average_weight_max')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class VaccinationRecordInline(admin.TabularInline):
    model = VaccinationRecord
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'pet_type', 'display_breed', 'age_display', 'weight', 'gender', 'is_active', 'created_at']
    list_filter = ['pet_type', 'gender', 'is_neutered', 'is_active', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__first_name', 'owner__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'age_display']
    inlines = [VaccinationRecordInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('owner', 'name', 'pet_type', 'breed', 'custom_breed')
        }),        ('详细信息', {
            'fields': ('birth_date', 'age_display', 'gender', 'is_neutered', 'weight')
        }),
        ('照片和备注', {
            'fields': ('photo', 'medical_notes', 'personality_notes')
        }),
        ('状态管理', {
            'fields': ('is_active',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'breed')


@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ['pet', 'vaccine_name', 'vaccination_date', 'next_due_date', 'veterinarian', 'is_overdue']
    list_filter = ['vaccination_date', 'next_due_date', 'vaccine_name']
    search_fields = ['pet__name', 'pet__owner__username', 'vaccine_name', 'veterinarian']
    ordering = ['-vaccination_date']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    
    fieldsets = (
        ('疫苗信息', {
            'fields': ('pet', 'vaccine_name', 'vaccination_date', 'next_due_date')
        }),
        ('医疗信息', {
            'fields': ('veterinarian', 'clinic_name', 'batch_number')
        }),
        ('备注', {
            'fields': ('notes',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pet', 'pet__owner')
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = '是否过期'
