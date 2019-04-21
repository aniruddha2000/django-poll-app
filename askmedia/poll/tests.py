import datetime
from django.urls import reverse, resolve
from django.utils import timezone
from django.test import SimpleTestCase, TestCase, Client
from .views import (
    QuestionList,
    DetailList,
    VoteView,
    ResultView
)
from .models import (
    Question,
    Choice
)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text, votes):
    """
    Create a choice with the given `choice_text` and published the
    given number of `votes` and refer to a `question`.
    """
    return Choice.objects.create(question=question, choice_text=choice_text, votes=votes)

class TestUrl(SimpleTestCase):
    """
    This class test our URls
    """
    def test_index_url(self):
        """Test our index url"""
        url = reverse('poll:index')
        self.assertEquals(resolve(url).func.view_class, QuestionList)

    def test_detail_url(self):
        """Test our detail url"""
        url = reverse('poll:detail', args=['5'])
        self.assertEquals(resolve(url).func.view_class, DetailList)

    def test_vote_url(self):
        """Test our vote url"""
        url = reverse('poll:vote', args=['2'])
        self.assertEquals(resolve(url).func.view_class, VoteView)

    def test_result_url(self):
        """Test our result url"""
        url = reverse('poll:results', args=['2'])
        self.assertEquals(resolve(url).func.view_class, ResultView)

class TestModels(TestCase):

    def setUp(self):
        self.question1 = create_question(question_text="Capital of UK", days=1)
        self.choice1 = create_choice(question=self.question1, choice_text='London', votes=3)
        self.choice2 = create_choice(question=self.question1, choice_text='Berlin', votes=1)
        self.choice3 = create_choice(question=self.question1, choice_text='Paris', votes=0)

    def test_question_is_created(self):
        self.assertEquals(self.question1.question_text, 'Capital of UK')

    def test_choice_is_created(self):
        self.assertEquals(self.choice1.question, self.question1)
        self.assertEquals(self.choice2.question, self.question1)
        self.assertEquals(self.choice3.question, self.question1)
        self.assertEquals(self.choice1.choice_text, 'London')
        self.assertEquals(self.choice2.choice_text, 'Berlin')
        self.assertEquals(self.choice3.choice_text, 'Paris')
        self.assertEquals(self.choice1.votes, 3)
        self.assertEquals(self.choice2.votes, 1)
        self.assertEquals(self.choice3.votes, 0)

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEquals(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertEquals(old_question.was_published_recently(), False)

class TestQuestionWithNoChoice(TestCase):
    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertEquals(recent_question.was_published_recently(), True)

class QuestionIndexViewTests(TestCase):
    client = Client()
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('poll:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_question_without_choice(self):
        create_question(question_text="No choice question.", days=-30)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=30)
        url = reverse('poll:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_past_questions(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-30)
        url = reverse('poll:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultViewTest(TestCase):
    def test_future_questions(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=30)
        url = reverse('poll:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_past_questions(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-30)
        url = reverse('poll:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
