# Generated by Django 3.0.6 on 2020-06-08 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader_app', '0002_auto_20200606_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='essay',
            name='raw_body',
            field=models.TextField(default=''),
        ),
    ]
