from django.db import models
from core.utils import get_time, get_timesince_persian, random_str

def upload_file_src(instance,path):
    frmt = str(path).split('.')[-1]
    tm = get_time('%Y-%m-%d')
    return f'files/{tm}/{random_str()}.{frmt}'


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_created_at_timepast(self):
        return get_timesince_persian(self.created_at)


class File(models.Model):
    file = models.FileField(upload_to=upload_file_src)

    class Meta:
        ordering = '-id',

    def __str__(self):
        return f'File {self.created_at}'
    
    
