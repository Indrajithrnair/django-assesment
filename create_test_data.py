import os
import django
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assessment.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import Post, Comment

def create_test_data():
    # Create test users
    users = [
        {
            'username': 'alice',
            'email': 'alice@example.com',
            'first_name': 'Alice',
            'last_name': 'Wonderland',
            'password': 'password123'
        },
        {
            'username': 'bob',
            'email': 'bob@example.com',
            'first_name': 'Bob',
            'last_name': 'Builder',
            'password': 'password123'
        },
        {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'first_name': 'Charlie',
            'last_name': 'Brown',
            'password': 'password123'
        }
    ]

    created_users = []
    for user_data in users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': user_data['password']
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Created user: {user.username}")
        created_users.append(user)

    # Add comments to existing posts
    posts = Post.objects.all()
    comments = [
        {
            'content': 'Great post! Really enjoyed reading it.',
            'author': created_users[0],
            'post': posts[0],
            'days_ago': 2
        },
        {
            'content': 'Thanks for sharing this information.',
            'author': created_users[1],
            'post': posts[1],
            'days_ago': 1
        },
        {
            'content': 'I found this post very helpful.',
            'author': created_users[2],
            'post': posts[2],
            'days_ago': 3
        }
    ]

    for comment_data in comments:
        comment = Comment.objects.create(
            content=comment_data['content'],
            author=comment_data['author'],
            post=comment_data['post'],
            created_date=datetime.now() - timedelta(days=comment_data['days_ago'])
        )
        print(f"Created comment by {comment.author.username} on post '{comment.post.title}'")

if __name__ == '__main__':
    create_test_data() 