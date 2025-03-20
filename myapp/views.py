from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Post, Comment
from .forms import CommentForm
from django.contrib.auth.models import User

# Create your views here.

def home(request):
    """View function for the home page."""
    return render(request, 'myapp/home.html')

class CustomLoginView(LoginView):
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

class PostListView(generic.ListView):
    """View for listing all blog posts with pagination."""
    model = Post
    template_name = 'myapp/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

class PostDetailView(generic.DetailView):
    """View for displaying a single blog post."""
    model = Post
    template_name = 'myapp/post_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
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

class AddCommentView(LoginRequiredMixin, generic.CreateView):
    """View for adding a comment to a blog post."""
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

class AuthorDetailView(generic.DetailView):
    """View for displaying author information."""
    model = User
    template_name = 'myapp/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.object).order_by('-created_date')
        return context

class ProfileView(LoginRequiredMixin, generic.ListView):
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

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
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

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Comment
    template_name = 'myapp/comment_confirm_delete.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, 'Your comment has been deleted!')
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'myapp/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been created!')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'myapp/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
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

class BloggerListView(generic.ListView):
    model = User
    template_name = 'myapp/blogger_list.html'
    context_object_name = 'bloggers'
    paginate_by = 10

    def get_queryset(self):
        # Get only users who have created posts
        return User.objects.filter(post__isnull=False).distinct().order_by('username')
