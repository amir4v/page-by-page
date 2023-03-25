from django.db import models
from django.contrib.auth.models import User


class PDF(models.Model):
    name = models.CharField(max_length=2048)
    current_page = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Page(models.Model):
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    path = models.CharField(max_length=2048)
