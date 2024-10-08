# Generated by Django 4.2.3 on 2024-08-14 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_extractor', '0020_study_trainingsession_study'),
        ('datasets', '0014_image_used_for_testing_image_used_for_training_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='shared',
            field=models.ManyToManyField(blank=True, related_name='shared_datasets', to='feature_extractor.study'),
        ),
    ]
