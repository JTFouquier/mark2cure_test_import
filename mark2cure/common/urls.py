from django.conf.urls import patterns, url

urlpatterns = patterns(
    'mark2cure.common.views',
    url(r'^$', r'signup_home'),
    url(r'^beta/$', r'home'),

    # Initial training for fresh signups
    url(r'^training/basics/$', r'introduction'),
    url(r'^training/intro/1/step/(?P<step_num>\w+)/$',
        r'training_one'),
    url(r'^training/intro/2/step/(?P<step_num>\w+)/$',
        r'training_two'),
    url(r'^training/intro/3/$', r'training_three'),

    url(r'^training/intro/$', r'training_read'),

    url(r'^dashboard/$', r'dashboard'),

    # Initial training for fresh signups
    url(r'^quest/(?P<quest_num>\w+)/$', r'quest_read'),
    # REST Framework
    url(r'^quest/api/read/$', r'quest_list'),
)
