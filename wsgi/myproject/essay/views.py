from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from .models import EssayModel, CronJob, Essay
# from .forms import DocumentForm


def index(request):
    # messages.add_message(request, messages.INFO, 'Hello world.')
    # messages.add_message(request, messages.DEBUG, 'Hello world.')
    # messages.add_message(request, messages.SUCCESS, 'Hello world.')
    # messages.add_message(request, messages.WARNING, 'Hello world.')
    # messages.add_message(request, messages.ERROR, 'Hello world.')
    essaysets = EssayModel.objects.all()
    context = {
            'essaysets': essaysets
            }
    return render(request, 'essay/index.html', context)


def register(request):
    if request.method == 'GET':
        return render(request, 'essay/register.html')
    elif request.method == 'POST':
        name = request.POST.get('name')
        info = request.POST.get('info')
        train_file = request.FILES['train_file']
        train_len = request.POST.get('train_len')
        essayModel = EssayModel(name=name, info=info,
                                train_file=train_file, train_len=train_len)
        essayModel.save()
        context = {
                'flash': True,
                'success': True
                }
        # context = {
                # 'flash': True,
                # 'success': False
                # }
        return render(request, 'essay/register.html', context)


# Evaluate
def view(request, essayModel_id):
    try:
        essayModel = EssayModel.objects.get(pk=essayModel_id)
        if request.method == 'GET':
            essay_text = ''
            previous_user_essay = 'None'
            if request.user.is_authenticated():
                previous_user_essay = Essay.objects.\
                                        filter(user=request.user,
                                               essaymodel=essayModel).\
                                        order_by('-created_at')
                if previous_user_essay.count():
                    essay_text = previous_user_essay.first().text
                paginator = Paginator(previous_user_essay, 5)
                page = request.GET.get('p_u_e_page')
                try:
                    previous_user_essay = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    previous_user_essay = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    previous_user_essay = paginator.page(paginator.num_pages)
            context = {
                    'essayModel': essayModel,
                    'autofocus': 'autofocus',
                    'essay_text': essay_text,
                    'previous_user_essay': previous_user_essay,
                    }
            return render(request, 'essay/detail.html', context)
        elif request.method == 'POST':
            essay_text = request.POST.get('essay_text')
            t = essayModel.evalute(essay_text)
            if request.user.is_authenticated():
                essay_submit = Essay(user=request.user, essaymodel=essayModel,
                                     predicted_mark=t, text=essay_text)
                essay_submit.save()
            alert = "alert-success" if t >= 4.8 else "alert-warning"
            scored_message = "Nice Work" if t >= 4.8 else "Need More Effort"
            context = {
                        'marks_scored': t,
                        'alert': alert,
                        'scored_message': scored_message
                    }
            return HttpResponse(json.dumps(context),
                                content_type="application/json"
                            )
    except EssayModel.DoesNotExist:
        raise Http404("Essay Model does not Exist")
