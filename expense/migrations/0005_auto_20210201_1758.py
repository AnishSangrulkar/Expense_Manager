# Generated by Django 3.1.4 on 2021-02-01 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0004_auto_20210201_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenselist',
            name='category',
            field=models.CharField(choices=[('Groceries', 'Groceries'), ('Trips', 'Trips and Eating outs'), ('Entertain', 'Hobbies/Entertainment'), ('Fixed', 'Fixed Expenses'), ('others', 'others')], default='others', max_length=100),
        ),
    ]
