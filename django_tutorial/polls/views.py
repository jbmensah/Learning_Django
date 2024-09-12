import datetime
from django.test import TestCase
from django.utils import timezone
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Choice, Question



def create_question(question_text, days):
	"""
	Create a question with the given `question_text` and published the
	given number of `days` offset to now (negative for questions published
	in the past, positive for questions that have yet to be published).
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		"""
		If no questions exist, an appropriate message is displayed.
		"""
		response = self.client.get(reverse("polls:index"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context["latest_question_list"], [])

	def test_past_question(self):
		"""
		Questions with a pub_date in the past are displayed on the
		index page.
		"""
		question = create_question(question_text="Past question.", days=-30)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerysetEqual(
			response.context["latest_question_list"],
			[question],
		)

	def test_future_question(self):
		"""
		Questions with a pub_date in the future aren't displayed on
		the index page.
		"""
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse("polls:index"))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context["latest_question_list"], [])

	def test_future_question_and_past_question(self):
		"""
		Even if both past and future questions exist, only past questions
		are displayed.
		"""
		question = create_question(question_text="Past question.", days=-30)
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerysetEqual(
			response.context["latest_question_list"],
			[question],
		)

	def test_two_past_questions(self):
		"""
		The questions index page may display multiple questions.
		"""
		question1 = create_question(question_text="Past question 1.", days=-30)
		question2 = create_question(question_text="Past question 2.", days=-5)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerysetEqual(response.context["latest_question_list"],
            [question2, question1])

class IndexView(generic.ListView):
	template_name = "polls/index.html"
	context_object_name = "latest_question_list"

	def get_queryset(self):
		"""Return the last five published questions."""
		return Question.objects.order_by("-pub_date")[:5]
	


class DetailView(generic.DetailView):
	model = Question
	template_name = "polls/detail.html"

def get_qurey(self):
	"""
	Excludes any question that aren't publishee yet.
	"""
	return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
	model = Question
	template_name = "polls/results.html"

def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST["choice"])
	except (KeyError, Choice.DoesNotExist):
		# Redisplay the question voting form.
		return render(
			request,
			"polls/detail.html",
			{
				"question": question,
				"error_message": "You didn't select a choice.",
			},
		)
	else:
		selected_choice.votes = F("votes") + 1
		selected_choice.save()
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a
		# user hits the Back button.
		return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
	
# Function based views
# def index(request):
# 	latest_question_list = Question.objects.order_by('-pub_date')[:5]
# 	template = loader.get_template("polls/index.html")
# 	context = {
# 		'latest_question_list': latest_question_list
# 	}
# 	return render(request, "polls/index.html", context)

# def detail(request, question_id):
# 	# try:
# 	question = get_object_or_404(Question, pk=question_id)
# 	# except Question.DoesNotExist:
# 	# 	raise Http404("Question does not exist")
# 	return render(request, "polls/detail.html", {"question": question})

# def results(request, question_id):
# 	# response = "You're looking at the results of question %s."
# 	# return HttpResponse(response % question_id)
# 	question = get_object_or_404(Question, pk=question_id)
# 	return render(request, "polls/results.html", {"question": question})