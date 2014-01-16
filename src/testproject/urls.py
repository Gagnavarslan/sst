from django.conf.urls import include, patterns
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
                       # Example:
                       # (r'^testproject/', include('testproject.foo.urls')),
                       (r'^static-files/(?P<path>.*)$',
                        'django.views.static.serve',
                        {'document_root': settings.STATIC_DOC_ROOT}),
                       (r'simple', include('testproject.simple.urls')),
                       (r'begin', 'simple.views.begin'),
                       (r'longscroll', 'simple.views.longscroll'),
                       (r'html5', 'simple.views.html5'),
                       (r'popup', 'simple.views.popup'),
                       (r'frame_a', 'simple.views.frame_a'),
                       (r'frame_b', 'simple.views.frame_b'),
                       (r'alerts', 'simple.views.alerts'),
                       (r'yui', 'simple.views.yui'),
                       (r'tables', 'simple.views.tables'),
                       (r'page_to_save', 'simple.views.page_to_save'),
                       (r'kill_django', 'simple.views.kill_django'),
                       (r'', 'simple.views.index'),)

urlpatterns += staticfiles_urlpatterns()
