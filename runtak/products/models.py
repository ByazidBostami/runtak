from django.db import models

class Category(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    price = models.FloatField()
    sale_price = models.FloatField(default=0)
    stock = models.IntegerField(default=100)
    image = models.URLField(blank=True)

    category_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name
