from tkinter import CASCADE
from django.db import models

from users.models import CustomUser

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(to=CustomUser, related_name="user_category", on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    category = models.ForeignKey(to=Category, related_name="ingredients", on_delete=models.DO_NOTHING)
    user = models.ForeignKey(to=CustomUser, related_name="user_ingredient", on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

