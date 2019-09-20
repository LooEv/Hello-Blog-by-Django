#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

import os
from contextlib import suppress

from django.core.paginator import Paginator, Page
from django.views.generic import ListView, FormView, DetailView
from django.contrib.sitemaps import Sitemap
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Article, Author, Category, Tag
from .forms import ArticlePostForm, RegisterForm
from .lib.tag_cloud import TagCloud

DEFAULT_AVATAR_PATH = getattr(Author, '_meta').get_field('avatar').get_default()


class ArticleListView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'article_list'
    queryset = Article.posted.all()
    paginate_by = 10
    paginate_orphans = 1
    max_display_page_buttons = 10
    half_page_buttons = max_display_page_buttons // 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator: Paginator = context['paginator']
        if paginator.num_pages <= self.max_display_page_buttons:
            page_range = paginator.page_range
        else:
            page_obj: Page = context['page_obj']
            current_page = page_obj.number
            num_pages = paginator.num_pages
            page_range = {1, current_page, num_pages}
            # 使页码显示地更加人性化,在页码较多的情况下,始终有跳转到第1页和最后1页的链接
            for i in range(1, self.max_display_page_buttons + 1):
                if current_page + i < num_pages:
                    page_range.add(current_page + i)
                    if len(page_range) >= self.max_display_page_buttons:
                        break
                if current_page - i > 0:
                    page_range.add(current_page - i)
                    if len(page_range) >= self.max_display_page_buttons:
                        break
            page_range = sorted(page_range)
            return page_range

        context['page_range'] = page_range
        return context


class ArticleDetailView(DetailView):
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    current_article_id = None

    def get_object(self, *args, **kwargs):
        try:
            article_link = self.kwargs['article_link']
            author = self.kwargs['author']
            user = self.request.user
            if user.is_authenticated and (user.username == author or user.is_staff):
                queryset = Article.objects
            else:
                queryset = Article.posted
            article = queryset.get(article_link=article_link, author__username=author)
            article.views += 1
            article.save()
            self.current_article_id = article.id
        except Article.DoesNotExist:
            raise Http404("Article does not exist!")
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.current_article_id:
            previous_article = None
            next_article = None
            try:
                previous_article = Article.posted.filter(pk__gt=self.current_article_id). \
                    order_by('pk').only('article_link', 'article_title', 'author'). \
                    select_related('author').first()
            except Article.DoesNotExist:
                pass
            try:
                next_article = Article.posted.filter(pk__lt=self.current_article_id). \
                    order_by('-pk').only('article_link', 'article_title', 'author'). \
                    select_related('author').first()
            except Article.DoesNotExist:
                pass
            context['previous_article'] = previous_article
            context['next_article'] = next_article
        return context


class ArticlePostView(FormView):
    template_name = 'blog/article_post_or_edit.html'
    form_class = ArticlePostForm
    article = None

    def form_valid(self, form):
        self.article = form.save(self.request.user.id)
        return super().form_valid(form)

    def get_success_url(self):
        if 'post' in self.request.POST:
            return self.article.get_absolute_url()
        elif 'draft' in self.request.POST:
            return self.article.get_edit_url()


class ArticleEditView(FormView):
    template_name = 'blog/article_post_or_edit.html'
    form_class = ArticlePostForm
    article = None

    def get_initial(self, *args, **kwargs):
        try:
            article_link = self.kwargs['article_link']
            author = self.kwargs['author']
            self.article = Article.objects.get(article_link=article_link,
                                               author__username=author)
            initial = {
                'article_id': self.article.id,
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
        context = super().get_context_data(**kwargs)
        context['post_page'] = dict(post_to_edit=post_to_edit)
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        msg = '保存失败，请重试！'
        if self.request.is_ajax():
            return JsonResponse({'message': msg})
        else:
            return response

    def form_valid(self, form):
        msg = '保存成功！'
        self.article = form.save(self.article.author_id, self.article.id)
        redirect_to_detail = self.article.get_absolute_url()
        if self.request.is_ajax():
            return JsonResponse({'message': msg, 'redirect_to_detail': redirect_to_detail})
        else:
            return super().form_valid(form)

    def get_success_url(self):
        return self.article.get_absolute_url()


class UserInfoView(DetailView):
    template_name = 'blog/user_info.html'
    context_object_name = 'author'
    user = None

    def get_object(self, *args, **kwargs):
        try:
            username = self.kwargs['username']
            self.user = Author.objects.get(username=username)
        except Author.DoesNotExist:
            raise Http404('该用户不存在')
        return self.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.username == self.user.username:
            context['article_list'] = self.user.article_set.all()
        else:
            context['article_list'] = self.user.article_set.filter(status='p')
        return context


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    new_user = None

    def form_valid(self, form):
        self.new_user = form.save()
        user = authenticate(username=self.request.POST['username'],
                            password=self.request.POST['password1'])
        if user is not None and user.is_active:
            permission = Permission.objects.get(codename='add_article')
            user.user_permissions.add(permission)
            login(self.request, user)
            # send_mail('Hello Blog注册成功', '感谢您的注册，祝您生活愉快', settings.DEFAULT_FROM_EMAIL,
            #           [self.new_user.email, ])
        else:
            return redirect(reverse('login'))
        return super().form_valid(form)

    def get_success_url(self):
        return self.new_user.get_absolute_url()


class TagFilterView(ListView):
    paginate_by = 20
    paginate_orphans = 2
    context_object_name = 'article_list'

    def get_template_names(self):
        if self.kwargs['tag_or_tags'] == 'tag':
            return 'blog/tag.html'
        return 'blog/tags.html'

    def get_context_object_name(self, object_list):
        if self.kwargs['tag_or_tags'] == 'tag':
            return 'article_list'
        return 'tag_dict'

    def get_queryset(self, *args, **kwargs):
        if self.kwargs['tag_or_tags'] == 'tag':
            tag_name = self.kwargs.get('tag_name')
            tag = get_object_or_404(Tag, name=tag_name)
            article_list = tag.article_set.filter(status='p')
            return article_list
        else:
            self.paginate_by = None
            self.paginate_orphans = 0
            tag_dict = TagCloud(tag_model=Tag).get_tag_cloud()
            return tag_dict


class CategoryFilterView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 20
    paginate_orphans = 2
    context_object_name = 'article_list'

    def get_queryset(self, *args, **kwargs):
        category_name = self.kwargs['category_name']
        category = get_object_or_404(Category, name=category_name)
        article_list = category.article_set.filter(status='p')
        return article_list


class ArchivesView(ListView):
    template_name = 'blog/archives.html'
    context_object_name = 'archives_dict'

    def get_queryset(self, *args, **kwargs):
        archives_dict = {}
        for year in Article.objects.archives():
            archives_dict[str(year)] = Article.posted.filter(created_time__year=year). \
                select_related('author')
        return archives_dict


class BlogSitemap(Sitemap):
    limit = 1000
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Article.posted.all()

    def lastmod(self, item):
        return item.updated_time


def about_view(request):
    """待添加功能"""
    return render(request, template_name='blog/about.html')


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.user.has_perm('blog.delete_article') and \
            request.method == 'DELETE' and request.is_ajax():
        article.delete()
        msg = 'success'
    else:
        msg = 'failed'
    return JsonResponse({'msg': msg})


@login_required
def change_avatar(request, username):
    if request.method == 'POST' and request.is_ajax():
        user = Author.objects.get(username=username)
        if request.user.id == user.id:
            image = request.FILES['change_avatar']
            file_suffix = image.name.rsplit('.', 1)[-1]
            if file_suffix in ['jpg', 'jpeg', 'gif', 'png']:
                with suppress(FileNotFoundError):
                    if not user.avatar.path.endswith(DEFAULT_AVATAR_PATH):
                        os.remove(user.avatar.path)
                image.name = user.username + '.' + file_suffix
                user.avatar = image
                user.save()
                return JsonResponse({'msg': '修改头像成功', 'status': 'OK',
                                     'img_url': user.avatar.url})
            else:
                return JsonResponse({'msg': '上传的文件格式不对', 'status': 'fail'})
    return JsonResponse({'msg': '修改头像失败', 'status': 'fail'})
