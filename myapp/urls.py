from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.home, name='blog-home'),
    path('blog/blogs/', views.PostListView.as_view(), name='post-list'),
    path('blog/search/', views.PostSearchView.as_view(), name='post-search'),
    path('blog/categories/', views.CategoryListView.as_view(), name='category-list'),
    path('blog/category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('blog/tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('blog/bloggers/', views.BloggerListView.as_view(), name='blogger-list'),
    path('blog/post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('blog/post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('blog/post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('blog/post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('blog/post/<int:pk>/like/', views.like_post, name='like_post'),
    path('blog/<int:pk>/create/', views.AddCommentView.as_view(), name='add-comment'),
    path('blog/author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
] 