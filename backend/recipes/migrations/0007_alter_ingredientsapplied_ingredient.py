# Generated by Django 3.2.3 on 2023-11-06 20:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_ingredientsapplied_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsapplied',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes_ings', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
    ]
