import os
import django
from datetime import datetime, timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assessment.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import Post, Comment

def add_more_comments():
    # Get all posts
    posts = Post.objects.all()
    if not posts:
        print("No posts found. Cannot add comments.")
        return
    
    # Get or create users
    user_data = [
        {'username': 'testuser1', 'password': 'password123', 'email': 'test1@example.com'},
        {'username': 'testuser2', 'password': 'password123', 'email': 'test2@example.com'},
        {'username': 'testuser3', 'password': 'password123', 'email': 'test3@example.com'},
    ]
    
    users = []
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={'email': data['email']}
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"Created user: {user.username}")
        users.append(user)
    
    # Sample comments
    comment_texts = [
        "Great article, I really enjoyed reading it!",
        "This information is very helpful. Thank you for sharing.",
        "I have a question about this topic. Can you elaborate more on it?",
        "This is exactly what I was looking for. Thanks!",
        "Very well written and informative.",
        "I disagree with some points, but overall a good article.",
        "Looking forward to more content like this.",
        "This helped me understand the topic better.",
        "I've shared this with my colleagues. Very useful!",
        "Could you recommend any additional resources on this topic?"
    ]
    
    # Add 3-5 comments to each post
    for post in posts:
        # Check if post already has comments
        existing_comments = Comment.objects.filter(post=post).count()
        print(f"Post '{post.title}' has {existing_comments} existing comments.")
        
        # Add 3-5 new comments if it has less than 3
        if existing_comments < 3:
            num_comments = random.randint(3, 5)
            for i in range(num_comments):
                user = random.choice(users)
                # Create comment with a random date in the past 30 days
                days_ago = random.randint(0, 30)
                comment = Comment.objects.create(
                    post=post,
                    author=user,
                    content=random.choice(comment_texts),
                    created_date=datetime.now() - timedelta(days=days_ago)
                )
                print(f"Added comment by {user.username} to post '{post.title}'")

if __name__ == "__main__":
    add_more_comments() 