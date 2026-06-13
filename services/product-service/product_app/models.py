from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name

# 10 specific product domains using multi-table inheritance

class Book(Product):
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, unique=True)
    page = models.IntegerField()
    language = models.CharField(max_length=100)

    class Meta:
        db_table = 'books'

class Electronic(Product):
    brand = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    power = models.CharField(max_length=100)

    class Meta:
        db_table = 'electronics'

class Fashion(Product):
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)

    class Meta:
        db_table = 'fashion'

class Cosmetic(Product):
    brand = models.CharField(max_length=100)
    skin_type = models.CharField(max_length=100)
    expiry_date = models.DateField()
    origin = models.CharField(max_length=100)

    class Meta:
        db_table = 'cosmetics'

class HealthCare(Product):
    brand = models.CharField(max_length=100)
    ingredient = models.TextField()
    expiry_date = models.DateField()
    usage = models.TextField()

    class Meta:
        db_table = 'health_care'

class Office(Product):
    brand = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=100)

    class Meta:
        db_table = 'office'

class Food(Product):
    brand = models.CharField(max_length=100)
    weight = models.CharField(max_length=50)
    expiry_date = models.DateField()
    origin = models.CharField(max_length=100)

    class Meta:
        db_table = 'food'

class Sports(Product):
    brand = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    weight = models.CharField(max_length=50)
    sport_type = models.CharField(max_length=100)

    class Meta:
        db_table = 'sports'

class Toys(Product):
    brand = models.CharField(max_length=100)
    age_range = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    player_count = models.CharField(max_length=50)

    class Meta:
        db_table = 'toys'

class HomeKitchen(Product):
    brand = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    capacity = models.CharField(max_length=50)
    warranty = models.CharField(max_length=100)

    class Meta:
        db_table = 'home_kitchen'
