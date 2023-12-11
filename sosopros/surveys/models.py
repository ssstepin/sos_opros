from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Survey(models.Model):
    _user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=256)


class Question(models.Model):
    _survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    text = models.TextField()


class Option(models.Model):
    _question = models.ForeignKey(Question, on_delete=models.PROTECT)
    text = models.CharField(max_length=256)


class SubmitProxy(models.Model):
    _survey = models.ForeignKey(Survey, on_delete=models.PROTECT)


class QuestionResult(models.Model):
    _submission = models.ForeignKey(SubmitProxy, on_delete=models.PROTECT)
    option = models.ForeignKey(Option, on_delete=models.PROTECT)
