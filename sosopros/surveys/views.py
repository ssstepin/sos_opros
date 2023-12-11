from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView
from .models import *

import plotly
import plotly.express as px


# Create your views here.

class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',)


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)

        return super(RegisterView, self).form_valid(form)


class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = ["title"]


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ["text"]


class OptionForm(ModelForm):
    class Meta:
        model = Option
        fields = ["text"]


class QuestionStatistics:
    def __init__(self, question, chart):
        self.question = question
        self.chart = chart


def get_chart(): # debug
    q = {
        'a': 3,
        'b': 3,
    }
    fig = px.pie(values=q.values(), names=q.keys(), title=f"ABOBA")
    return fig.to_html()


def home(request):
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('/home')


@login_required
def get_user_surveys(request):
    cur_user = request.user
    surveys = Survey.objects.filter(_user=cur_user)
    return render(request, "surveys/user_surveys.html", {"surveys": surveys})


@login_required
def survey_details(request, pk):
    survey = Survey.objects.prefetch_related('question_set').get(pk=pk, _user=request.user)
    questions = [QuestionStatistics(q, get_chart()) for q in survey.question_set.all()]
    return render(request, "surveys/survey.html", {"survey": survey, "questions": questions})


@login_required
def edit_survey(request, pk):
    survey = Survey.objects.prefetch_related('question_set').get(pk=pk, _user=request.user)

    if request.method == "POST":
        survey.save()
        return redirect("survey_details", pk=pk)
    else:
        related_questions = survey.question_set.all()
        return render(request, "surveys/edit.html", {"survey": survey, "questions": related_questions})


@login_required
def create_survey(request):
    survey_form = {}
    if request.method == "GET":
        survey_form = SurveyForm()

    elif request.method == "POST":
        survey_form = SurveyForm(request.POST)
        if survey_form.is_valid():
            new_survey = survey_form.save(commit=False)  # Now don't save to DB
            new_survey._user = request.user
            new_survey.save()  # Now save
            return redirect("survey_edit", pk=new_survey.id)
    return render(request, "surveys/create.html", {"form": survey_form})


@login_required
def create_question(request, pk):
    question_form = {}
    survey = get_object_or_404(Survey, pk=pk, _user=request.user)
    if request.method == "GET":
        question_form = QuestionForm()
    elif request.method == "POST":
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            new_question = question_form.save(commit=False)
            new_question._survey = survey
            new_question.save()
            return redirect("option_create", spk=pk, qpk=new_question.pk)
    return render(request, "surveys/question_create.html", {'survey': survey, 'form': question_form})


@login_required
def create_option(request, spk, qpk):
    option_form = {}
    related_survey = get_object_or_404(Survey, pk=spk, _user=request.user)
    related_question = Question.objects.get(pk=qpk)
    if request.method == "GET":
        option_form = OptionForm()
    elif request.method == "POST":
        option_form = OptionForm(request.POST)
        if option_form.is_valid():
            new_option = option_form.save(commit=False)
            new_option._question_id = related_question.pk
            new_option.save()

    question_options = related_question.option_set.all()
    return render(request, "surveys/options.html",
                  {'survey': related_survey, 'question': related_question, 'options': question_options,
                   'form': option_form})
