from django.conf.urls import include, url, patterns
from user_server import views
from django.views.generic import RedirectView


urlpatterns = [
    # Examples:
    # url(r'^$', 'irap_user_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='home'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^accounts/login/$',  RedirectView.as_view(pattern_name='login')),
    url(r'^register/$',  views.register, name='register'),
    url(r'^experiments/$', views.experiments_index, name='experiments')

]
