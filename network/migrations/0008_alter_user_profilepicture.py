# Generated by Django 3.2.12 on 2022-05-28 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_auto_20220527_0812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profilePicture',
            field=models.ImageField(blank=True, default='network/profilePictures/default.png', null=True, upload_to='profilePictures/'),
        ),
    ]
