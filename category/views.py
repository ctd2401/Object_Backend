from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from math import ceil
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404


from category.models import *
from django.db.models import Q
from .serializers import *


class CategoryView(APIView):
    """
    API để xử lý danh sách danh mục (GET) và tạo danh mục (POST).
    """


    def get(self, request):
        try:
            page = request.query_params.get("page", 1)
            limit = request.query_params.get("limit", 10)
            keyword = request.query_params.get("keyword", None)
            try:
                page = int(page)
                limit = int(limit)
            except ValueError:
                return Response(
                    {"error": "Page and limit must be integers."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            categories = Category.objects.all().order_by('name')
            # Lọc theo keyword nếu có
            print(categories)
            if keyword:
                categories = categories.filter(Q(name__icontains=keyword) |Q(code__icontains=keyword))

            # Tính toán phân trang
            total_items = categories.count()
            total_pages = ceil(total_items / limit)
            start = (page - 1) * limit
            end = start + limit
            paginated_category = categories[start:end]

            serializer = CategoryMenuSerializer(paginated_category,many=True)   
            return Response(
                {
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": limit,
                    "results": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        cat_name = request.data.get("name")

        try:
            if Category.objects.filter(name=cat_name).exists():
                return Response(
                    {"error": "Category with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CategoryDetailView(APIView):
    """
    API để xử lý chi tiết, cập nhật và xóa danh mục.
    """


    parser_classes = [MultiPartParser, FormParser]


    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.active == False:
            return Response(
                {"error": "Category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CategorySerializer(
            category
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk)
            serializer = UpdateCategorySerializer(
                category, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            return Response(
                {"error": "Category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def delete(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk)
            category.delete()
            return Response(
                {"message": "Category deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


