# Generated by Django 4.1.3 on 2022-11-30 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='journey',
            name='isActive',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='journey',
            name='number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]