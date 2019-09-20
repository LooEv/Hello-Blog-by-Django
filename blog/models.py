#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.urls import reverse


class ArchivesManager(models.Manager):
    def archives(self):
        date_list = self.get_queryset().dates('created_time', 'year', order='DESC')
        return [int(date.year) for date in date_list]


class PostedArticleManager(models.Manager):
    def get_queryset(self):
        return super(PostedArticleManager, self).get_queryset().filter(status='p')


class Author(AbstractUser):
    avatar = models.ImageField('头像', upload_to=r'user/avatar/', blank=True,
                               default=r'user/avatar/guest_a2b2c4z.png')
    bio = models.TextField('个人简介', max_length=1000, blank=True)
    location = models.CharField('地址', max_length=50, blank=True)

    def get_absolute_url(self):
        return reverse('blog:user_information', kwargs={'username': self.username})

    def __str__(self):
        return self.username


class Article(models.Model):
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发布'),
    )

    article_link = models.CharField('链接', max_length=12)
    article_title = models.CharField('文章标题', max_length=100)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, verbose_name='作者')
    tags = models.ManyToManyField('Tag', verbose_name='标签集合')  # 文章标签，以逗号进行分割
    category = models.ForeignKey('Category', on_delete=models.SET('未知分类'),
                                 verbose_name='所属分类')
    content_md = models.TextField('文章内容(md格式)')
    content_html = models.TextField('文章内容(Html格式)', null=True)
    views = models.IntegerField('浏览量')
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    updated_time = models.DateTimeField('更新时间', default=timezone.now)
    status = models.CharField('状态', max_length=1, choices=STATUS_CHOICES,
                              default=STATUS_CHOICES[0][0])

    objects = ArchivesManager()
    posted = PostedArticleManager()

    class Meta:
        ordering = ['-created_time', ]
        verbose_name = '文章'
        verbose_name_plural = '文章'

    def __str__(self):
        return self.article_title

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={
            'author': self.author.username, 'article_link': self.article_link})

    def get_edit_url(self):
        return reverse('blog:article_edit', kwargs={
            'author': self.author.username, 'article_link': self.article_link})

    def tags_split(self):
        return [tag.name for tag in self.tags.all()]

    def join_tags(self, join_with=','):
        return join_with.join(self.tags_split())

    def get_author_homepage(self):
        return reverse('blog:user_information',
                       kwargs={'username': self.author.username})


class Tag(models.Model):
    name = models.CharField('名称', max_length=30, db_index=True, unique=True)
    created_time = models.DateTimeField('创建时间', default=timezone.now)

    class Meta:
        ordering = ['name', ]
        verbose_name = '文章标签'
        verbose_name_plural = '文章标签'

    def get_absolute_url(self):
        return reverse('blog:tag_filter', kwargs={'tag_name': self.name})

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('名称', max_length=30, db_index=True, unique=True)
    created_time = models.DateTimeField('创建时间', default=timezone.now)

    class Meta:
        ordering = ['name', ]
        verbose_name = '文章分类'
        verbose_name_plural = '文章分类'

    def __str__(self):
        return self.name
