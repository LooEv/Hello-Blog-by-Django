#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : test_tag_filter.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-09-24 22:34:02
@History :
@Desc    :
"""

from django.test import TestCase

from .init_data import init_data


class TagFilterTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        init_data(cls)

    def test_get_tag_name(self):
        res = self.client.get('/tag/tag1')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'blog/tag.html')
        self.assertTrue(res.context.get('article_list') is not None)
        self.assertTrue(self.article1 in res.context['article_list'])
        self.assertTrue(self.article8 in res.context['article_list'])

    def test_tags(self):
        res = self.client.get('/tags/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'blog/tags.html')
        self.assertTrue(res.context.get('tag_dict') is not None)
        self.assertTrue('tag1' in res.context['tag_dict'])
        # tag_dict: {'tag0': 3, 'tag1': 5, 'tag2': 5, 'tag3': 3, ...}
        sorted_tag_dict = sorted(res.context['tag_dict'].items(), key=lambda x: x[-1])
        self.assertTrue(sorted_tag_dict[-1][0] in ['tag1', 'tag2'])
