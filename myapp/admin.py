from django.contrib import admin
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_date',)
    fields = ('author', 'content', 'created_date')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date')
    list_filter = ('created_date', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_date'
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'post', 'author', 'created_date')
    list_filter = ('created_date', 'author', 'post')
    search_fields = ('content', 'post__title', 'author__username')
    date_hierarchy = 'created_date'
    
    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    
    truncated_content.short_description = 'Comment'
