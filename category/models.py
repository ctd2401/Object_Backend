from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
import logging
from django.db import transaction
logger = logging.getLogger("Category")
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
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        try:
            if self.id:  # Check if the instance already exists (i.e., not a new object)
                original_instance = Category.objects.get(id=self.id)
                if original_instance.image != self.image:
                    logger.info(f"prepare to update image for Category {original_instance.id} : {original_instance.image.url}")
                    if original_instance.image:
                        destroy(parse_path(original_instance.image.url), invalidate=True)
                    else:
                        pass
            
            super().save(*args, **kwargs)
            if self.image:
                logger.info(f"current image for Category {self.id} : {self.image.url}")


        except Exception as e:
            logger.warning(f"error : {e}")
            transaction.set_rollback(True)
    
    def delete(self):
        destroy(parse_path(self.image.url), invalidate=True)
        return super().delete()