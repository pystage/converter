# Generated by Django 4.2.13 on 2024-05-31 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversion',
            name='language',
            field=models.CharField(default='en', max_length=20),
            preserve_default=False,
        ),
    ]
