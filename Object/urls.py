"""
URL configuration for Object project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
admin.site.site_header = "OBJECT ADMIN"

from django.urls import path,include
urlpatterns = [
    ### admin site
    path('admin/', admin.site.urls),
    ### api product
    path('product/', include('product.urls')),
    ### api category
    path('category/', include('category.urls')),
]
