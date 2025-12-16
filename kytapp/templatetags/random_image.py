# kytapp/templatetags/random_image.py
import os
import random
from django import template
from django.templatetags.static import static
from django.conf import settings

register = template.Library()

@register.simple_tag
def random_image(category):
    path = os.path.join(settings.BASE_DIR, 'kytapp', 'static', 'kytapp', category)
    try:
        images = [f for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.jpeg'))]
        if images:
            return static(f'kytapp/{category}/{random.choice(images)}')
    except FileNotFoundError:
        pass
    return ''
