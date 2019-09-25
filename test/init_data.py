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
    cls.author1 = Author.objects.create(username='loo1', id=1)
    cls.author2 = Author.objects.create(username='loo2', id=2)
    cls.author3 = Author.objects.create(username='loo3', id=3)
    for i in range(1, 30):
        content = f'{text[i % len(text)]}{i}'
        setattr(cls, f'article{i}', Article.objects.create(
            id=i,
            article_link=f'article{i}',
            article_title='django 使用分享',
            author_id=i % 3 if i % 3 else 1,
            category_id=1,
            content_md=content,
            content_html=f'<p>{content}</p>',
            views=i % 2,
            created_time=datetime.datetime(2019, 9, 10, 10, 45, 24, 284292),
            updated_time=datetime.datetime(2019, 9, 10, 11, 45, 24, 284292),
            status='p',
        ))
