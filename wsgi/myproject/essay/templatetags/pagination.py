from django import template


register = template.Library()


@register.inclusion_tag('pagination.html')
def pagination(objects, page_variable, hash_tag=''):
    if hash_tag:
        hash_tag = '#'+hash_tag
    return {'objects': objects, 'page_variable': page_variable,
            'hash_tag': hash_tag}
