from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
def parse_path(url):
    public_id = url.split('/')[-1].rsplit('.', 1)[0]
    return public_id

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=255, unique=True,verbose_name="Đường dẫn")
    description = models.TextField(blank=True, null=True,verbose_name="Mô tả")
    code = models.CharField(max_length=100, unique=True,verbose_name="Mã danh mục")
    image = CloudinaryField(blank=True, null=True,verbose_name="Hình ảnh")
    active = models.BooleanField(default=True,verbose_name='Trạng thái')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:  # Check if the instance already exists (i.e., not a new object)
            original_instance = Category.objects.get(pk=self.pk)
            if original_instance.image != self.image:
                print("Cloudinary image field has changed!")
                if original_instance.image:
                    destroy(parse_path(original_instance.image.url), invalidate=True)
                else:
                    pass
        
        super().save(*args, **kwargs)
        
    
    def delete(self):
        destroy(parse_path(self.image.url), invalidate=True)
        return super().delete()