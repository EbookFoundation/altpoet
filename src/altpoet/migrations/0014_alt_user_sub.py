# Generated by Django 4.2.20 on 2025-05-06 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('altpoet', '0013_usersubmission_submission_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='alt',
            name='user_sub',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alts_created', to='altpoet.usersubmission'),
        ),
    ]
