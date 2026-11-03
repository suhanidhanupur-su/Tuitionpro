from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Usage: {{ my_dict|get_item:key }}
    Returns dictionary[key] or None if missing.
    Used in attendance templates to look up per-student, per-day status.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def get_range(value):
    """
    Usage: {% for day in days_in_month|get_range %}
    Returns range(1, value+1) so we can iterate over day numbers in a template.
    """
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)
