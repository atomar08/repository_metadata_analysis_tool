# Generated by Django 2.2.2 on 2019-06-08 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo_name', models.CharField(max_length=50, unique=True)),
                ('latest_commit_no', models.IntegerField()),
                ('latest_commit_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'repo',
            },
        ),
        migrations.CreateModel(
            name='RepoMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commit_no', models.IntegerField(default=1)),
                ('repo_name', models.CharField(max_length=50)),
                ('commit_id', models.CharField(max_length=50, null=True)),
                ('author_name', models.CharField(max_length=20, null=True)),
                ('commit_date', models.DateTimeField()),
                ('commit_message', models.CharField(max_length=200, null=True)),
                ('files', models.CharField(max_length=3000, null=True)),
            ],
            options={
                'db_table': 'repo_metadata',
            },
        ),
    ]
