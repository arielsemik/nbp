from django.http import HttpResponse
from django.template import loader

def index(request):
    template = loader.get_template("index.html")
    context = {
        # "latest_question_list": latest_question_list,
    }
    return HttpResponse(template.render(context, request))

def get_rates(request):

    return HttpResponse("You're looking at question %s.")