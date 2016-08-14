from django.conf.urls import url

from . import views

# router.register(r'essay/(?P<pk>[0-9]+)', views.EssayDetail)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
# url(r'^essay/(?P<pk>[0-9]+)/$', views.EssayDetail),

urlpatterns = [
    url(r'^register', views.register, name='register'),
    url(r'^search', views.search, name='search'),
    url(r'^update_submitted_essay_score',
        views.essay_original_submit, name='update_submitted_essay_score'),
    url(r'^$', views.index, name='index'),
    # url(r'^api/', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^(?P<essayModel_id>[0-9]+)/$', views.view, name='detail'),
]
