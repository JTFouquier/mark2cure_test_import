from mark2cure.common.bioc import *
from mark2cure.document.models import Document, Annotation


def apply_bioc_documents(documents, bioc_collection, user=None):
    for doc in documents:
        d = doc.as_bioc_obj()

        passage_offset = 0
        for section in doc.available_sections():
            passage = section.as_bioc(passage_offset)
            passage_offset += len(section.text)

            apply_bioc_annotations(section, passage, passage_offset, user)
            d.add_passage(passage)

        bioc_collection.add_document(d)

def apply_bioc_annotations(section, bioc_passage, passage_offset, user=None):
    if user:
        query_set = Annotation.objects.filter(view__section=section, view__user=user)
    else:
        query_set = Annotation.objects.filter(view__section=section)

    for ann in query_set.all():
        annotation = BioCAnnotation()
        annotation.id = str(ann.pk)
        annotation.put_infon('type', str(ann.type))
        annotation.put_infon('user', str(ann.view.user.pk))

        location = BioCLocation()
        location.offset = str(passage_offset+ann.start)
        location.length = str(len(ann.text))
        annotation.add_location(location)

        annotation.text = ann.text

        bioc_passage.add_annotation(annotation)