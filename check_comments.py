import os
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assessment.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import Post, Comment

def check_and_add_comments():
    # Check existing comments
    comments = Comment.objects.all()
    print(f"Found {comments.count()} comments in the database:")
    
    for comment in comments:
        print(f"- Comment by {comment.author.username} on post '{comment.post.title}'")
    
    # If there are no comments, add some
    if comments.count() == 0:
        print("\nNo comments found. Adding sample comments...")
        
        # Get users
        users = User.objects.all()
        if users.count() < 3:
            print("Not enough users. Creating additional users...")
            sample_users = [
                {'username': 'alice', 'password': 'password123', 'email': 'alice@example.com'},
                {'username': 'bob', 'password': 'password123', 'email': 'bob@example.com'},
                {'username': 'charlie', 'password': 'password123', 'email': 'charlie@example.com'}
            ]
            
            for user_data in sample_users:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={'email': user_data['email']}
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    print(f"Created user: {user.username}")
        
        # Get posts
        posts = Post.objects.all()
        if posts.count() == 0:
            print("No posts found. Cannot add comments without posts.")
            return
        
        # Add sample comments to all posts
        users = User.objects.all()[:3]  # Get first three users
        sample_comments = [
            "This is a great post! Thanks for sharing.",
            "I found this information very helpful.",
            "Interesting perspective on this topic.",
            "Looking forward to more posts like this.",
            "This helped me understand the concept better."
        ]
        
        for post in posts:
            for i, user in enumerate(users):
                comment = Comment.objects.create(
                    post=post,
                    author=user,
                    content=sample_comments[i % len(sample_comments)]
                )
                print(f"Added comment by {user.username} to post '{post.title}'")

if __name__ == "__main__":
    check_and_add_comments() 