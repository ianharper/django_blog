from django.conf.urls import url
from . import views

urlpatterns = [ 
	url(r'^(?P<page>\d+)?$', views.post_list, name = 'post_list'),
	url(r'^post/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
	url(r'^post/new/$', views.post_new, name='post_new'),
	url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
	url(r'^category/(?P<name>[\d\w]+)/(?P<page>\d+)?$', views.category_list, name='category_list'),
	url(r'^tag/(?P<name>[\d\w]+)/(?P<page>\d+)?$', views.tag_list, name='tag_list'),
]