# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BinaryFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('the_file', models.FileField(upload_to=b'uploads')),
                ('filename', models.CharField(max_length=255)),
                ('filesize', models.IntegerField()),
                ('hash', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BinaryOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target', models.CharField(max_length=128)),
                ('architecture', models.CharField(max_length=128)),
                ('extra_options', models.CharField(default=b'{"flags" : [] }', max_length=256)),
                ('base_address', models.CharField(max_length=18)),
            ],
        ),
        migrations.CreateModel(
            name='BinaryStringStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('binary_string', models.TextField()),
                ('binary_options', models.OneToOneField(to='odaweb.BinaryOptions')),
            ],
        ),
        migrations.CreateModel(
            name='InstDoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.TextField()),
                ('mnemonic', models.TextField()),
                ('short', models.TextField()),
                ('long', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='OdaMaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ipAddress', models.CharField(default=b'', max_length=64)),
                ('project_name', models.CharField(default=b'', max_length=64)),
                ('short_name', models.CharField(max_length=12, db_index=True)),
                ('revision', models.IntegerField(default=0)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('copy', models.ForeignKey(to='odaweb.OdaMaster', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OdbFileStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pickled_odb_file', models.BinaryField(null=True)),
                ('binary_file', models.ForeignKey(to='odaweb.BinaryFile', null=True)),
                ('binary_string', models.ForeignKey(to='odaweb.BinaryStringStorage', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SandboxJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.IntegerField()),
                ('reloaded', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SandboxServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=255)),
                ('port', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16, db_index=True)),
                ('odaMaster', models.ForeignKey(to='odaweb.OdaMaster')),
            ],
        ),
        migrations.AddField(
            model_name='sandboxjob',
            name='server',
            field=models.ForeignKey(to='odaweb.SandboxServer', null=True),
        ),
        migrations.AddField(
            model_name='odamaster',
            name='odb_file_storage',
            field=models.ForeignKey(to='odaweb.OdbFileStorage', null=True),
        ),
        migrations.AddField(
            model_name='odamaster',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='odamaster',
            name='sandbox_job',
            field=models.ForeignKey(to='odaweb.SandboxJob', null=True),
        ),
        migrations.AddField(
            model_name='binaryfile',
            name='binary_options',
            field=models.OneToOneField(null=True, to='odaweb.BinaryOptions'),
        ),
    ]
