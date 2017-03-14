#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv


class TagCloud(object):
    def __init__(self, tag_model):
        self.tags = tag_model.objects.all
        self.max_tag_count = self.min_tag_count = 0

    def get_font_size(self, max_font_size, min_font_size, tag_dict):
        step = (max_font_size - min_font_size) * 1.0 / (self.max_tag_count - self.min_tag_count)
        for tag_name, count in tag_dict.iteritems():
            font_size = min_font_size + (count - self.min_tag_count) * step
            if 0.5 < (font_size - min_font_size) < 1.0:
                font_size = min_font_size + 1
            elif 0.5 < (font_size - max_font_size) < 1.0:
                font_size = max_font_size
            tag_dict[tag_name] = int(font_size)
        return tag_dict

    def get_tag_cloud(self):
        tag_dict = {}
        if not self.tags():
            return tag_dict
        for tag in self.tags():
            tag_dict[tag.name] = tag.article_set.all().count()
        self.max_tag_count = max(tag_dict.iteritems(), key=lambda x: x[1])[1]
        self.min_tag_count = min(tag_dict.iteritems(), key=lambda x: x[1])[1]
        if self.max_tag_count == self.min_tag_count:
            for tag_name in tag_dict.iterkeys():
                tag_dict[tag_name] = 4
        else:
            tag_dict = self.get_font_size(8, 1, tag_dict)
        return tag_dict
