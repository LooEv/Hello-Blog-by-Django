from django.contrib import admin
from .models import Article, Category, Author, Tag


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('article_title', 'author', 'category', 'status', 'views', 'created_time', 'updated_time')
    list_filter = ['author', 'category', 'status']
    search_fields = ['article_title', 'author']
    date_hierarchy = 'created_time'
    # raw_id_fields = ('category',)


class BlogAuthor(admin.ModelAdmin):
    list_display = ('username', 'email', 'location', 'is_staff', 'is_active', 'date_joined', 'last_login')


admin.site.register(Author, BlogAuthor)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)
admin.site.register(Tag)
