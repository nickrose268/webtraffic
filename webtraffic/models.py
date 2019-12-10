from django.db import models
import datetime
from django.urls import reverse, reverse_lazy

class GaDimension(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    use = models.BooleanField(default=False)

    # def get_absolute_url(self):
    #     return reverse("webtraffic:ga_dimension_detail", kwargs={'id': self.id})

    def __str__(self):
        return self.name

class GaMetric(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    use = models.BooleanField(default=False)

    # def get_absolute_url(self):
    #     return reverse("webtraffic:ga_dimension_detail", kwargs={'id': self.id})

    def __str__(self):
        return self.name
