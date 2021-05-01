from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.


class ExpenseList(models.Model):
    choices = (('Groceries and Eatables','Groceries and Eatables'),('Trips and Eating outs','Trips and Eating outs'),('Hobbies/Entertainment','Hobbies/Entertainment'),('Fixed Expenses','Fixed Expenses'),('others','others'))
    item = models.CharField(max_length=100)
    price = models.IntegerField()
    time = models.TimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.CharField(max_length=100,choices=choices,default='others')

    def __str__(self):
        return f'{self.item}-{self.author}'

    def get_absolute_url(self):
        return reverse('update', kwargs={'pk':self.pk})