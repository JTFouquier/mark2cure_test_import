from django.contrib.auth.models import User
from django.db import models

from ..document.models import Document
from ..task.models import DocumentQuestRelationship, Task

from brabeion.base import Badge, BadgeAwarded
from brabeion import badges
from decimal import Decimal

import random


class SkillBadge(Badge):
    slug = "skill"
    levels = [
        "Basic",
        "Disease Marking",  # T1 complete
        "Disease Advanced",  # T2 complete
        "Disease Matching",  # T3 complete
        "Intermediate",  # 1st GM Quest Complete
        "Proficient",
        "Advanced",
        "Expert",
    ]
    events = [
        "skill_awarded",
    ]
    multiple = False

    def award(self, **state):
        user = state["user"]
        level = state.pop("level", None)
        current_highest = user.profile.highest_level(self.slug).level

        if (level and level == current_highest + 1) or state.get('force', None):
            return BadgeAwarded(level=level + 1)

badges.register(SkillBadge)


class PointsBadge(Badge):
    slug = "points"
    levels = [
        "Novice Magic Marker",
        "Magic Marker",
        "Expert Magic Marker",
        "Novice Marker Bee",
        "Marker Bee",
        "Expert Marker Bee",
        "Novice Marksman",
        "Marksman",
        "Expert Marksman",
        "Novice Mark up",
        "Mark up",
        "Expert Mark up"
        "Novice Benchmarker",
        "Benchmarker",
        "Expert Benchmarker",
        "Master Benchmarker",
        "Master Marker",
        "Bronze Master Marker",
        "Silver Master Marker",
        "Gold Master Marker",
    ]
    events = [
        "points_awarded",
    ]
    multiple = False

    def award(self, **state):
        user = state["user"]
        points = user.profile.score()
        if points > 500:
            return BadgeAwarded(level=2)
        if points > 50:
            return BadgeAwarded(level=1)


badges.register(PointsBadge)


class Group(models.Model):
    '''Describe a non-task specific selection of documents (1-n) that curator defined'''

    name = models.CharField(max_length=200)
    stub = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.DecimalField(default=0, max_digits=3, decimal_places=3)

    enabled = models.BooleanField(default=False)

    def get_documents(self):
        # (TODO?) Return for __in of task_ids
        return Document.objects.filter(task__group=self)

    def total_documents(self):
        # (TODO) rename of return time is reflected
        return DocumentQuestRelationship.objects.filter(task__group=self)

    def current_avg_f(self, weighted=True):
        report_qs = self.report_set.filter(report_type=1).order_by('-created')

        if report_qs.exists():
            report = report_qs.first()
            df = report.dataframe

            if weighted:
                df['wf'] = df['pairings'] * df['f-score']
                return df['wf'].sum() / df['pairings'].sum()
            else:
                return df['f-score'].mean()

        else:
            return 0.0

    def percentage_complete(self):
        task_queryset = self.task_set.extra(select={
            "completed": """
                SELECT COUNT(*) AS completed
                FROM task_userquestrelationship
                WHERE (task_userquestrelationship.completed = 1
                    AND task_userquestrelationship.task_id = task_task.id)"""
        })
        completed = sum([x for x in task_queryset.values_list('completed', flat=True) if x is not None])
        required = sum([x for x in task_queryset.values_list('completions', flat=True) if x is not None])
        if required:
            return (Decimal(completed) / Decimal(required)) * 100
        else:
            return 0

    def pubtator_coverage(self):
        queryset = self.get_documents().prefetch_related('pubtator_set')
        completed = sum([3 for x in queryset if x.pubtator_set.filter(validate_cache=True).count() == 3])
        if completed:
            return (Decimal(completed) / Decimal(queryset.count() * 3)) * 100
        else:
            return 0

    def assign(self, documents, smallest_bin=5, largest_bin=5, completions=15):
        # Insert the other Documents
        document_set = list(documents.values_list('id', flat=True))
        random.shuffle(document_set)
        last_task = None
        name_counter = 1

        while len(document_set) >= 1:

            quest_size = int(random.uniform(smallest_bin, largest_bin))
            # If there was an existing Task with less than the
            # desired number of documents
            if last_task and last_task.documents.count() < quest_size:

                # Shuffle & Remove the document_pk for use and from being selected again
                random.shuffle(document_set)
                doc_pk = document_set[0]
                document_set.remove(doc_pk)

                document = Document.objects.get(pk=doc_pk)
                DocumentQuestRelationship.objects.create(task=last_task, document=document)

            else:
                last_task, task_created = Task.objects.get_or_create(
                    name=str(name_counter),
                    completions=completions,
                    requires_qualification=7,
                    provides_qualification=7,
                    points=5000,
                    group=self)
                name_counter += 1

    def __unicode__(self):
        return self.name


class SupportMessage(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    text = models.TextField()
    referral = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'{text} (via {user})'.format(text=self.text, user=self.user)

