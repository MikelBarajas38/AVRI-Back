"""
Export statistics to CSV files.
"""
import csv
from django.http import HttpRequest, HttpResponse
from core.statistics import (get_user_field_of_study_stats,
                             get_most_consulted_documents_stats,
                             get_most_consulted_authors_stats,
                             get_document_keywords_stats,
                             get_user_education_level_stats,
                             get_user_activity_status_stats,
                             get_chats_over_time_stats,
                             )


def export_user_field_of_study_csv(request: HttpRequest) -> HttpResponse:
    """
    Export user field of study statistics to a CSV file.
    """
    data = get_user_field_of_study_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=user_\
        field_of_study_stats.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Field', 'Count'])

    labels = data['labels']
    values = data['values']

    for label, value in zip(labels, values):
        writer.writerow(['user_field_of_study', label, value])

    return response


def export_user_education_level_csv(request: HttpRequest) -> HttpResponse:
    """
    Export user education level statistics to a CSV file.
    """
    data = get_user_education_level_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=user_\
        education_level_stats.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Field', 'Count'])

    labels = data['labels']
    values = data['values']

    for label, value in zip(labels, values):
        writer.writerow(['user_education_level', label, value])

    return response


def export_user_activity_status_csv(request: HttpRequest) -> HttpResponse:
    """
    Export user activity status statistics to a CSV file.
    """
    data = get_user_activity_status_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\
        user_activity_status_stats.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Field', 'Count'])

    labels = data['labels']
    values = data['values']

    for label, value in zip(labels, values):
        writer.writerow(['user_activity_status', label, value])

    return response


def export_most_consulted_documents_csv(request: HttpRequest) -> HttpResponse:
    """
    Export most consulted documents statistics to a CSV file.
    """
    data = get_most_consulted_documents_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=most_\
        consulted_documents.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Title', 'Count'])

    for label, value in zip(data['labels'], data['values']):
        writer.writerow(['most_consulted_documents', label, value])

    return response


def export_most_consulted_authors_csv(request: HttpRequest) -> HttpResponse:
    """
    Export most consulted authors statistics to a CSV file.
    """
    data = get_most_consulted_authors_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=most_\
        consulted_authors.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Author', 'Count'])

    for label, value in zip(data['labels'], data['values']):
        writer.writerow(['most_consulted_authors', label, value])

    return response


def export_document_keywords_csv(request: HttpRequest) -> HttpResponse:
    """
    Export document keyword statistics to a CSV file.
    """
    data = get_document_keywords_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=document\
        _keywords.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Keyword', 'Count'])

    for label, value in zip(data['labels'], data['values']):
        writer.writerow(['document_keywords', label, value])

    return response


def export_chats_over_time_csv(request: HttpRequest) -> HttpResponse:
    """
    Export chat session statistics over time to a CSV file.
    """
    data = get_chats_over_time_stats()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=chats_\
        over_time.csv'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Date', 'Count'])

    for label, value in zip(data['labels'], data['values']):
        writer.writerow(['chats_over_time', label, value])

    return response
