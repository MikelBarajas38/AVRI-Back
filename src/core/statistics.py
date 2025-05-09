"""
Generate statistics for the application.
"""
from django.db.models.functions import TruncDate
from django.db.models import Count
from core import models
from collections import Counter
import re
from typing import List, Dict, Union


def get_user_field_of_study_stats() -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on user fields of study with counts per field.
    """
    queryset = models.User.objects.values('field_of_study__name')\
        .annotate(count=Count('id')).order_by('-count')

    labels = [item['field_of_study__name'] or 'No field' for item in queryset]
    values = [item['count'] for item in queryset]

    return {
        "labels": labels,
        "values": values
    }


def get_most_consulted_documents_stats(
        limit: int = 10) -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on the most consulted documents,
    limited by the given number.
    """
    queryset = models.SavedDocument.objects.values('document__title')\
        .annotate(count=Count('id'))\
        .order_by('-count')[:limit]

    labels = [item['document__title'] or 'No title' for item in queryset]
    values = [item['count'] for item in queryset]
    return {
        "labels": labels,
        "values": values
    }


def get_most_consulted_authors_stats(
        limit: int = 10) -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on the most consulted authors, based on saved documents.
    """
    queryset = models.AuthoredDocument.objects\
        .filter(document__saveddocument__isnull=False)\
        .values('author__name') \
        .annotate(count=Count('document__saveddocument'))\
        .order_by('-count')[:limit]

    labels = [item['author__name'] or 'No name' for item in queryset]
    values = [item['count'] for item in queryset]

    return {
        "labels": labels,
        "values": values
    }


def get_document_keywords_stats(
        limit: int = 10) -> Dict[str, List[Union[str, int]]]:
    """
    Return keyword frequency statistics extracted from document titles.
    """
    documents = models.Document.objects.values_list('title', flat=True)
    text = ' '.join(documents).lower()
    words = re.findall(r'\b\w+\b', text)

    stop_words = {"the", "and", "of", "in", "a", "to", "for", "on",
                  "with", "by", "an", "at", "as", "from", "is", "that",
                  "this", "it", "or", "are", "was", "be", "not", "but",
                  "all", "any", "some", "such", "which", "who", "whom",
                  "el", "la", "los", "las", "de", "que", "en", "del",
                  "y", "un", "una", "se", "al", "por", "no", "es",
                  "su", "como", "más", "este", "esta", "este", "estos",
                  "estas", "todo", "toda", "todos", "todas", "este",
                  "esta", "estos", "estas", "ese", "esa", "esos",
                  "esas", "aquel", "aquella", "aquellos", "aquellas", }

    filtered_words = [
        word for word in words if word not in stop_words and len(word) > 2]
    most_common = Counter(filtered_words).most_common(limit)

    labels = [word for word, _ in most_common]
    values = [count for _, count in most_common]

    return {
        "labels": labels,
        "values": values
    }


def get_user_education_level_stats() -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on users' education levels.
    """
    queryset = models.User.objects.values('education_level')\
        .annotate(count=Count('id')).\
        order_by('-count')

    labels = [models.User.EDUCATION_LEVELS.get(
        item['education_level'], 'Unknown') for item in queryset]
    values = [item['count'] for item in queryset]
    return {"labels": labels, "values": values}


def get_user_activity_status_stats() -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on user activity status (active vs inactive).
    """
    queryset = models.User.objects.values(
        'is_active').annotate(count=Count('id'))
    labels = ['Active' if item['is_active']
              else 'Inactive' for item in queryset]
    values = [item['count'] for item in queryset]
    return {"labels": labels, "values": values}


def get_user_interaction_levels() -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics of users based on number of saved documents.
    """
    queryset = models.SavedDocument.objects.values('user__email').annotate(
        saved_count=Count('id')).order_by('-saved_count')[:10]
    labels = [item['user__email'] or 'No email' for item in queryset]
    values = [item['saved_count'] for item in queryset]
    return {"labels": labels, "values": values}


def get_document_status_distribution() -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on the distribution of document statuses.
    """
    queryset = models.Document.objects.values(
        'status').annotate(count=Count('id'))
    labels = [models.Document.DOCUMENT_STATUS.get(
        item['status'], 'Unknown') for item in queryset]
    values = [item['count'] for item in queryset]
    return {"labels": labels, "values": values}


def get_chats_over_time_stats() -> Dict[str, List[Union[str, int]]]:
    """
    Return statistics on number of chat sessions per day over time.
    """
    queryset = models.ChatSession.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('session_id')).order_by('date')

    labels = [item['date'].strftime("%Y-%m-%d") for item in queryset]
    values = [item['count'] for item in queryset]

    return {"labels": labels, "values": values}
