from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Post, Comment, Category, Tag
from .forms import CommentForm, PostSearchForm, PostForm
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.utils import translation
from django.conf import settings
from django.http import HttpResponseRedirect

class CategoryTagContextMixin:
    """Mixin to add categories and popular tags to context"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:10]
        return context

# Create your views here.

def home(request):
    """View function for the home page."""
    categories = Category.objects.all()
    popular_tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:10]
    context = {
        'categories': categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'myapp/home.html', context)

def switch_language(request, language_code):
    """
    Switch the language of the site
    """
    # Validate the language code
    if language_code in [lang[0] for lang in settings.LANGUAGES]:
        translation.activate(language_code)
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
        return response
    
    # If the language code is not valid, redirect to the previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class CustomLoginView(CategoryTagContextMixin, LoginView):
    """Custom login view."""
    template_name = 'myapp/login.html'
    form_class = AuthenticationForm
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')

class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = 'home'

class PostListView(CategoryTagContextMixin, generic.ListView):
    """View for listing all blog posts with pagination."""
    model = Post
    template_name = 'myapp/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the 10 most used tags
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('posts')).order_by('-num_posts')[:10]
        return context

class PostDetailView(CategoryTagContextMixin, generic.DetailView):
    """View for displaying a single blog post."""
    model = Post
    template_name = 'myapp/post_detail.html'
    
    def get_object(self, queryset=None):
        """Get the post object and increment view count."""
        obj = super().get_object(queryset)
        # Increment view count
        obj.increment_view_count()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        # Add related posts
        context['related_posts'] = self.object.get_related_posts()
        # Add categories and popular tags
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('posts')).order_by('-num_posts')[:10]
        return context
        
    def post(self, request, *args, **kwargs):
        """Handle comment submission directly from the post detail page."""
        self.object = self.get_object()
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = self.object
                comment.author = request.user
                comment.save()
                return redirect('post-detail', pk=self.object.pk)
        return self.get(request, *args, **kwargs)

class CategoryDetailView(CategoryTagContextMixin, generic.DetailView):
    """View for displaying posts in a category."""
    model = Category
    template_name = 'myapp/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get posts for this category with pagination
        category = self.get_object()
        posts_list = Post.objects.filter(category=category)
        paginator = Paginator(posts_list, 5)
        page = self.request.GET.get('page')
        posts = paginator.get_page(page)
        
        context['posts'] = posts
        return context

class TagDetailView(CategoryTagContextMixin, generic.DetailView):
    """View for displaying posts with a specific tag."""
    model = Tag
    template_name = 'myapp/tag_detail.html'
    context_object_name = 'tag'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get posts for this tag with pagination
        tag = self.get_object()
        posts_list = Post.objects.filter(tags=tag)
        paginator = Paginator(posts_list, 5)
        page = self.request.GET.get('page')
        posts = paginator.get_page(page)
        
        context['posts'] = posts
        return context

class AddCommentView(LoginRequiredMixin, CategoryTagContextMixin, generic.CreateView):
    """View for adding a comment to a post."""
    model = Comment
    form_class = CommentForm
    template_name = 'myapp/comment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        messages.success(self.request, 'Your comment has been added successfully!')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.kwargs['pk']})

class AuthorDetailView(CategoryTagContextMixin, generic.DetailView):
    """View for displaying author information."""
    model = User
    template_name = 'myapp/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.object).order_by('-created_date')
        # Add categories and popular tags
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('posts')).order_by('-num_posts')[:10]
        return context

class ProfileView(LoginRequiredMixin, CategoryTagContextMixin, generic.ListView):
    """View for displaying user profile."""
    template_name = 'myapp/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(author=self.request.user)
        context['liked_posts'] = Post.objects.filter(likes=self.request.user)
        return context

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, CategoryTagContextMixin, generic.UpdateView):
    """View for updating a comment."""
    model = Comment
    fields = ['content']
    template_name = 'myapp/comment_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your comment has been updated!')
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, CategoryTagContextMixin, generic.DeleteView):
    """View for deleting a comment."""
    model = Comment
    template_name = 'myapp/comment_confirm_delete.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, 'Your comment has been deleted!')
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class PostCreateView(LoginRequiredMixin, CategoryTagContextMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'myapp/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        
        # Check if a new category was created
        if form.cleaned_data.get('new_category'):
            messages.success(self.request, f"New category '{form.cleaned_data['new_category']}' was created!")
        
        # Check if new tags were created
        if form.cleaned_data.get('new_tags'):
            tag_count = len([t for t in form.cleaned_data['new_tags'].split(',') if t.strip()])
            if tag_count > 0:
                messages.success(self.request, f"{tag_count} new tag(s) were created!")
        
        messages.success(self.request, 'Your post has been created!')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, CategoryTagContextMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'myapp/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        
        # Check if a new category was created
        if form.cleaned_data.get('new_category'):
            messages.success(self.request, f"New category '{form.cleaned_data['new_category']}' was created!")
        
        # Check if new tags were created
        if form.cleaned_data.get('new_tags'):
            tag_count = len([t for t in form.cleaned_data['new_tags'].split(',') if t.strip()])
            if tag_count > 0:
                messages.success(self.request, f"{tag_count} new tag(s) were created!")
        
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, CategoryTagContextMixin, generic.DeleteView):
    model = Post
    template_name = 'myapp/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        messages.success(self.request, 'Your post has been deleted!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

def like_post(request, pk):
    """View function for liking/unliking a post."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to like posts.')
        return redirect('login')
        
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.info(request, 'You have unliked this post.')
    else:
        post.likes.add(request.user)
        messages.success(request, 'You have liked this post.')
    
    return redirect('post-detail', pk=pk)

class BloggerListView(CategoryTagContextMixin, generic.ListView):
    """View for displaying a list of bloggers."""
    model = User
    template_name = 'myapp/blogger_list.html'
    context_object_name = 'bloggers'
    paginate_by = 10

    def get_queryset(self):
        # Get only users who have created posts
        return User.objects.filter(post__isnull=False).distinct().order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add categories and popular tags
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('posts')).order_by('-num_posts')[:10]
        return context

class PostSearchView(CategoryTagContextMixin, generic.ListView):
    """View for searching and filtering blog posts."""
    model = Post
    template_name = 'myapp/post_search.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        form = PostSearchForm(self.request.GET)
        queryset = Post.objects.all()
        
        if form.is_valid():
            # Apply text search filter
            query = form.cleaned_data.get('query')
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | Q(content__icontains=query)
                )
            
            # Apply category filter
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
                
            # Apply tag filter
            tag = form.cleaned_data.get('tag')
            if tag:
                queryset = queryset.filter(tags=tag)
            
            # Apply date filter
            date_filter = form.cleaned_data.get('date_filter')
            if date_filter:
                today = timezone.now().date()
                if date_filter == 'today':
                    queryset = queryset.filter(created_date__date=today)
                elif date_filter == 'this_week':
                    week_start = today - timedelta(days=today.weekday())
                    queryset = queryset.filter(created_date__date__gte=week_start)
                elif date_filter == 'this_month':
                    queryset = queryset.filter(
                        created_date__year=today.year,
                        created_date__month=today.month
                    )
                elif date_filter == 'this_year':
                    queryset = queryset.filter(created_date__year=today.year)
            
            # Apply sorting
            sort_by = form.cleaned_data.get('sort_by')
            if sort_by:
                if sort_by == '-likes':
                    # For 'Most liked', we need to annotate with likes count
                    queryset = queryset.annotate(like_count=Count('likes')).order_by('-like_count')
                elif sort_by == '-view_count':
                    # For 'Most viewed', order by view_count
                    queryset = queryset.order_by('-view_count')
                else:
                    queryset = queryset.order_by(sort_by)
        else:
            # Default sorting if form is not valid
            queryset = queryset.order_by('-created_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PostSearchForm(self.request.GET or None)
        # Keep the query parameters for pagination
        if self.request.GET:
            query_params = self.request.GET.copy()
            if 'page' in query_params:
                del query_params['page']
            context['query_params'] = query_params.urlencode()
        
        # Add categories and popular tags
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('posts')).order_by('-num_posts')[:10]
        return context
