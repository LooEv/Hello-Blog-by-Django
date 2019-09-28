#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : init_data.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-09-25 21:37:51
@History :
@Desc    :
"""

import datetime

from django.utils.timezone import make_aware
from blog.models import Article, Author, Tag, Category

text = [s.strip() for s in """
我美丽的新娘
我大胆走过你身旁
以为你有话要对我讲
我不敢抬头看着你
喔  的脸庞
你问我要去向何方
我指着你心的方向
你的微笑像是给我
""".splitlines() if s.strip()]


def init_data(cls):
    cls.author1 = Author.objects.create_user(username='loo1', id=1, email='loo1@gmail.com', password='A1B2C34G56LZ')
    cls.author2 = Author.objects.create_user(username='loo2', id=2, email='loo2@gmail.com', password='A1B2C34G56LZ')
    cls.author3 = Author.objects.create_user(username='loo3', id=3, email='loo3@gmail.com', password='A1B2C34G56LZ')
    cls.category1 = Category.objects.create(name='category1', id=1)
    for i in range(1, 31):
        content = f'{text[i % len(text)]}'
        setattr(cls, f'article{i}', Article.objects.create(
            id=i,
            article_link=f'article{i}',
            article_title=f'django 使用分享{i}',
            author_id=i % 3 if i % 3 else 3,
            category_id=1,
            content_md=content,
            content_html=f'<p>{content}</p>',
            views=i % 2,  # range 0, 1
            created_time=make_aware(datetime.datetime(2019 - i % 2, i % 7 + 1, 10, 10, 45, 24, 284292)),
            updated_time=make_aware(datetime.datetime(2019, 9, 10, 11, 45, 24, 284292)),
            status='p' if i % 10 else 'd',  # 10, 20, 30 is 'd'
        ))
        if not getattr(cls, f'tag{i % 7}', None):
            setattr(cls, f'tag{i % 7}', Tag.objects.get_or_create(name=f'tag{i % 7}')[0])
        getattr(cls, f'article{i}').tags.add(getattr(cls, f'tag{i % 7}'))
