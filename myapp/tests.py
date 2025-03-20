from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment
from django.utils import timezone

class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        test_user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a test post
        Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=test_user,
            created_date=timezone.now()
        )
    
    def test_title_label(self):
        post = Post.objects.get(id=1)
        field_label = post._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')
    
    def test_title_max_length(self):
        post = Post.objects.get(id=1)
        max_length = post._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)
    
    def test_content_label(self):
        post = Post.objects.get(id=1)
        field_label = post._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')
    
    def test_author_label(self):
        post = Post.objects.get(id=1)
        field_label = post._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')
    
    def test_created_date_label(self):
        post = Post.objects.get(id=1)
        field_label = post._meta.get_field('created_date').verbose_name
        self.assertEqual(field_label, 'created date')
    
    def test_object_name_is_title(self):
        post = Post.objects.get(id=1)
        expected_object_name = post.title
        self.assertEqual(str(post), expected_object_name)
    
    def test_get_absolute_url(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.get_absolute_url(), reverse('post-detail', args=[str(post.id)]))
    
    def test_ordering(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post._meta.ordering, ['-created_date'])

class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        test_user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a test post
        test_post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=test_user,
            created_date=timezone.now()
        )
        
        # Create a test comment
        Comment.objects.create(
            post=test_post,
            author=test_user,
            content='This is a test comment content.',
            created_date=timezone.now()
        )
        
        # Create a test comment with more than 75 characters
        Comment.objects.create(
            post=test_post,
            author=test_user,
            content='This is a test comment content with more than 75 characters. It should be truncated in the string representation.',
            created_date=timezone.now()
        )
    
    def test_post_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('post').verbose_name
        self.assertEqual(field_label, 'post')
    
    def test_author_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')
    
    def test_content_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')
    
    def test_created_date_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('created_date').verbose_name
        self.assertEqual(field_label, 'created date')
    
    def test_object_name_is_truncated_content(self):
        # Test short comment (no truncation)
        comment1 = Comment.objects.get(id=1)
        self.assertEqual(str(comment1), comment1.content)
        
        # Test long comment (truncated)
        comment2 = Comment.objects.get(id=2)
        expected_truncated = comment2.content[:75] + '...'
        self.assertEqual(str(comment2), expected_truncated)
    
    def test_ordering(self):
        comment = Comment.objects.get(id=1)
        self.assertEqual(comment._meta.ordering, ['created_date'])

class BlogListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        test_user = User.objects.create_user(username='testuser', password='12345')
        
        # Create 8 posts for pagination tests
        number_of_posts = 8
        for post_num in range(number_of_posts):
            Post.objects.create(
                title=f'Test Post {post_num}',
                content=f'Test content for post {post_num}',
                author=test_user,
                created_date=timezone.now()
            )
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/blogs/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/post_list.html')
    
    def test_pagination_is_correct(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['posts']), 5)  # 5 items on first page

class BloggerListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 3 users
        number_of_users = 3
        for user_num in range(number_of_users):
            test_user = User.objects.create_user(
                username=f'testuser{user_num}', 
                password='12345'
            )
            
            # Create 2 posts for each user
            for post_num in range(2):
                Post.objects.create(
                    title=f'Test Post {user_num}-{post_num}',
                    content=f'Test content for post {post_num} by user {user_num}',
                    author=test_user,
                    created_date=timezone.now()
                )
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/bloggers/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blogger-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blogger-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/blogger_list.html')
    
    def test_context_data_contains_bloggers_with_posts(self):
        response = self.client.get(reverse('blogger-list'))
        self.assertEqual(response.status_code, 200)
        # Should have 3 bloggers
        self.assertEqual(len(response.context['bloggers']), 3)

class AuthorDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        test_user = User.objects.create_user(username='testuser', password='12345')
        
        # Create 5 posts for the user
        number_of_posts = 5
        for post_num in range(number_of_posts):
            Post.objects.create(
                title=f'Test Post {post_num}',
                content=f'Test content for post {post_num}',
                author=test_user,
                created_date=timezone.now()
            )
    
    def test_view_url_exists_at_desired_location(self):
        test_user = User.objects.get(username='testuser')
        response = self.client.get(f'/blog/author/{test_user.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        test_user = User.objects.get(username='testuser')
        response = self.client.get(reverse('author-detail', args=[str(test_user.id)]))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        test_user = User.objects.get(username='testuser')
        response = self.client.get(reverse('author-detail', args=[str(test_user.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/author_detail.html')
    
    def test_context_data_contains_user_posts(self):
        test_user = User.objects.get(username='testuser')
        response = self.client.get(reverse('author-detail', args=[str(test_user.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 5)  # User has 5 posts
