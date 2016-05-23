# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.views.decorators.csrf import csrf_exempt

from user_server.forms import *
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.template import RequestContext
from django.core import serializers
from gridfs.errors import NoFile
from mimetypes import guess_type
from django.utils.http import urlquote_plus

from utils import *
from bson.objectid import ObjectId
import pymongo

# Create your views here.


def index(request):
    return render(request, 'index.html')


def profile(request, username):
    try:
        u = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'profile.html', {'selected_user': u})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/accounts/profile/' + form.cleaned_data['username'])
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response('registration/register.html', variables, )


def experiments_index(request):
    experiments = Experiment.objects.only('author', 'status', 'title').order_by('-date_created')
    return render(request, 'experiments/list.html', {'experiments': experiments})


def user_experiments(request, username):
    try:
        User.objects.get(username__iexact=username)
        experiments = Experiment.objects.only('author', 'status', 'title').filter(author__iexact=username).order_by(
            '-date_created')
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'experiments/list_by_user.html', {'username': username, 'experiments': experiments})


def get_user_unfinished_experiments(request, username):
    try:
        User.objects.get(username__iexact=username)
        experiments = Experiment.objects.only('author', 'status', 'title').filter(author__iexact=username,
                                                                                  status__lt=100,
                                                                                  status__gt=-0.5).order_by(
            '-date_created')
    except User.DoesNotExist:
        raise Http404("User does not exist")
    data = serializers.serialize('json', experiments)
    return HttpResponse(data, mimetype='application/json')


@login_required
def create_experiment(request):
    if request.method == 'POST':
        form = ExperimentForm(request.POST, request.FILES)
        if form.is_valid():
            ref_g, created1 = RefGenome.objects.get_or_create(file_address__iexact=form.cleaned_data['reference_genome'])
            if created1:
                ref_g.file_address = form.cleaned_data['reference_genome']
                ref_g.save()
            gtf_f, created2 = GTFFile.objects.get_or_create(file_address__iexact=form.cleaned_data['gtf_file'])
            if created2:
                gtf_f.file_address = form.cleaned_data['gtf_file']
                gtf_f.save()
            if not (ref_g and gtf_f):
                return render(request, 'experiments/create.html', {'form': form})
            exp = Experiment.objects.create(
                author=request.user.get_username(),
                title=form.cleaned_data['title'],
                species=form.cleaned_data['species'],
                description=form.cleaned_data['description'],
                conf_file=form.cleaned_data['conf_file'],
                libraries_file=form.cleaned_data['libraries_file'],
                reference_genome=ref_g,
                gtf_file=gtf_f
            )
            start_experiment(exp)
            return HttpResponseRedirect('/experiments/' + exp.title)
    else:
        form = ExperimentForm()
    return render(request, 'experiments/create.html', {'form': form})


def view_experiment(request, exp_title):
    try:
        e = Experiment.objects.get(title__iexact=exp_title)
        e.conf_file_url = urlquote_plus(str(e.conf_file)[1:])
        e.libraries_file_url = urlquote_plus(str(e.libraries_file)[1:])
        e.out_log_url = urlquote_plus(str(e.out_log)[1:])
        e.err_log_url = urlquote_plus(str(e.err_log)[1:])
        e.results_url = urlquote_plus(str(e.results_archive)[1:])
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return render(request, 'experiments/view.html', {'experiment': e})


@login_required
def create_reference_genome(request):
    if request.method == 'POST':
        ss = ''
        form = ReferenceGenomeForm(request.POST)
        if form.is_valid():
            s, created = Species.objects.get_or_create(name__iexact=form.cleaned_data['species'].lower())
            if created:
                s.name = form.cleaned_data['species'].lower()
                s.save()
            version_no = get_next_version_number(s)
            rg = ReferenceGenome.objects.create(
                species=s,
                version=version_no,
                file_name=s.name+"."+str(version_no)+".gtf.gz"
            )
            return HttpResponseRedirect('/reference-genomes/' + s.name)
    else:
        ss = Species.objects.all()
        form = ReferenceGenomeForm()
    return render(request, 'ReferenceGenomes/create.html', {'form': form, 'species': ss})


def view_reference_genome(request, species):
    try:
        s = Species.objects.get(name__iexact=species)
        rgs = ReferenceGenome.objects.only('version', 'date_created').filter(species__exact=s).order_by('-version')
    except Species.DoesNotExist:
        raise Http404("No reference genomes exist for that species")
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return render(request, 'ReferenceGenomes/view.html', {'reference_genomes': rgs, 'species': s})


def list_reference_genome(request):
    try:
        ss = Species.objects.all()
        ss = [append_latest_version_to_species(s) for s in ss]
    except Experiment.DoesNotExist:
        raise Http404("No reference genomes exist")
    return render(request, 'ReferenceGenomes/list.html', {'species': ss})


def append_latest_version_to_species(species):
    rg = ReferenceGenome.objects.only('version', 'date_created').filter(species__exact=species).order_by('-version').last()
    s = species
    s['latest_version'] = str(rg.version)
    s['modified_on'] = rg.date_created
    return s


def page_not_found_view(request):
    return render(request, '404.html')


def not_yet_done(request):
    return render(request, 'todo.html', )


@login_required
def redirect_to_user_profile(request):
    return HttpResponseRedirect('/accounts/profile/' + request.user.get_username())


from django.conf import settings


@csrf_exempt
def serve_to_gridfs(request):
    if request.method == 'POST':
        form = UploadFileToFrontServerForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if form.cleaned_data['model'] == 'gtffile':
                    obj = GTFFile.objects.get(file_address__iexact=form.cleaned_data['address'])
                    obj.file_content = form.cleaned_data['file']
                    obj.save()
                elif form.cleaned_data['model'] == 'referencegenome':
                    obj = RefGenome.objects.get(file_address__iexact=form.cleaned_data['address'])
                    obj.file_content = form.cleaned_data['file']
                    obj.save()
                elif form.cleaned_data['model'] == 'experiment':
                    obj = Experiment.objects.get(title__iexact=form.cleaned_data['name'])
                    if form.cleaned_data['field'] == 'err_log':
                        obj.err_log = form.cleaned_data['file']
                    elif form.cleaned_data['field'] == 'out_log':
                        obj.out_log = form.cleaned_data['file']
                    elif form.cleaned_data['field'] == 'results_archive':
                        obj.results_archive = form.cleaned_data['file']
                    obj.save()
                else:
                    raise Http404("Model not found: " + form.cleaned_data['id'])
            except:
                raise Http404("Model not found: " + form.cleaned_data['id'])
            return HttpResponse('File Uploaded')
        return HttpResponse(content="Invalid Request", status=400)
    return HttpResponse(content="Only POST requests are supported", status=400)

# note: files should NEVER be served this way in production. This was done during development for rapid testing
# TODO: PLEASE use nginx-gridfs to serve large files before moving this to production
if settings.DEBUG:
    def serve_from_gridfs(request, path):
        # Serving GridFS files through Django is inefficient and
        # insecure. NEVER USE IN PRODUCTION!
        try:
            grid_file = gridfs_storage.open(path)
        except NoFile:
            raise Http404
        else:
            return HttpResponse(grid_file, mimetype=guess_type(path)[0])

