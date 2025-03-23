from django.contrib import admin
from .models import Post, Comment, Category, Tag

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_date',)
    fields = ('author', 'content', 'created_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_date', 'display_tags')
    list_filter = ('created_date', 'author', 'category', 'tags')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_date'
    filter_horizontal = ('tags',)
    inlines = [CommentInline]
    
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()[:3]])
    
    display_tags.short_description = 'Tags'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'post', 'author', 'created_date')
    list_filter = ('created_date', 'author', 'post')
    search_fields = ('content', 'post__title', 'author__username')
    date_hierarchy = 'created_date'
    
    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    
    truncated_content.short_description = 'Comment'
