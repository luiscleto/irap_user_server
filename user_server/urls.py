from django.conf.urls import include, url, patterns
from user_server import views
from django.views.generic import RedirectView


handler404 = 'user_server.views.page_not_found_view'

urlpatterns = [
    # Examples:
    # url(r'^$', 'irap_user_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', RedirectView.as_view(pattern_name='home')),
    url(r'^home/$', views.index, name='home'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url('^', include('django.contrib.auth.urls')),

    url(r'^accounts/profile/(?P<username>\w+)$', views.profile, name='profile'),
    url(r'^accounts/profile/$', views.redirect_to_user_profile),
    url(r'^accounts/login/$',  RedirectView.as_view(pattern_name='login')),
    url(r'^register/$',  views.register, name='register'),

    url(r'^experiments/list/$', views.experiments_index, name='experiments'),
    url(r'^experiments/create/$', views.create_experiment, name='new_experiment'),
    url(r'^experiments/(?P<exp_title>\w+)/$', views.view_experiment, name='experiment'),
    url(r'^(?P<username>\w+)/experiments/$', views.user_experiments, name='user_experiments'),

    url(r'^reference-genomes/list/$', views.list_reference_genome, name='reference_genomes'),
    url(r'^reference-genomes/create/$', views.create_reference_genome, name='new_reference_genome'),
    url(r'^reference-genomes/(?P<species>[\w\ ]+)/$', views.view_reference_genome, name='reference_genome'),

    url(r'^notdone/$', views.not_yet_done, name='notdone'),

    url(r'^getgridfile/(?P<path>.*)$', views.serve_from_gridfs, name='get_file'),
    url(r'^storegridfile/$', views.serve_to_gridfs, name='put_file')
]
