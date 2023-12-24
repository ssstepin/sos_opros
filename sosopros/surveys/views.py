from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Form, ChoiceField, RadioSelect, BaseFormSet, formset_factory
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

def home_redirect(request):
    return redirect('/home')


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


class SubmissionForm(Form):
    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options")
        choices = {(op.pk, op.text) for op in options}
        super().__init__(*args, **kwargs)
        op_field = ChoiceField(choices=choices, widget=RadioSelect, required=True)
        self.fields["option"] = op_field


def create_question_form(questions, formset):
    return zip(questions, formset)


class BaseSubmissionFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        ret = super().get_form_kwargs(index)
        ret["options"] = ret["options"][index]
        return ret


def begin_survey(request, spk):
    survey = get_object_or_404(Survey, pk=spk)
    if request.method == "POST":
        submission = SubmitProxy.objects.create(_survey=survey)
        return redirect("survey_submit", survey_key=spk, submit_key=submission.pk)
    else:
        return render(request, "surveys/start.html", {"survey": survey})


def submit_survey(request, survey_key, submit_key):
    survey = Survey.objects.prefetch_related("question_set__option_set").get(pk=survey_key)
    submission = survey.submitproxy_set.get(pk=submit_key)
    all_options = [q.option_set.all() for q in survey.question_set.all()]
    SubmissionFormSet = formset_factory(SubmissionForm, extra=len(survey.question_set.all()), formset=BaseSubmissionFormSet)  # creating class
    if request.method == "POST":
        formset = SubmissionFormSet(request.POST, form_kwargs={"empty_permitted": False, "options": all_options})
        # print([form.has_changed() for form in formset])
        if formset.is_valid() and all([form.has_changed() for form in formset]):
            for form in formset:
                QuestionResult.objects.create(
                    option_id=form.cleaned_data["option"], _submission_id=submit_key,
                )

            submission.is_complete = True
            submission.save()
            return redirect("survey_end", spk=survey_key)
        else:
            messages.error(request, "Survey isn't filled")
            return redirect("survey_submit", survey_key=survey_key, submit_key=submit_key)

    else:
        formset = SubmissionFormSet(form_kwargs={"empty_permitted": False, "options": all_options})

    return render(
        request,
        "surveys/submit.html",
        {"survey": survey, "question_forms": create_question_form(survey.question_set.all(), formset),
         "formset": formset},
    )

def survey_end(request, spk):
    messages.success(request, "Thanks for submitting!")
    return redirect('/home')