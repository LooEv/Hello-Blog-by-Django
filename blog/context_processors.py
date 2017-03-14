#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

from django.contrib.sessions.models import Session
from django.conf import settings
from .models import Category


def hello_blog(request):
    """
    加载博客站点相关全局配置
    """
    blog_data = dict()
    blog_data['site_domain'] = getattr(settings, 'SITE_DOMAIN', 'http://example.com/')
    blog_data['site_title'] = getattr(settings, 'SITE_TITLE', 'Hello Blog')
    blog_data['duoshuo_shortname'] = getattr(settings, 'DUOSHUO_SHORTNAME')
    blog_data['categories'] = Category.objects.all().order_by('created_time')
    return {'blog_data': blog_data}
