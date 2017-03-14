#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

from django.utils.encoding import force_bytes
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Permission
from django.core.urlresolvers import reverse
from django.db import models
from collections import defaultdict


class ArchivesManager(models.Manager):
    def archives(self):
        date_list = Article.objects.dates('created_time', 'year', order='DESC')
        date_list = [date.year for date in date_list]
        return sorted(date_list, reverse=True)


class PostManager(models.Manager):
    def get_queryset(self):
        return super(PostManager, self).get_queryset().filter(status='p')


class Article(models.Model):
    STATUS_CHOICES = (
        ('d', u'草稿'),
        ('p', u'发布'),
    )

    # article_link 表示文章在网址链接中显示的文章标题，建议使用英文字母
    article_link = models.CharField(u'链接', max_length=100, blank=True)
    article_title = models.CharField(u'文章标题', max_length=100)
    # author = models.ForeignKey('Author', verbose_name=u'作者')
    author = models.CharField(u'作者', max_length=50)
    tags = models.ManyToManyField('Tag', verbose_name=u'标签集合' )
    # tags = models.CharField(u'标签', max_length=100)  # 文章标签，以逗号进行分割
    category = models.ForeignKey('Category', verbose_name=u'所属分类')
    content_md = models.TextField(u'文章内容(md格式)')
    content_html = models.TextField(u'文章内容(Html格式)', null=True)
    views = models.IntegerField(u'浏览量')
    created_time = models.DateTimeField(u'创建时间', default=timezone.now)
    updated_time = models.DateTimeField(u'更新时间')
    status = models.CharField(u'状态', max_length=1, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    objects = ArchivesManager()
    posted = PostManager()

    class Meta:
        ordering = ['-created_time', ]
        verbose_name = u'文章'
        verbose_name_plural = u'文章'

    def __str__(self):
        return force_bytes(self.article_title)

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'author': self.author, 'article_link': self.article_link})

    def get_edit_url(self):
        return reverse('blog:article_edit', kwargs={'author': self.author, 'article_link': self.article_link})

    def tags_split(self):
        return [tag.name for tag in self.tags.all()]

    def join_tags(self):
        return ','.join([tag.name for tag in self.tags.all()])

    def get_author_homepage(self):
        return Author.objects.get(username=self.author).get_absolute_url()

    def save(self, *args, **kwargs):
        self.article_link = slugify(self.article_link, allow_unicode=True)
        super(Article, self).save(*args, **kwargs)


class Author(AbstractUser):
    # name = models.CharField(u'名字', max_length=50, db_index=True)
    # email = models.EmailField(u'邮箱', unique=True)
    # password = models.CharField(u'密码', max_length=30)
    # register_time = models.DateTimeField(u'注册时间')

    avatar = models.ImageField(u'头像', upload_to=r'user/avatar/', blank=True, default=r'user/avatar/guest.png')
    bio = models.TextField(u'个人简介', max_length=1000, blank=True)
    location = models.CharField(u'地址', max_length=50, blank=True)

    def get_absolute_url(self):
        return reverse('blog:user_information', kwargs={'user_id': str(self.id)})

    def __str__(self):
        return force_bytes(self.username)


class Category(models.Model):
    name = models.CharField(u'名称', max_length=30, db_index=True, unique=True)
    created_time = models.DateTimeField(u'创建时间', default=timezone.now)

    class Meta:
        ordering = ['name', ]
        verbose_name = u'文章分类'
        verbose_name_plural = u'文章分类'

    def __str__(self):
        return force_bytes(self.name)


class Tag(models.Model):
    name = models.CharField(u'名称', max_length=30, db_index=True, unique=True)
    created_time = models.DateTimeField(u'创建时间', default=timezone.now)

    class Meta:
        ordering = ['name', ]
        verbose_name = u'文章标签'
        verbose_name_plural = u'文章标签'

    def get_absolute_url(self):
        return reverse('blog:tag_filter', kwargs={'tag_name': self.name})

    def __str__(self):
        return force_bytes(self.name)


class ReadBooks(models.Model):
    STATUS_CHOICES = (
        (0, u'已读'),
        (1, u'在读'),
        (2, u'想读'),
    )
    title = models.CharField(u'书名', max_length=100, db_index=True, unique=True)
    author = models.CharField(u'作者', max_length=100)
    book_link = models.URLField(u'书籍豆瓣链接')
    cover = models.URLField(u'封面图片链接')
    review = models.TextField(u'读后感')
    score = models.FloatField(u'评分')
    status = models.IntegerField(u'状态', choices=STATUS_CHOICES, default=STATUS_CHOICES[1][0])

    class Meta:
        ordering = ['title', ]
        verbose_name = u'读书'
        verbose_name_plural = u'读书'

    def __str__(self):
        return force_bytes(self.title)
