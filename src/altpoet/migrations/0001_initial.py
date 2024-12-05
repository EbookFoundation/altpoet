# Generated by Django 4.2.17 on 2024-12-05 20:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=80)),
                ('hash', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('url', models.CharField(default='', max_length=80)),
                ('basepath', models.CharField(default='/{item)', max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(default='/{item)', max_length=80)),
                ('base', models.CharField(default='', max_length=80)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pages', to='altpoet.project')),
            ],
        ),
        migrations.CreateModel(
            name='Img',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_id', models.CharField(max_length=80, null=True)),
                ('img_type', models.IntegerField(default=0)),
                ('described_by', models.CharField(max_length=80, null=True)),
                ('alt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='imgs', to='altpoet.image')),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='altpoet.image')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imgs', to='altpoet.page')),
            ],
        ),
        migrations.CreateModel(
            name='Alt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(default='', max_length=1000)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('source', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alts', to='altpoet.agent')),
            ],
        ),
    ]
