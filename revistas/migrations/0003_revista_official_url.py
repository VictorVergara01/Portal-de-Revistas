# Generated by Django 5.1.3 on 2024-12-02 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revistas', '0002_revista_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='revista',
            name='official_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]