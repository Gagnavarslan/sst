from django.conf.urls import include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views import static

from .simple import views

admin.autodiscover()


urlpatterns = [
    # Example:
    # url(r'^testproject/', include('testproject.foo.urls')),
    url(
        r'^static-files/(?P<path>.*)$',
        static.serve,
        {'document_root': settings.STATIC_DOC_ROOT}
    ),
    url(r'simple', include('testproject.simple.urls')),
    url(r'begin', views.begin),
    url(r'longscroll', views.longscroll),
    url(r'html5', views.html5),
    url(r'popup', views.popup),
    url(r'frame_a', views.frame_a),
    url(r'frame_b', views.frame_b),
    url(r'alerts', views.alerts),
    url(r'yui', views.yui),
    url(r'tables', views.tables),
    url(r'page_to_save', views.page_to_save),
    url(r'kill_django', views.kill_django),
    url(r'', views.index),
]

urlpatterns += staticfiles_urlpatterns()
