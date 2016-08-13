from django import template


register = template.Library()


def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.inclusion_tag('pagination.html', takes_context=True)
def pagination(context, objects, page_variable, hash_tag=''):
    request = context['request']
    context = {}
    if objects.has_previous():
        previous_page_url = url_replace(request, page_variable,
                                        objects.previous_page_number())
        context.update({'previous_page_url': previous_page_url})
    if objects.has_next():
        next_page_url = url_replace(request, page_variable,
                                    objects.next_page_number())
        context.update({'next_page_url': next_page_url})
    if hash_tag:
        hash_tag = '#'+hash_tag

    context.update({'objects': objects, 'page_variable': page_variable,
            'hash_tag': hash_tag,
                    })
    return context
