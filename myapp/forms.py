from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Comment, Post, Category, Tag
from django.utils.text import slugify

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'}),
        }

class PostForm(forms.ModelForm):
    # Add fields for creating new category and tags
    new_category = forms.CharField(
        required=False,
        help_text="Create a new category if it doesn't exist",
        widget=forms.TextInput(attrs={'placeholder': 'Create a new category'})
    )
    
    new_tags = forms.CharField(
        required=False,
        help_text="Add new tags separated by commas",
        widget=forms.TextInput(attrs={'placeholder': 'Add new tags separated by commas'})
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter post title', 'class': 'form-control'}),
            'content': forms.Textarea(attrs={'placeholder': 'Write your post here...', 'rows': 10, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Create new category...')]),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control select2-tags'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty option to category field
        self.fields['category'].required = False
        self.fields['category'].empty_label = "Create new category..."
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle new category if provided
        if self.cleaned_data['new_category']:
            category_name = self.cleaned_data['new_category'].strip()
            category_slug = slugify(category_name)
            category, created = Category.objects.get_or_create(
                name=category_name, 
                defaults={'slug': category_slug}
            )
            instance.category = category
        
        if commit:
            instance.save()
            
            # Handle existing tags from the form
            self.save_m2m()
            
            # Handle new tags from the new_tags field
            if self.cleaned_data['new_tags']:
                tag_names = [name.strip() for name in self.cleaned_data['new_tags'].split(',') if name.strip()]
                for tag_name in tag_names:
                    tag_slug = slugify(tag_name)
                    tag, created = Tag.objects.get_or_create(name=tag_name, defaults={'slug': tag_slug})
                    instance.tags.add(tag)
        
        return instance

class PostSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search in title and content...', 'class': 'search-input'})
    )
    
    # Filter by category
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        label='Category',
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    
    # Filter by tag
    tag = forms.ModelChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        label='Tag',
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    
    # Filter by date
    date_choices = [
        ('', 'Any time'),
        ('today', 'Today'),
        ('this_week', 'This week'),
        ('this_month', 'This month'),
        ('this_year', 'This year'),
    ]
    date_filter = forms.ChoiceField(
        required=False,
        choices=date_choices,
        label='Posted',
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    
    # Sort options
    sort_choices = [
        ('-created_date', 'Newest first'),
        ('created_date', 'Oldest first'),
        ('-likes', 'Most liked'),
        ('-view_count', 'Most viewed'),
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
    ]
    sort_by = forms.ChoiceField(
        required=False,
        choices=sort_choices,
        label='Sort by',
        initial='-created_date',
        widget=forms.Select(attrs={'class': 'filter-select'})
    )

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text=_('Optional'))
    last_name = forms.CharField(max_length=30, required=False, help_text=_('Optional'))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and CSS classes to the fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Choose a username')
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Enter your email address')
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Enter your first name (optional)')
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Enter your last name (optional)')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Enter a password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Confirm your password')
        }) 