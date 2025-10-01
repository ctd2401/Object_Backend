from django.urls import path
from .views import *
from .log import *

app_name = "categories"

urlpatterns = [
    path("categories", CategoryView.as_view(), name="list category"),
    path("categories/<int:pk>", CategoryDetailView.as_view(), name="detail category"),

    ###log
    path("log/image_category",view_logs_category,name='view log category'),
    path("log/image_category/del",clear_logs,name='delete log category')
]
