# -*- coding: utf-8 -*-
import json
import logging
from django import http
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse

from answer_question.couch_server import ConnectCouchdb


class JSONResponseMixin(object):
	def render_to_response(self, context):
		return self.get_json_response(self.convert_context_to_json(context))

	def get_json_response(self, content, **http_response_kwargs):
		return http.HttpResponse(
			content,
			content_type='application/json',
			**http_response_kwargs
		)

	def convert_context_to_json(self, context):
		return json.dumps(context)


class ListQA(ListView):
	paginate_by = 20
	template_name = "answer_question/list_answer_question.html"

	def get_queryset(self):
		couch_server = ConnectCouchdb()
		map_func = 'function(doc) {if(doc.table=="question"){emit(doc.id, doc);}}'

		queryset = [
			{
				"id": str(q["value"]["_id"]),
				"category": str(q["value"]["category"]),
				"type": str(q["value"]["type"]),
				"content": str(q["value"]["content"]),
			}
			for q in couch_server.query_doc(map_func)
		]
		return queryset


class QADetail(TemplateView, JSONResponseMixin):
	template_name = "answer_question/edit_answer_question.html"

	def get_context_data(self, **kwargs):
		question_id = str(self.kwargs.get("question_id", None))
		couch_server = ConnectCouchdb()
		doc_question = couch_server.get_doc(question_id)

		context = super(QADetail, self).get_context_data(**kwargs)
		context["question_id"] = question_id
		context["question"] = str(doc_question["content"])
		context["category"] = str(doc_question["category"])
		context["type"] = str(doc_question["type"])
		context["answers"] = []

		if doc_question["answer_id"]:
			for answer_id in filter(None, doc_question["answer_id"]):
				doc_answer = couch_server.get_doc(answer_id)
				doc_answer.update({"id": answer_id})
				context["answers"].append(doc_answer)

		return context

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				question_id = kwargs.get("question_id")
			except Exception, e:
				logging.error(str(e))
				return HttpResponse(status=500)

			question = str(request.POST["question"])
			answers = filter(None, request.POST.getlist('answer'))
			category = str(request.POST["categories"])
			type_answers = str(request.POST["type-answers"])

			_doc_question = {
				"content": question,
				"type": type_answers,
				"category": category,
			}

			couch_server = ConnectCouchdb()
			doc_question = couch_server.get_doc(question_id)
			doc_question.update(_doc_question)

			if doc_question["type"] != "03" and answers:
				for answer in answers:
					_doc_answer = {
						"content": str(answer),
						"table": "answer",
						"question_id": doc_question["_id"]
					}
					doc_answer = couch_server.save_doc(_doc_answer)
					doc_question["answer_id"].append(doc_answer["_id"])
			elif doc_question["type"] == "03":
				del (doc_question["answer_id"])[:]

			couch_server.save_doc(doc_question)

			messages.add_message(
				request,
				messages.SUCCESS,
				"SUCCESS: Question and answers have been edited successfully!"
			)
		return HttpResponseRedirect('')


class QAAdd(TemplateView, JSONResponseMixin):
	template_name = "answer_question/add_answer_question.html"

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':

			couch_server = ConnectCouchdb()
			question = str(request.POST["question"])
			answers = filter(None, request.POST.getlist('answer'))
			category = str(request.POST["categories"])
			type_answers = str(request.POST["type-answers"])

			_doc_question = {
				"table": "question",
				"content": question,
				"type": type_answers,
				"category": category,
				"answer_id": []
			}
			doc_question = couch_server.save_doc(_doc_question)

			if answers:
				for answer in answers:
					_doc_answer = {
						"content": str(answer),
						"table": "answer",
						"question_id": doc_question["_id"]
					}
					doc_answer = couch_server.save_doc(_doc_answer)
					doc_question["answer_id"].append(doc_answer["_id"])

			couch_server.save_doc(doc_question)

			messages.add_message(
				request,
				messages.SUCCESS,
				"SUCCESS: Question and answers have been created successfully!"
			)
		return HttpResponseRedirect('/edit_answer_question/%s' % doc_question["_id"])


@csrf_exempt
def remove_answer(request):
	if request.method == 'POST':
		try:
			answer_id = request.POST["answerId"]
			question_id = request.POST["questionId"]
		except Exception, e:
			logging.error(str(e))
			return HttpResponse(status=500)

		couch_server = ConnectCouchdb()
		doc_answer = couch_server.get_doc(answer_id)
		doc_question = couch_server.get_doc(question_id)

		couch_server.delete_doc(answer_id)
		doc_question["answer_id"].remove(answer_id)
		couch_server.save_doc(doc_question)

		return HttpResponse(status=200)

@csrf_exempt
def remove_answer_question(request):
	if request.method == 'POST':
		try:
			question_id = request.POST["questionId"]
		except Exception, e:
			logging.error(str(e))
			return HttpResponse(status=500)

		couch_server = ConnectCouchdb()
		doc_question = couch_server.get_doc(question_id)

		if doc_question:
			doc_answers = doc_question["answer_id"]
			couch_server.delete_doc(question_id)

			if doc_answers:
				for answer in doc_answers:
					couch_server.delete_doc(answer)

		messages.add_message(
			request,
			messages.SUCCESS,
			"SUCCESS: Question and answers have been deleted successfully!"
		)
		return HttpResponse(status=200)

