from django.conf import settings
from django.utils import translation

def language_context(request):
    """
    Add language information to the template context.
    This makes language information available in all templates.
    """
    current_language = translation.get_language()
    return {
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE_CODE': current_language,
        'LANGUAGE_BIDI': translation.get_language_info(current_language).get('bidi', False),
    } 