from django.conf.urls import include, url, patterns
from user_server import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Examples:
    # url(r'^$', 'irap_user_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='home'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', views.profile, name='profile'),

]
