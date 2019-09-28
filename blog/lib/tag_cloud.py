#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LooEv


class TagCloud:
    def __init__(self, tag_model):
        self.get_tags = tag_model.objects.all
        self.max_tag_count = self.min_tag_count = 0

    def get_tag_cloud(self, max_font_size=8, min_font_size=1):
        tag_font_size_dict = {}
        tags = self.get_tags()
        if not tags:
            return tag_font_size_dict
        tag_dict = {}
        for tag in tags:
            tag_dict[tag.name] = tag.article_set.count()
        count_list = sorted(tag_dict.values())
        max_tag_count = count_list[-1]
        min_tag_count = count_list[0]
        if max_tag_count == min_tag_count:
            for tag_name in tag_dict.keys():
                tag_font_size_dict[tag_name] = 4
        else:
            if len(set(count_list)) == 2:
                max_font_size, min_font_size = 5, 3
            step = (max_font_size - min_font_size) * 1.0 / (max_tag_count - min_tag_count)
            for tag_name, count in tag_dict.items():
                font_size = min_font_size + (count - min_tag_count) * step
                if 0.5 < (font_size - min_font_size) < 1.0:
                    font_size = min_font_size + 1
                elif 0.5 < (max_font_size - font_size) < 1.0:
                    font_size = max_font_size
                tag_font_size_dict[tag_name] = int(font_size)
        return tag_font_size_dict
