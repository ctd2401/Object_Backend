from django.urls import path
from .views import *

app_name = "categories"

urlpatterns = [
    path("categories", CategoryView.as_view(), name="list category"),
    path("categories/<int:pk>", CategoryDetailView.as_view(), name="detail category"),
]
