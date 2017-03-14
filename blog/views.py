#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.contrib.sitemaps import Sitemap
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404, redirect, render_to_response, render
from .models import Article, Author, Category, Tag
from .forms import ArticlePostForm, RegisterForm
from .lib.tag_cloud import TagCloud
import os


def get_object_list(self, object_list, per_page=10, orphans=0):
    paginator = Paginator(object_list, per_page=per_page, orphans=orphans)
    page = self.request.GET.get('page')
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
    return object_list


class ArticleListView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'article_list'

    def get_queryset(self, *args, **kwargs):
        article_list = Article.posted.all()
        return get_object_list(self, article_list)

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        paginator_page_range = list(self.object_list.paginator.page_range)
        max_display_page = 15
        half_display_page = max_display_page // 2
        if self.object_list.paginator.num_pages <= max_display_page:
            page_range = paginator_page_range
        else:
            index = paginator_page_range.index(self.object_list.number) + 1  # 转换成页码计数，从1开始，更符合逻辑
            max_index = len(self.object_list.paginator.page_range)
            if index <= half_display_page + 1:
                start_index = 0
                end_index = max_display_page - 1
                page_range = paginator_page_range[start_index:end_index] + [self.object_list.paginator.num_pages]
            elif index >= (max_index - half_display_page):
                start_index = index - (max_display_page - (max_index - index)) + 1
                end_index = max_index
                page_range = [1] + paginator_page_range[start_index:end_index]
            else:
                start_index = index - (half_display_page - 1) - 1
                end_index = index + half_display_page - 1
                page_range = [1, ] + paginator_page_range[start_index:end_index] + [
                    self.object_list.paginator.num_pages]
        context['page_range'] = page_range
        return context


class ArticleDetailView(DetailView):
    template_name = 'blog/article_detail.html'
    current_article_id = None
    context_object_name = 'article'

    def get_object(self, *args, **kwargs):
        article_link = self.kwargs.get('article_link')
        author = self.kwargs.get('author')
        try:
            article = Article.posted.get(article_link=article_link, author=author)
            self.current_article_id = article.id
            article.views += 1
            article.save()
        except Article.DoesNotExist:
            raise Http404("Article does not exist!")
        return article

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        current_article_index = -9999
        if self.current_article_id:
            previous_article = None
            next_article = None
            post_articles = Article.objects.filter(status='p')
            for index, article in enumerate(post_articles):
                if self.current_article_id == article.id:
                    current_article_index = index
                    break
            try:
                previous_article = post_articles[current_article_index - 1]
            except (IndexError, AssertionError):
                pass
            try:
                next_article = post_articles[current_article_index + 1]
            except (IndexError, AssertionError):
                pass
            context['previous_article'] = previous_article
            context['next_article'] = next_article
        return context


class ArticlePostView(FormView):
    template_name = 'blog/article_post_or_edit.html'
    form_class = ArticlePostForm
    article = None

    def get_context_data(self, **kwargs):
        context = super(ArticlePostView, self).get_context_data(**kwargs)
        article_link = 'article/' + self.request.user.username + '/'
        context['post_page'] = dict(article_link=article_link)
        return context

    def form_valid(self, form):
        self.article = form.save(self.request.user.username)
        return super(ArticlePostView, self).form_valid(form)

    def get_success_url(self):
        if 'post' in self.request.POST:
            return self.article.get_absolute_url()
        elif 'draft' in self.request.POST:
            return self.article.get_edit_url()


class ArticleEditView(FormView):
    template_name = 'blog/article_post_or_edit.html'
    form_class = ArticlePostForm
    success_url = '/'
    article = None
    article_link = msg = ''

    def get_initial(self, *args, **kwargs):
        article_link = self.kwargs.get('article_link')
        author = self.kwargs.get('author')
        try:
            self.article = Article.objects.get(article_link=article_link, author=author)
            initial = {
                'article_link': article_link,
                'article_title': self.article.article_title,
                'content': self.article.content_md,
                'tags': self.article.join_tags(),
                'category': Category.objects.get(pk=self.article.category_id),
            }
            return initial
        except Article.DoesNotExist:
            raise Http404("Article does not exist")

    def get_context_data(self, **kwargs):
        post_to_edit = False
        try:
            HTTP_REFERER = self.request.META['HTTP_REFERER']
            post_view_url = reverse('blog:article_post')
            if post_view_url in HTTP_REFERER:
                post_to_edit = True
        except KeyError:
            pass
        context = super(ArticleEditView, self).get_context_data(**kwargs)
        article_link = 'article/' + self.article.author + '/'
        context['post_page'] = dict(article_link=article_link, post_to_edit=post_to_edit)
        return context

    def form_invalid(self, form):
        response = super(ArticleEditView, self).form_invalid(form)
        self.msg = u'保存失败，请重试！'
        if self.request.is_ajax():
            return JsonResponse({'message': self.msg})
        else:
            return response

    def form_valid(self, form):
        self.msg = u'保存成功！'
        self.article = form.save(self.article.author, self.article.id)
        redirect_to_detail = self.article.get_absolute_url()
        if self.request.is_ajax():
            return JsonResponse({'message': self.msg, 'redirect_to_detail': redirect_to_detail})
        else:
            return super(ArticleEditView, self).form_valid(form)


class UserInfoView(DetailView):
    template_name = 'blog/user_info.html'
    context_object_name = 'author'
    user = None

    def get_object(self, *args, **kwargs):
        try:
            user_id = int(self.kwargs.get('user_id'))
            self.user = Author.objects.get(id=user_id)
        except Author.DoesNotExist:
            raise Http404(u'该用户不存在')
        return self.user

    def get_context_data(self, **kwargs):
        context = super(UserInfoView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.username == self.user.username:
            context['article_list'] = Article.objects.filter(author=self.user.username)
        else:
            context['article_list'] = Article.posted.filter(author=self.user.username)
        return context


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    new_user = None

    def form_valid(self, form):
        self.new_user = form.save()
        # send_mail(u'Hello Blog注册成功', u'感谢您的注册，祝您生活愉快', settings.DEFAULT_FROM_EMAIL,
        #           [self.new_user.email, ])
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password1'])
        permission = Permission.objects.get(name=u'Can delete 文章')
        user.user_permissions.add(permission)
        if user is not None and user.is_active:
            login(self.request, user)
        else:
            return redirect(reverse('login'))
        return super(RegisterView, self).form_valid(form)

    def get_success_url(self):
        return self.new_user.get_absolute_url()


class TagFilterView(ListView):
    tag_name = ''

    def get_flag(self):
        flag = self.kwargs.get('tag_or_tags')
        return flag     # tag or tags

    def get_template_names(self):
        if self.get_flag() == 'tag':
            return 'blog/tag.html'
        return 'blog/tags.html'

    def get_context_object_name(self, object_list):
        if self.get_flag() == 'tag':
            return 'article_list'
        return 'tag_dict'

    def get_queryset(self, *args, **kwargs):
        if self.get_flag() == 'tag':
            self.tag_name = self.kwargs.get('tag_name')
            tag = get_object_or_404(Tag, name=self.tag_name)
            article_list = tag.article_set.filter(status='p')
            return get_object_list(self, article_list, per_page=20, orphans=5)
        else:
            tag_dict = TagCloud(tag_model=Tag).get_tag_cloud()
            return tag_dict

    def get_context_data(self, **kwargs):
        context = super(TagFilterView, self).get_context_data(**kwargs)
        context['tag_name'] = self.tag_name
        return context


class CategoryFilterView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'article_list'
    category_name = ''

    def get_queryset(self, *args, **kwargs):
        self.category_name = self.kwargs.get('category_name')
        category = get_object_or_404(Category, name=self.category_name)
        article_list = category.article_set.filter(status='p')
        return get_object_list(self, article_list, per_page=20, orphans=5)

    def get_context_data(self, **kwargs):
        context = super(CategoryFilterView, self).get_context_data(**kwargs)
        context['category_name'] = self.category_name
        return context


class ArchivesView(ListView):
    template_name = 'blog/archives.html'
    context_object_name = 'archives_dict'

    def get_queryset(self, *args, **kwargs):
        archives_dict = {}
        for year in Article.objects.archives():
            archives_dict[str(year)] = Article.posted.filter(created_time__year=year)
        return archives_dict

    def get_context_data(self, **kwargs):
        context = super(ArchivesView, self).get_context_data(**kwargs)
        context['date_archives'] = Article.objects.archives()
        return context


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.updated_time


def about_view(request):
    """待添加功能"""
    return render(request, template_name='blog/about.html')


def read_books(request):
    """待添加功能"""
    return render(request, template_name='blog/read_books.html')


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.user.has_perm('blog.delete_article') and request.method == 'DELETE' and request.is_ajax():
        article.delete()
        msg = 'success'
    else:
        msg = 'failed'
    return JsonResponse({'msg': msg})


def download_image(request):
    image = open(r'static/blog/source/images/1.jpg', 'rb').read()
    response = HttpResponse(image, content_type="image/jpg")
    response['Content-Disposition'] = 'attachment; filename=sunset.jpg'
    return response


def change_avatar(request, user_id):
    if request.method == 'POST' and request.is_ajax():
        user = Author.objects.get(pk=user_id)
        image = request.FILES['change_avatar']
        file_suffix = image.name.split('.')[-1]
        if file_suffix in ['jpg', 'jpeg', 'gif', 'png']:
            os.remove(user.avatar.path)
            image.name = user.username + '.' + file_suffix
            user.avatar = image
            user.save()
            return JsonResponse({'msg': u'修改头像成功', 'status': 'OK', 'img_url': user.avatar.url})
        else:
            return JsonResponse({'msg': u'上传的文件格式不对', 'status': 'fail'})
    return JsonResponse({'msg': u'修改头像失败', 'status': 'fail'})
