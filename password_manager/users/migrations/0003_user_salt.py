# Generated by Django 4.2.7 on 2023-11-13 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='salt',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]