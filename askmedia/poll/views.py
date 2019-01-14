from django.shortcuts import render, reverse
from .models import *
from django.http import Http404, HttpResponseRedirect
from django.views.generic import ListView, View

class QuestionList(ListView):
    template_name = 'poll/index.html'
    context_object_name = 'latest_question_list'

    def show_question_include_choice(self):
        return Question.objects.exclude(choice__isnull=True)

    def get_queryset(self):
        return self.show_question_include_choice().filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailList(ListView):
    template_name = 'poll/details.html'
    context_object_name = 'question'

    def get_queryset(self, **kwargs):
        try:
            question = Question.objects.get(id=self.kwargs.get('question_id'), pub_date__lte=timezone.now())
        except Question.DoesNotExist:
            raise Http404("Question does not exist")
        return question

class VoteView(View):
    template_name = 'poll/details.html'

    def get(self, requests):
        context = {}
        return render(requests, 'poll/details.html', context)

    def post(self, request, question_id):
        question = Question.objects.get(id=question_id)
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            context = {
                'question': question,
                'error_message': "You didn't select a choice.",
            }
            return render(request, 'poll/details.html', context)
        else:
            selected_choice.votes += 1
            selected_choice.save()
            return HttpResponseRedirect(reverse('poll:results', args=(question.id,)))

class ResultView(ListView):
    template_name = 'poll/result.html'
    context_object_name = 'question'

    def get_queryset(self, **kwargs):
        try:
            question = Question.objects.get(id=self.kwargs.get('question_id'))
        except Question.DoesNotExist:
            raise Http404("Result does not exist")
        return question
