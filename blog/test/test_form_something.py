#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : test_form_something.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-09-28 16:16:11
@History :
@Desc    :
"""

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from blog.forms import RegisterForm
from .init_data import init_data


class FormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        init_data(cls)

    def test_register_form_repeat_username(self):
        post_data = {
            'username': 'loo1', 'email': 'test@test.com',
            'password1': 'A1B2C34G56LZ',
            'password2': 'A1B2C34G56LZ',
        }
        form = RegisterForm(data=post_data)
        self.assertTrue('username' in form.errors)
        self.assertTrue(_("A user with that username already exists.") in form.errors['username'])

    def test_register_form_email(self):
        post_data = {
            'username': 'dont_exist', 'email': 'loo1@gmail.com',
            'password1': 'A1B2C34G56LZ',
            'password2': 'A1B2C34G56LZ',
        }
        form = RegisterForm(data=post_data)
        self.assertTrue('email' in form.errors)
        self.assertTrue('此电子邮箱已经被注册，请输入其他电子邮箱！' in form.errors['email'])

    def test_register_form_password(self):
        post_data = {
            'username': 'dont_exist', 'email': 'dont_exist@gmail.com',
            'password1': 'A1B2C34G56LZ',
            'password2': 'A1B2C34G56LZ1',
        }
        form = RegisterForm(data=post_data)
        self.assertTrue('password2' in form.errors)
        self.assertTrue('两次输入的密码不同，请重新输入！' in form.errors['password2'])

    def test_register_form_is_valid(self):
        post_data = {
            'username': 'dont_exist', 'email': 'dont_exist@gmail.com',
            'password1': 'A1B2C34G56LZ',
            'password2': 'A1B2C34G56LZ',
        }
        form = RegisterForm(data=post_data)
        self.assertTrue(form.is_valid())
