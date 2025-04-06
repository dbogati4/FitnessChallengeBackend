# Generated by Django 5.2 on 2025-04-06 01:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FitnessChallenges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='user_images/')),
                ('caption', models.CharField(max_length=1000, null=True)),
                ('profile_video', models.FileField(blank=True, null=True, upload_to='user_videos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='FitnessChallenges.user')),
            ],
        ),
    ]
