from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.urls import reverse

### administration
@login_required
def administration(request):

    context = {
        'pagetitle' : 'SJ - Administration'
    }
    template = loader.get_template('administration_show.html')

    return HttpResponse(template.render(context, request))