# Generated by Django 5.0 on 2023-12-11 09:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SubmitProxy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=256)),
                ('_question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.question')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.option')),
                ('_submission', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.submitproxy')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='submitproxy',
            name='_survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.survey'),
        ),
        migrations.AddField(
            model_name='question',
            name='_survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.survey'),
        ),
    ]