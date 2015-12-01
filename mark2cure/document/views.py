from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from ..common.bioc import BioCReader, BioCWriter
from ..common.formatter import bioc_writer, bioc_as_json
from .models import Document, Pubtator


def read_bioc(request, pubmed_id, format_type):
    """A plain (no annotations) BioC file for a PMID"""
    writer = bioc_writer(request)
    doc = get_object_or_404(Document, document_id=pubmed_id)

    writer = bioc_writer(request)
    bioc_document = doc.as_bioc_with_passages()
    writer.collection.add_document(bioc_document)

    if format_type == 'json':
        writer_json = bioc_as_json(writer)
        return HttpResponse(writer_json, content_type='application/json')
    else:
        return HttpResponse(writer, content_type='text/xml')


def read_pubtator(request, pk):
    """Return the exact Pubtator file that was downloaded"""
    pubtator = get_object_or_404(Pubtator, pk=pk)
    return HttpResponse(pubtator.content, content_type='text/xml')


def read_specific_pubtator_bioc(request, pub_pk, format_type):
    # When fetching via pubmed, include no annotaitons
    pubtator = get_object_or_404(Pubtator, pk=pub_pk)

    r = BioCReader(source=pubtator.content)
    r.read()

    writer = BioCWriter()
    writer.collection = r.collection

    # writer = bioc_writer(request)
    # bioc_document = doc.as_bioc_with_pubtator_annotations()
    #writer.collection.add_document(bioc_document)
    #return HttpResponse(200);

    if format_type == 'json':
        writer_json = bioc_as_json(writer)
        return HttpResponse(writer_json, content_type='application/json')
    else:
        return HttpResponse(writer, content_type='text/xml')


def read_pubtator_bioc(request, pubmed_id, format_type):
    """A merged file of the multiple Pubtator responses"""
    # When fetching via pubmed, include no annotaitons
    doc = get_object_or_404(Document, document_id=pubmed_id)

    writer = bioc_writer(request)
    bioc_document = doc.as_bioc_with_pubtator_annotations()
    writer.collection.add_document(bioc_document)

    if format_type == 'json':
        writer_json = bioc_as_json(writer)
        return HttpResponse(writer_json, content_type='application/json')
    else:
        return HttpResponse(writer, content_type='text/xml')

