#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : test_article_detail.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-09-24 22:34:02
@History :
@Desc    :
"""

from django.test import TestCase

from .init_data import init_data


class DetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        init_data(cls)

    def test_get_detail_by_link(self):
        res = self.client.get('/article/loo1/article1.html')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'blog/article_detail.html')
        self.assertEqual(res.context['previous_article'], self.article2)
        self.assertEqual(res.context['next_article'], None)
        self.assertContains(res, '<p>我大胆走过你身旁</p>')

        res = self.client.get('/article/loo3/article3.html')
        self.assertEqual(res.context['previous_article'], self.article4)
        self.assertEqual(res.context['next_article'], self.article2)

        res = self.client.get('/article/loo3/article9.html')
        # self.article10 status is draft, so `previous_article` is self.article11
        self.assertEqual(res.context['previous_article'], self.article11)
        self.assertEqual(res.context['next_article'], self.article8)

    def test_detail_object_does_not_exist(self):
        res = self.client.get('/article/does_not_exist/article1.html')
        self.assertEqual(res.status_code, 404)
        self.assertTemplateUsed(res, '404.html')

    def test_view_add_1(self):
        res = self.client.get('/article/loo1/article1.html')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['article'].views, 2)

    def test_visit_draft_article(self):
        self.client.post('/accounts/login/',
                         {'username': 'loo1', 'password': 'A1B2C34G56LZ'})
        # self.article10 status is draft, but loo1 has been login, so it can access
        res = self.client.get('/article/loo1/article10.html')
        self.assertEqual(res.status_code, 200)
