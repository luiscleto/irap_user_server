from django.conf.urls import include, url
from django.contrib import admin
from user_server import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'irap_user_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('user_server.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mongonaut/', include('mongonaut.urls'))
]
