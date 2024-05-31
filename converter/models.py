from django.db import models
from django.utils import timezone
import random


# Create your models here.

alphabet = "abcdefghjkmnpqrstuvwxzy"
alphabet += alphabet.upper()
alphabet += "23456789"


class Conversion(models.Model):
    project_name = models.TextField()
    sb3_file_name = models.TextField()
    project_link = models.CharField(max_length=100, unique=True)
    tmpdir = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    python_code = models.TextField()
    intermediate = models.TextField()
    sb3_json = models.TextField()
    language = models.CharField(max_length=20)


    class Meta:
       indexes = [
           models.Index(fields=['project_link',]),
]



def generate_unique_link():
    result = ''.join(random.choices(alphabet, k=5))
    result += '-'
    result += ''.join(random.choices(alphabet, k=5))
    return result
