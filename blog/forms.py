#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

import datetime
import markdown
import random
import string
import re
from django import forms
from django.utils.text import slugify
from .models import Article, Category, Author, Tag
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import password_validation


class ArticlePostForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    article_title = forms.CharField(
        label=u'文章标题',
        max_length=50,
        error_messages={'required': u'文章标题不能为空！', 'invalid': u'请输入正确的文章标题'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'文章标题', 'title': u'必填'}),
    )

    article_link = forms.CharField(
        label=u'文章的英文链接',
        max_length=100,
        error_messages={'required': u'文章的英文链接不能为空！', 'invalid': u'请输入有效的文章英文链接'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'文章的英文链接，尽量别使用中文',
                                      'title': u'文章的英文链接：必填，请勿频繁修改此项'}),
    )

    content = forms.CharField(
        label=u'正文',
        min_length=10,
        error_messages={'required': u'文章内容都还没写，就想提交？！', 'min_length': u'文章内容太少了，多写点哈'},
        widget=forms.Textarea(attrs={'placeholder': u'请使用 Markdown 格式创作文章'}),
    )

    tags = forms.CharField(
        label=u'标签',
        max_length=30,
        error_messages={'required': u'文章标签不能为空！', 'invalid': u'能不能别乱填标签'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'标签，以逗号进行分割', 'title': u'必填'}),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label=u'分类',
        error_messages={'required': u'文章分类不能为空！', 'invalid': u'请正确选择分类，好吗？'},
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': u'分类，以逗号进行层次分割'}),
    )

    status = forms.CharField(
        label=u'文章状态',
        widget=forms.HiddenInput()
    )

    def get_valid_article_link(self, article_id, username, article_link):
        article_link = slugify(article_link, allow_unicode=True)
        while 1:
            try:
                article = Article.objects.get(article_link=article_link, author=username)
                if article.id != article_id:
                    article_link += ''.join(random.sample(string.digits, 3))
                    continue
                else:
                    break
            except Article.DoesNotExist:
                break
        return article_link

    def save(self, username, article_id=None):
        article_link = self.cleaned_data['article_link'].replace(' ', '-').strip()
        self.article_link = self.get_valid_article_link(article_id, username, article_link)
        article_title = self.cleaned_data['article_title'].strip()
        author = Author.objects.get(username=username)
        now = datetime.datetime.now()
        content_md = self.cleaned_data['content']
        content_html = markdown.markdown(self.cleaned_data['content'], extensions=['markdown.extensions.extra',
                                                                                   'markdown.extensions.nl2br', ])
        tags = []
        for tag in re.split(r',| +', self.cleaned_data['tags']):
            if tag:
                tags.append(Tag.objects.get_or_create(name=tag.strip())[0])
        status = self.cleaned_data['status']
        category = Category.objects.get(name=self.cleaned_data['category'])
        if article_id:
            article = Article.objects.filter(pk=article_id)
            article.update(article_link=self.article_link,
                           article_title=article_title,
                           content_md=content_md,
                           content_html=content_html,
                           status=status,
                           category=category,
                           updated_time=now)
            article = Article.objects.get(pk=article_id)
            for tag in article.tags.all():
                if tag not in tags:
                    article.tags.filter(pk=tag.id).delete()
            article.tags.clear()
            article.tags.add(*tags)
            article.save()
        else:
            article = Article(
                article_link=self.article_link,
                article_title=article_title,
                author=author,
                content_md=content_md,
                content_html=content_html,
                views=0,
                status=status,
                category=category,
                updated_time=now)
            article.save()
            article.tags.add(*tags)
        return article


class RegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    error_messages = {
        'password_mismatch': u'两次输入的密码不同，请重新输入！',
        'email_existed': u'此电子邮箱已经被注册，请输入其他电子邮箱！',
    }

    password1 = forms.CharField(error_messages={'required': u'密码都不填，你是在逗我吗？！'})
    password2 = forms.CharField(error_messages={'required': u'难道你觉得不需要确认密码吗？！'})

    class Meta:
        model = Author
        fields = ('username', 'email')
        error_messages = {
            'username': {
                'max_length': u'用户名太长了，亲~.~',
                'required': u'用户名还没填呢',
            },
            'email': {
                'required': u'电子邮箱地址还没填呢',
            }
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch',)
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def clean_email(self):
        email = self.cleaned_data['email']
        res = Author.objects.filter(email=email)
        if len(res) != 0:
            raise forms.ValidationError(self.error_messages['email_existed'], code='email_existed')
        return email

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
