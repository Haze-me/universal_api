# Generated by Django 5.2 on 2025-04-17 12:59

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('api_key', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('db_type', models.CharField(choices=[('mongodb', 'MongoDB'), ('postgresql', 'PostgreSQL'), ('mysql', 'MySQL'), ('sqlite', 'SQLite')], max_length=20)),
                ('connection_type', models.CharField(choices=[('params', 'Connection Parameters'), ('string', 'Connection String')], max_length=20)),
                ('connection_string', models.TextField(blank=True, null=True)),
                ('db_host', models.CharField(blank=True, max_length=255, null=True)),
                ('db_port', models.IntegerField(blank=True, null=True)),
                ('db_name', models.CharField(blank=True, max_length=255, null=True)),
                ('db_user', models.CharField(blank=True, max_length=255, null=True)),
                ('db_password', models.CharField(blank=True, max_length=255, null=True)),
                ('target_table', models.CharField(max_length=255)),
                ('verification_method', models.CharField(choices=[('email', 'Email Verification'), ('phone', 'Phone Verification'), ('none', 'No Verification')], default='email', max_length=10)),
                ('validation_rules', models.JSONField(blank=True, default=dict)),
            ],
        ),
    ]
