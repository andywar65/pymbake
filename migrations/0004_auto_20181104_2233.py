# Generated by Django 2.0.9 on 2018-11-04 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pymbake', '0003_auto_20181029_2333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pymbakefinishingpage',
            old_name='intro',
            new_name='introduction',
        ),
        migrations.RenameField(
            model_name='pymbakepage',
            old_name='intro',
            new_name='introduction',
        ),
        migrations.RenameField(
            model_name='pymbakepartitionpage',
            old_name='intro',
            new_name='introduction',
        ),
    ]
