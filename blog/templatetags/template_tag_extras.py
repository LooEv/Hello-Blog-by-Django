#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv

from django import template

register = template.Library()


@register.filter(name='myfilter')
def myfilter(value):
    return value.upper()
