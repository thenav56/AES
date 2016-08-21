from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json

from .models import EssayModel, CronJob, Essay
# from .forms import DocumentForm


# Helper function for  index and search
def essayset_paginator(request, essaysets):
    paginator = Paginator(essaysets, 10)
    page = request.GET.get('e_page')

    try:
        essaysets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        essaysets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        essaysets = paginator.page(paginator.num_pages)
    context = {
            'essaysets': essaysets
            }
    return context


def index(request):
    # messages.add_message(request, messages.INFO, 'Hello world.')
    # messages.add_message(request, messages.DEBUG, 'Hello world.')
    # messages.add_message(request, messages.SUCCESS, 'Hello world.')
    # messages.add_message(request, messages.WARNING, 'Hello world.')
    # messages.add_message(request, messages.ERROR, 'Hello world.')
    essaysets = EssayModel.objects.all()
    context = essayset_paginator(request, essaysets)
    return render(request, 'essay/index.html', context)


def search(request):
    query = request.GET.get('query')
    essaysets = EssayModel.objects.filter(name__contains=query)
    context = essayset_paginator(request, essaysets)
    context.update({
        'search': True,
        'query': query,
        })
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
            submitted_essay = None

            if request.user.is_authenticated():
                previous_user_essay = Essay.objects.\
                                        filter(user=request.user,
                                               essaymodel=essayModel).\
                                        order_by('-created_at')

                if previous_user_essay.count():
                    essay_text = previous_user_essay.first().text

                paginator = Paginator(previous_user_essay, 3)
                page = request.GET.get('p_u_e_page')

                try:
                    previous_user_essay = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    previous_user_essay = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    previous_user_essay = paginator.page(paginator.num_pages)

                if request.user.is_superuser:
                    paginator = Paginator(essayModel.essays.all(), 3)
                    page = request.GET.get('s_e_page')

                    try:
                        submitted_essay = paginator.page(page)
                    except PageNotAnInteger:
                        # If page is not an integer, deliver first page.
                        submitted_essay = paginator.page(1)
                    except EmptyPage:
                        # If page is out of range (e.g. 9999), deliver last page of results.
                        submitted_essay = paginator.page(paginator.num_pages)

            context = {
                    'essayModel': essayModel,
                    'autofocus': 'autofocus',
                    'essay_text': essay_text,
                    'previous_user_essay': previous_user_essay,
                    'submitted_essay': submitted_essay,
                    }

            return render(request, 'essay/detail.html', context)

    except EssayModel.DoesNotExist:
        raise Http404("Essay Model does not Exist")


def evalute_essay_text(request):
    if request.method == 'POST':
        essayModel_id = request.POST.get('essayModel_id')
        try:
            essayModel = EssayModel.objects.get(pk=essayModel_id)
        except EssayModel.DoesNotExist:
            context = { 'error': 'EssayModel DoesNotExist, Please Refresh\
                    the page', 'error_code': '404' }
            return HttpResponse(json.dumps(context),
                                content_type="application/json")
        # import time
        # time.sleep(.4)
        essay_text = request.POST.get('essay_text')

        if essayModel.cronjob.get_status_display() == 'finished':
            t = essayModel.evalute(essay_text)
        else:
            context = { 'error': 'Model status is not finished, Try Again\
                    Later', 'error_code': '503' }
            return HttpResponse(json.dumps(context),
                                content_type="application/json")

        if request.user.is_authenticated():
            try:
                essay_submit = Essay.objects.filter(user=request.user,
                                                  essaymodel=essayModel).first()
                if essay_submit is None:
                    essay_submit = Essay(user=request.user, essaymodel=essayModel,
                                         predicted_mark=t, text=essay_text)
                else:
                    essay_submit.text = essay_text
                essay_submit.save()
            except IntegrityError as e:
                pass

        alert = "alert-success" if t >= 4.8 else "alert-warning"
        scored_message = 'Nice Work <span class="glyphicon\
                         glyphicon-thumbs-up"></span>' \
                         if t >= 4.8 else "Need More Effort"
        context = {
                    'marks_scored': t,
                    'alert': alert,
                    'scored_message': scored_message,
                    'grammer' : 100*(t/(12)),
                    'cspell' : 100*(12/(8*t)),
                    'bagofwords' : 100*(t/(1.3*12))
                }

        return HttpResponse(json.dumps(context),
                            content_type="application/json"
                        )

def essay_original_submit(request):
    response = 'Invalid Request'
    alert = 'danger'
    if request.method == 'POST' and request.user.is_superuser:
        essayID = request.POST['essayID']
        essay = Essay.objects.get(pk=essayID)
        if essay:
            original_mark = request.POST['o_mark']
            essay.original_mark =  original_mark
            essay.save()
            response = 'Updated'
            alert = 'success'
        else:
            response = 'Essay Does Not Exist'

    context = { 'response': response, 'alert': alert }
    return HttpResponse(json.dumps(context),
                        content_type="application/json")


def load_graph(request, essayModel_id):
    context = {'error' : 'Unknown Method'}
    # import time
    # time.sleep(0.5)
    if request.method == 'POST':
        graph_name = request.POST.get('graph_name')
        essayModel = EssayModel.objects.get(pk=essayModel_id)
        if graph_name == 'HISTOGRAM':
            data = essayModel.graph_data_read('histogram')
            original = [key for key in data]
            predicted = [ sum(values)/len(values) for key, values in data.items()]
            context = {
                    'predicted_y':predicted,
                    'original_x':original,
                    'original_y':original
                    }

        elif essayModel.name == 'computer' and graph_name == 'HISTOGRAM-casestudy':
            context = {
                    'predicted_x':[1,2,3,4,5,6,7,8,9,10,11,
                                   12,13,14,15,16,17,18,19,20],
                    'predicted_y':[7, 9, 9, 6, 9, 7, 8, 8, 7,
                                   6, 6, 7, 8, 9, 7, 6, 6, 8, 7, 8],
                    'original_x':[1,2,3,4,5,6,7,8,9,10,11,
                                   12,13,14,15,16,17,18,19,20],
                    'original_y':[8, 10, 8, 6, 7, 6, 8, 6, 7,
                                  7, 6, 7, 7, 9, 8, 5, 6, 7, 7, 7],
                    }
        elif graph_name == 'ROC':
            data = essayModel.graph_data_read('roc')
            data = zip(data[0], data[1])
            data = sorted(data, key=lambda d: d[0])
            x, y = zip(*data)
            context = {
                    'original_x': x,
                    'original_y': y,
                    }
        elif graph_name == 'CONFUSION':
            data = essayModel.graph_data_read('confusion')
            classes = ['class:'+str(i) for i in range(2, 13)]
            data = [[i/(sum(ele,1)) for i in ele] for ele in data]
            context = {
                    'x': classes,
                    'y': classes[::-1],
                    'matrix': data[::-1],
                    }
        elif graph_name == 'SCATTER':
            context = {
                    'class_data':[{
                'x_data':[0,1,2,3,4,5,6,7,8,9,10,11,
                       12,13,14,15,16,17,18,19,20],
                'y_data':[8,8,8,7,8,8,8,3,4,7,4,
                         7,4,5,8,9,7,6,4,3]
                },
            {
                'x_data':[0,1,2,3,4,5,6,7,8,9,10,11,
                       12,13,14,15,16,17,18,19,20],
                'y_data':[8,7,8,7,7,8,8,3,4,9,4,
                        6,3,7,6,10,8,6,4,4]
                },
            {
                'x_data':[0,1,2,3,4,5,6,7,8,9,10,11,
                       12,13,14,15,16,17,18,19,20],
                'y_data':[7,4,5,8,9,7,6,8,8,8,7,8,8,
                        8,3,4,7,4,4,3]
                                },]
            }
    return HttpResponse(json.dumps(context),
                        content_type="application/json")

