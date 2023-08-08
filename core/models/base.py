from django.db import models
from core.utils import get_time, random_str

def upload_file_src(instance,path):
    frmt = str(path).split('.')[::-1]
    return f'files/{get_time()}/{random_str()}.{frmt}'


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class File(BaseModel):
    file = models.FileField(upload_to=upload_file_src)

    class Meta:
        ordering = '-id',

    def __str__(self):
        return f'File {self.created_at}'
    
