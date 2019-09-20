#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

import re

import markdown

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from .models import Article, Category, Author, Tag


class ArticlePostForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    tags_str_set = None

    article_title = forms.CharField(
        label='文章标题',
        max_length=50,
        error_messages={'required': '文章标题不能为空！', 'invalid': '请输入正确的文章标题'},
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '文章标题', 'title': '必填'}),
    )

    content = forms.CharField(
        label='正文',
        min_length=10,
        error_messages={'required': '文章内容都还没写，就想提交？！', 'min_length': '文章内容太少了，多写点哈'},
        widget=forms.Textarea(attrs={'placeholder': '请使用 Markdown 格式创作文章'}),
    )

    tags = forms.CharField(
        label='标签',
        max_length=30,
        error_messages={'required': '文章标签不能为空！', 'invalid': '能不能别乱填标签'},
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '标签，以逗号进行分割', 'title': '必填'}),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='分类',
        error_messages={'required': '文章分类不能为空！', 'invalid': '请正确选择分类，好吗？'},
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    status = forms.CharField(label='文章状态', widget=forms.HiddenInput())

    @staticmethod
    def gen_article_link(user_id):
        """如果10次还没有成功生成没有使用过的url,那你的网站的某个作者太666*666了"""
        max_times = 10
        while max_times:
            article_link = get_random_string(length=9).lower()
            if Article.objects.filter(article_link=article_link, author_id=user_id):
                max_times -= 1
            else:
                return article_link

    def clean_tags(self):
        tags = re.split(r',| +', self.cleaned_data['tags'])
        tags = set([tag.strip() for tag in tags if tag.strip()])
        if len(tags) >= 5:
            raise ValidationError(_('标签不能超过5个'))
        self.tags_str_set = tags

    def get_tags(self):
        tags = []
        for tag in self.tags_str_set:
            tags.append(Tag.objects.get_or_create(name=tag)[0])
        return tags

    def save(self, user_id, article_id=None):
        article_title = self.cleaned_data['article_title'].strip()
        content_md = self.cleaned_data['content']
        content_html = markdown.markdown(
            self.cleaned_data['content'],
            extensions=['markdown.extensions.extra', 'markdown.extensions.nl2br', ]
        )
        new_tags = self.get_tags()
        status = self.cleaned_data['status']
        category = Category.objects.get(name=self.cleaned_data['category'])
        if article_id:
            Article.objects.filter(pk=article_id). \
                update(article_title=article_title,
                       content_md=content_md,
                       content_html=content_html,
                       status=status,
                       category=category,
                       updated_time=timezone.now())
            article = Article.objects.get(pk=article_id)
            clear_tags = [tag.id for tag in article.tags.all() if tag not in new_tags]
            if clear_tags:
                article.tags.filter(pk__in=clear_tags).delete()
            article.tags.clear()
            article.tags.add(*new_tags)
            article.save()
        else:
            article_link = self.gen_article_link(user_id)
            article = Article(article_link=article_link,
                              article_title=article_title,
                              author_id=user_id,
                              content_md=content_md,
                              content_html=content_html,
                              views=0,
                              status=status,
                              category=category)
            article.save()
            article.tags.add(*new_tags)
        return article


class RegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    error_messages = {
        'password_mismatch': '两次输入的密码不同，请重新输入！',
        'email_existed': '此电子邮箱已经被注册，请输入其他电子邮箱！',
    }

    password1 = forms.CharField(error_messages={'required': '密码都不填，你是在逗我吗？！'})
    password2 = forms.CharField(error_messages={'required': '难道你觉得不需要确认密码吗？！'})

    class Meta:
        model = Author
        fields = ('username', 'email')
        error_messages = {
            'username': {
                'max_length': '用户名太长了，亲~.~',
                'required': '用户名还没填呢',
            },
            'email': {
                'required': '电子邮箱地址还没填呢',
            }
        }

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise ValidationError(self.error_messages['password_mismatch'],
                                  code='password_mismatch')
        self.instance.username = self.cleaned_data['username']
        password_validation.validate_password(self.cleaned_data['password2'], self.instance)
        return password2

    def clean_email(self):
        email = self.cleaned_data['email']
        if Author.objects.filter(email=email):
            raise ValidationError(self.error_messages['email_existed'], code='email_existed')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
