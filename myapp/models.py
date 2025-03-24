from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.slug)])

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag-detail', args=[str(self.slug)])

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_date']  # Sort by newest first
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])

    def total_likes(self):
        return self.likes.count()
    
    def get_reading_time(self):
        """Calculate the estimated reading time in minutes.
        Average reading speed is about 200-250 words per minute for adults."""
        word_count = len(self.content.split())
        reading_time_minutes = max(1, round(word_count / 200))
        return reading_time_minutes
    
    def get_related_posts(self):
        """Get posts that share the same category or tags."""
        related_posts = Post.objects.exclude(id=self.id)
        
        # If the post has a category, get posts from the same category
        if self.category:
            related_posts = related_posts.filter(category=self.category)
        
        # Add posts that share tags (if this post has tags)
        tags = self.tags.all()
        if tags.exists():
            tagged_posts = Post.objects.filter(tags__in=tags).exclude(id=self.id).distinct()
            # Combine the two querysets without duplicates
            if related_posts.exists():
                related_posts = (related_posts | tagged_posts).distinct()
            else:
                related_posts = tagged_posts
        
        # Return at most 3 related posts, ordered by created date
        return related_posts.order_by('-created_date')[:3]

    def increment_view_count(self):
        """Increment the view count for this post."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
        return self.view_count

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_date']  # Sort by oldest first
    
    def __str__(self):
        truncated_content = self.content[:75] + '...' if len(self.content) > 75 else self.content
        return truncated_content
