import os
import django
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assessment.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import Post

def create_sample_data():
    # Create authors
    authors = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'password123'
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'password': 'password123'
        }
    ]

    created_authors = []
    for author_data in authors:
        user = User.objects.create_user(
            username=author_data['username'],
            email=author_data['email'],
            first_name=author_data['first_name'],
            last_name=author_data['last_name'],
            password=author_data['password']
        )
        created_authors.append(user)
        print(f"Created author: {user.username}")

    # Sample blog posts
    posts = [
        {
            'title': 'Getting Started with Django',
            'content': '''Django is a high-level Python web framework that enables rapid development of secure and maintainable websites. 
            Built by experienced developers, it takes care of much of the hassle of web development, so you can focus on writing your app without needing to reinvent the wheel.''',
            'author': created_authors[0],
            'days_ago': 5
        },
        {
            'title': 'The Art of Blogging',
            'content': '''Blogging is an art form that combines writing, creativity, and technical skills. 
            A successful blog requires dedication, consistency, and a genuine passion for your subject matter.''',
            'author': created_authors[1],
            'days_ago': 4
        },
        {
            'title': 'Web Development Best Practices',
            'content': '''When developing web applications, following best practices is crucial for creating maintainable and scalable code. 
            This includes writing clean code, following security guidelines, and implementing proper testing.''',
            'author': created_authors[2],
            'days_ago': 3
        },
        {
            'title': 'Python Programming Tips',
            'content': '''Python is a versatile programming language known for its simplicity and readability. 
            Here are some tips to help you write better Python code and improve your programming skills.''',
            'author': created_authors[0],
            'days_ago': 2
        },
        {
            'title': 'The Future of Web Development',
            'content': '''The web development landscape is constantly evolving with new technologies and frameworks emerging regularly. 
            Staying up-to-date with the latest trends and tools is essential for modern web developers.''',
            'author': created_authors[1],
            'days_ago': 1
        }
    ]

    # Create posts
    for post_data in posts:
        post = Post.objects.create(
            title=post_data['title'],
            content=post_data['content'],
            author=post_data['author'],
            created_date=datetime.now() - timedelta(days=post_data['days_ago'])
        )
        print(f"Created post: {post.title} by {post.author.username}")

if __name__ == '__main__':
    create_sample_data() 