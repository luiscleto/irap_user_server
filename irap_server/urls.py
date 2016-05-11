from django.conf.urls import include, url, patterns
from irap_server import views
from django.views.generic import RedirectView


handler404 = 'user_server.views.page_not_found_view'

urlpatterns = [
    # Examples:
    # url(r'^$', 'irap_user_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^run/(?P<exp_title>\w+)/$', views.run_experiment, name='run_experiment')
]
