# Generated by Django 4.2.3 on 2024-06-12 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_extractor', '0018_testresult_grad_cam'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfmodel',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
