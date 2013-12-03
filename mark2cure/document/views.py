'''
doc views (controllers)
'''

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q

from mark2cure.document.models import Document, Annotation, View
from mark2cure.document.forms import DocumentForm
from mark2cure.common.utils import get_timezone_offset

from copy import copy

import oauth2 as oauth
import json


@login_required
def list(request, page_num=1):
    doc_list = Document.objects.all()
    paginator = Paginator(doc_list, 25)

    try:
        docs = paginator.page(page_num)
    except PageNotAnInteger:
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)

    return render_to_response('document/list.jade',
                              {"docs": docs},
                              context_instance=RequestContext(request))


@login_required
def read(request, doc_id):

    doc = get_object_or_404(Document, pk=doc_id)

    return render_to_response('document/read.jade',
                              {"doc": doc},
                              context_instance=RequestContext(request))

@login_required
def delete(request, doc_id):
    ###############
    # (TODO) MUST BE ADMIN
    ###############

    # doc = get_object_or_404(Document, pk=doc_id)
    # doc.delete()
    return redirect('/document/')

@login_required
@require_http_methods(["POST"])
def create(request):
    form = DocumentForm(request.POST)
    if form.is_valid():
      doc_id = request.POST['document_id']

      Document.objects.create_from_pubmed_id( doc_id )

      return redirect('/document/'+ doc_id)
