from django.contrib import admin
from .models import *

class ProductVariantTabularInline(admin.TabularInline):
    model = ProductVariant
    extra = 1 # Số dòng trống để thêm variant mới
    fields = ['product','variant','image','price_diff','available']
    # ordering = ['variant__variant_type']

class ProductAdmin(admin.ModelAdmin):

    list_display = ('id','name','code','slug','description','origin_price','image','available')
    list_filter = ('available','category',)
    search_fields = ('name','code','slug',)
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 50
    inlines = [ProductVariantTabularInline]
    actions = ['set_default_description','set_active_status','set_inactive_status']

    def get_ordering(self,request):
        if request.user.is_superuser:
            return ('name','-created_at')
        return ('name',)

    def set_default_description(self,request,queryset):
        queryset.update(description="No description provided")
        self.message_user(request,f"{queryset.count()} products were updated with default description.")
    set_default_description.short_description = 'Set default description for selected products'

    def set_active_status(self,request,queryset):
        queryset.update(active=True)
        self.message_user(request,f"{queryset.count()} product were marked as active.")
    set_active_status.short_description = 'Set active status for selected products'

    def set_inactive_status(self,request,queryset):
        queryset.update(active=False)
        self.message_user(request,f"{queryset.count()} product were marked as inactive.")
    set_inactive_status.short_description = 'Set inactive status for selected products'


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product','variant','available',)
    list_filter = ('available','product',)
    search_fields = ('product__name',)
    list_per_page = 50
    actions = ['set_active_status','set_inactive_status']

    def set_active_status(self,request,queryset):
        queryset.update(active=True)
        self.message_user(request,f"{queryset.count()} product variant were marked as active.")
    set_active_status.short_description = 'Set active status for selected product variants'

    def set_inactive_status(self,request,queryset):
        queryset.update(active=False)
        self.message_user(request,f"{queryset.count()} product variant were marked as inactive.")
    set_inactive_status.short_description = 'Set inactive status for selected product variants'

admin.site.register(Product,ProductAdmin)
admin.site.register(VariantType)
admin.site.register(Variant)
admin.site.register(ProductVariant,ProductVariantAdmin)

