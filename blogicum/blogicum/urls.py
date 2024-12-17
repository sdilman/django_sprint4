from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import path, include, reverse_lazy
from django.views.generic.edit import CreateView


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('auth/', include('django.contrib.auth.urls'))
]

if settings.DEBUG:
    urlpatterns = (
        urlpatterns
        + [path('__debug__/', include('debug_toolbar.urls')), ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
