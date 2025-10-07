from django.contrib import admin
from .models import Category
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):

    list_display = ('id','name','code','slug','image','active')
    list_filter = ('active',)
    search_fields = ('name','code','slug',)
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 50
    actions = ['set_default_description','set_active_status','set_inactive_status']

    def get_ordering(self,request):
        if request.user.is_superuser:
            return ('name','-created_at')
        return ('name',)

    def set_default_description(self,request,queryset):
        queryset.update(description="No description provided")
        self.message_user(request,f"{queryset.count()} categories were updated with default description.")
    set_default_description.short_description = 'Set default description for selected categories'

    def set_active_status(self,request,queryset):
        queryset.update(active=True)
        self.message_user(request,f"{queryset.count()} category were marked as active.")
    set_default_description.short_description = 'Set active status for selected categories'

    def set_inactive_status(self,request,queryset):
        queryset.update(active=False)
        self.message_user(request,f"{queryset.count()} category were marked as inactive.")
    set_default_description.short_description = 'Set inactive status for selected categories'



admin.site.register(Category,CategoryAdmin)
