# Generated by Django 5.1.4 on 2025-01-08 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="posts",
            name="filename",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="파일명"
            ),
        ),
        migrations.AddField(
            model_name="posts",
            name="original_filename",
            field=models.CharField(
                blank=100, max_length=100, null=True, verbose_name="원본파일명"
            ),
        ),
    ]
