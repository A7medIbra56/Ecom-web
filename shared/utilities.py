from django.db import models
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

def search_model(queryset, search_query, search_fields=None):
    """
    Perform a search across specified fields or all valid fields of a given queryset
    and return a filtered queryset sorted by relevance.

    Args:
        queryset (QuerySet): The Django queryset to search.
        search_query (str): The search query string.
        search_fields (list or None): A list of fields to search. If None, all valid fields are used.

    Returns:
        QuerySet: A queryset filtered and sorted by relevance.
    """
    if not search_query:
        # If no search query is provided, return the original queryset
        return queryset

    # Get the model from the queryset
    model = queryset.model

    # If search_fields is provided, use it; otherwise, dynamically retrieve fields
    if search_fields is None:
        # Get all valid field names of the model (exclude related fields like OneToOneField)
        fields = [
            field.name for field in model._meta.get_fields()
            if hasattr(field, 'attname') and not field.is_relation
        ]
    else:
        # Use the provided search_fields
        fields = search_fields

    # Check if the model has a "user" field and if it's a OneToOneField to the user model
    try:
        user_field = model._meta.get_field("user")
        if isinstance(user_field, models.OneToOneField) and user_field.related_model == get_user_model():
            # Add user model fields (e.g., username, email) to the search fields
            user_model = get_user_model()
            user_fields = [
                f"user__{field.name}" for field in user_model._meta.get_fields()
                if hasattr(field, 'attname') and not field.is_relation
            ]
            fields.extend(user_fields)
    except Exception:
        # If the "user" field does not exist or any error occurs, continue without adding user fields
        pass

    # Build a Q object to search across all valid fields
    query = Q()
    for field in fields:
        query |= Q(**{f"{field}__icontains": search_query})

    # Annotate the queryset with a relevance score
    filtered_queryset = (
        queryset.filter(query)
        .annotate(relevance=Count('id'))  # Use Count as a placeholder for relevance
        .order_by('-relevance')  # Sort by relevance in descending order
    )

    return filtered_queryset