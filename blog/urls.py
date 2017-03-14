from django.contrib.sitemaps.views import sitemap
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url, include
from .views import (ArticleListView, UserInfoView, ArticlePostView, ArticleDetailView,
                    ArticleEditView, RegisterView, TagFilterView, CategoryFilterView, BlogSitemap,
                    download_image, ArchivesView, about_view, read_books, delete_article, change_avatar)

urlpatterns = [
    url(r'^$', ArticleListView.as_view(), name='blog_index'),
    url(r'^user/(?P<user_id>\d+)$', UserInfoView.as_view(), name='user_information'),
    url(r'^user/register/$', RegisterView.as_view(), name='register'),
    url(r'^post/article/$', ArticlePostView.as_view(), name='article_post'),
    url(r'^edit/article/(?P<author>\S+)/(?P<article_link>\S+)\.html$', ArticleEditView.as_view(), name='article_edit'),
    url(r'^article/(?P<author>\S+)/(?P<article_link>\S+)\.html$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^archives/$', ArchivesView.as_view(), name='article_archives'),
    url(r'^tag/(?P<tag_name>\S+)$', TagFilterView.as_view(), kwargs={'tag_or_tags': 'tag'}, name='tag_filter'),
    url(r'^tags/$', TagFilterView.as_view(), kwargs={'tag_or_tags': 'tags'}, name='tags'),
    url(r'^category/(?P<category_name>\S+)$', CategoryFilterView.as_view(), kwargs={'category_all': False}, name='category_filter'),
    url(r'^categories/$', CategoryFilterView.as_view(), kwargs={'category_all': True}, name='categories'),
    url(r'^search/', include('haystack.urls')),
    url(r'^about\.html$', about_view, name='about_blog'),
    url(r'read-books\.html$', read_books, name='read_books'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'blog': BlogSitemap}}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'download-image/download.jpg$', download_image, name='download_image'),
    url(r'chagng-avatar/user/(?P<user_id>\d+)$', change_avatar, name='change_avatar'),
    url(r'delete/article/(?P<article_id>\d+)$', delete_article, name='delete_article'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
