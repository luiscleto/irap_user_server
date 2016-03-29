from django.conf.urls import include, url, patterns
from user_server import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Examples:
    # url(r'^$', 'irap_user_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='home'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'password_reset.html'}, name='password_reset'),
    url(r'^accounts/profile/$', views.profile, name='profile'),

]
