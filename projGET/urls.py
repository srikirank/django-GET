from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'projectGET.views.home', name='home'),
    # url(r'^projectGET/', include('projectGET.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'projGET.views.login', name = 'default'),
    url(r'^login/$', 'projGET.views.login', name = 'login'),
    url(r'^invalid_login/$','projGET.views.invalid', name = 'invalid'),
    url(r'^logout/$','projGET.views.loggedout', name = 'loggedout'),
    url(r'^register/$','projGET.views.register', name = 'register'),
    url(r'^register_success/$','projGET.views.register_success', name = 'register_success'),

    url(r'^get/', include('GET.urls', namespace = 'get')),
    url(r'^admin/', include(admin.site.urls)),
) +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)