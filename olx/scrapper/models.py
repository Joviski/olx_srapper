from djongo import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

from typing import Iterable

class ListField(models.TextField):
    """
    A custom Django field to represent lists as comma separated strings
    """

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['token'] = self.token
        return name, path, args, kwargs

    def to_python(self, value):

        class SubList(list):
            def __init__(self, token, *args):
                self.token = token
                super().__init__(*args)

            def __str__(self):
                return self.token.join(self)

        if isinstance(value, list):
            return value
        if value is None:
            return SubList(self.token)
        return SubList(self.token, value.split(self.token))

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return
        assert(isinstance(value, Iterable))
        return self.token.join(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

class Scrap(models.Model):
    keyw= models.CharField(max_length=100)
    email= models.CharField(max_length=100)
    size= models.DecimalField(default= 20, decimal_places = 0, max_digits = 300, validators=[MinValueValidator(20)])

class Ad(models.Model):
    keyw = models.CharField(max_length=100)
    price= models.PositiveIntegerField()
    location= models.CharField(max_length=100)
    title= models.CharField(max_length=100)
    owner_name= models.CharField(max_length=100)
    owner_phone= models.CharField(max_length=100, default="NA")
    description= models.TextField(max_length=800)
    details= models.JSONField()
    extra= ListField()
    date= models.DateField(auto_now_add=True)


