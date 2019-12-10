from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                    PermissionRequiredMixin
                                    )
from django.views.generic import (TemplateView, CreateView, DetailView,
                                ListView, UpdateView, DeleteView, FormView)
from django.db.models import Q
from . import models
from . import ga4, ga4models, panda
from .appsettings import AppSettings
import datetime

class HomeView(TemplateView):
    template_name = 'webtraffic/home.html'

@login_required
def ga_show(request, **kwargs):

    d_chosen = models.GaDimension.objects.filter(use=True).order_by('name')
    m_chosen = models.GaMetric.objects.filter(use=True).order_by('name')

    context = {
        'd_chosen': d_chosen,
        'm_chosen': m_chosen,
    }

    if request.method == 'POST':

        dimensions = request.POST.getlist('select_dimension')
        metrics = request.POST.getlist('select_metric')
        view_id = request.POST.get('view_id')
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')


        print(request.POST)

        print(f'DIMENSION: {dimensions}')
        print(f'METRIC: {metrics}')
        print(f'DATE_START: {date_start}')
        print(f'DATE_END: {date_end}')
        print(f'VIEW_ID: {view_id}')

        dates=[(date_start, date_end)]

        if dimensions and metrics:
            ga4con = ga4.Ga4Connector(view_id)

            status, message, result = ga4con.get_data(dates, metrics, dimensions)

            if status:
                context['headers'] = result.get('headers', [])
                context['data'] = result.get('data', [])
        else:
            message = 'Insufficient information passed to Google'

        context['message'] = message

    return render(request, 'webtraffic/data_show.html', context)

@login_required
def ga_list(request, **kwargs):
    qsd = models.GaDimension.objects.all().order_by('name')
    qsm = models.GaMetric.objects.all().order_by('name')

    d_chosen = qsd.filter(use=True)
    for record in d_chosen:
        print('DCHOSEN', record)
    m_chosen = qsm.filter(use=True)
    for record in m_chosen:
        print('MCHOSEN', record)

    if request.method == 'POST':

        if request.POST.get('remove'):
            for name in request.POST.getlist('d_rem'):
                print('D-CHOICE', name)
                models.GaDimension.objects.filter(name=name).update(use=False)
            for name in request.POST.getlist('m_rem'):
                print('M-CHOICE', name)
                models.GaMetric.objects.filter(name=name).update(use=False)

        if request.POST.get('reset'):
            models.GaMetric.objects.all().update(use=False)
            models.GaDimension.objects.all().update(use=False)

        if request.POST.get('add'):
            for name in request.POST.getlist('d_choice'):
                print('D-CHOICE', name)
                models.GaDimension.objects.filter(name=name).update(use=True)
            for name in request.POST.getlist('m_choice'):
                print('M-CHOICE', name)
                models.GaMetric.objects.filter(name=name).update(use=True)

        return redirect(reverse('webtraffic:ga_list'))

    context = {
        'dimensions': qsd,
        'metrics': qsm,
        'd_chosen': d_chosen,
        'm_chosen': m_chosen,
    }
    return render(request, 'webtraffic/ga_list.html', context)

@login_required
def userinfo_show(request, **kwargs):

    userinfo = {}
    userinfo['header'] = []
    userinfo['cookie'] = []
    userinfo['meta'] = []

    for i in request.COOKIES:
         userinfo['cookie'].append([i, request.COOKIES[i]])

    for i in request.headers:
         userinfo['header'].append([i, request.headers[i]])

    for i in request.META:
          userinfo['meta'].append([i, request.META[i]])

    userinfo['request'] = request

    userinfo['os'] = request.META.get('OS', 'Not available')

    userinfo['ip1'] = request.META.get('HTTP_X_FORWARDED_FOR', '')
    userinfo['ip2'] = request.META.get('REMOTE_ADDR', '')

    context = {
        'userinfo': userinfo,
    }

    return render(request, 'webtraffic/userinfo.html', context)

@login_required
def view_show(request, **kwargs):

    view = kwargs.get('view')

    message = ''
    i_error = False

    if request.method == 'POST':
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
    else:
        date_start='2019-01-01'
        date_end=datetime.date.today().strftime("%Y-%m-%d")

    if datetime.datetime.strptime(date_start, '%Y-%m-%d') > datetime.datetime.strptime(date_end,'%Y-%m-%d'):
            message = f'Please ensure that start date is before end date: {date_start}, {date_end}'
            i_error = True

    if not i_error:
        if view == 'traffic':
            model = ga4models.TrafficModel(date_start, date_end)
        elif view == 'geo':
            model = ga4models.GeoModel(date_start, date_end)
        elif view == 'tech':
            model = ga4models.TechModel(date_start, date_end)
        elif view == 'site':
            model = ga4models.SiteModel(date_start, date_end)
        else:
            model = ''
            message = 'Unrecognised view request'
            i_error = True


    if not i_error:
        context = model.get_context()
    else:
        context = {}

    context['message'] = message

    return render(request, 'webtraffic/view_show.html', context)

@login_required
def panda_show(request, **kwargs):

    view = kwargs.get('view')

    message = ''
    i_error = False

    if request.method == 'POST':
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
    else:
        date_start='2019-01-01'
        date_end=datetime.date.today().strftime("%Y-%m-%d")

    if datetime.datetime.strptime(date_start, '%Y-%m-%d') > datetime.datetime.strptime(date_end,'%Y-%m-%d'):
            message = f'Please ensure that start date is before end date: {date_start}, {date_end}'
            i_error = True

    if not i_error:
        if view == 'geo':
            model = panda.GeoPanda(date_start, date_end)
        elif view == 'traffic':
            pass
        elif view == 'tech':
            pass
        elif view == 'site':
            pass
        else:
            model = ''
            message = 'Unrecognised view request'
            i_error = True


    if not i_error:
        context = {}
    else:
        context = {}

    context['message'] = 'HELLO'

    return render(request, 'webtraffic/panda_show.html', context)
