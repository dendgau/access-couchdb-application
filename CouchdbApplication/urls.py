from django.conf.urls import patterns, url
from answer_question.views import ListQA, QADetail, QAAdd, remove_answer_question, remove_answer


urlpatterns = patterns(
	"",
	url(
		r"^$",
		ListQA.as_view(),
		name="home"
	),
	url(
		r"^add_answer_question",
		QAAdd.as_view(),
		name="add_answer_question"
	),
	url(
		r'^edit_answer_question/(?P<question_id>.*)',
		QADetail.as_view(),
		name='edit_answer_question'),
	url(
		r"^remove_answer_question",
		remove_answer_question,
		name="remove_answer_question"
	),
	url(
		r"^remove_answer",
		remove_answer,
		name="remove_answer"
	)
)

