# Reddit Scraping Quick Reference

Quick reference for common Reddit data collection tasks.

## Table of Contents
- [Authentication](#authentication)
- [Collecting Posts](#collecting-posts)
- [Collecting Comments](#collecting-comments)
- [Rate Limiting](#rate-limiting)
- [Common Filters](#common-filters)
- [Error Handling](#error-handling)
- [Useful Attributes](#useful-attributes)

---

## Authentication

### Basic Authentication
```python
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="AppName/1.0 by /u/username"
)
```

### Read-Only Access (No Credentials)
```python
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="AppName/1.0"
)
```

---

## Collecting Posts

### Hot Posts
```python
subreddit = reddit.subreddit('python')
for post in subreddit.hot(limit=25):
    print(post.title)
```

### New Posts
```python
for post in subreddit.new(limit=25):
    print(post.title)
```

### Top Posts
```python
# Time filters: 'hour', 'day', 'week', 'month', 'year', 'all'
for post in subreddit.top(time_filter='week', limit=25):
    print(post.title)
```

### Rising Posts
```python
for post in subreddit.rising(limit=25):
    print(post.title)
```

### Multiple Subreddits
```python
# Use + to combine subreddits
multi = reddit.subreddit('python+javascript+programming')
for post in multi.hot(limit=25):
    print(f"[{post.subreddit}] {post.title}")
```

### From r/all
```python
for post in reddit.subreddit('all').hot(limit=25):
    print(post.title)
```

---

## Collecting Comments

### All Comments (Flattened)
```python
submission = reddit.submission(id='abc123')
submission.comments.replace_more(limit=0)  # Remove "load more" objects

for comment in submission.comments.list():
    print(f"{comment.author}: {comment.body}")
```

### Top-Level Comments Only
```python
submission = reddit.submission(id='abc123')

for comment in submission.comments:
    if hasattr(comment, 'body'):  # Skip MoreComments objects
        print(f"{comment.author}: {comment.body}")
```

### Comments with Replies
```python
submission = reddit.submission(id='abc123')

def print_comment_tree(comment, depth=0):
    indent = "  " * depth
    print(f"{indent}{comment.author}: {comment.body[:50]}")
    
    for reply in comment.replies:
        if hasattr(reply, 'body'):
            print_comment_tree(reply, depth + 1)

for comment in submission.comments:
    if hasattr(comment, 'body'):
        print_comment_tree(comment)
```

---

## Rate Limiting

### Check Rate Limit Status
```python
# After making a request, check headers
import prawcore

try:
    response = reddit.subreddit('python').hot(limit=1)
    # Access rate limit info from the last request
    print(f"Remaining: {reddit.auth.limits['remaining']}")
    print(f"Used: {reddit.auth.limits['used']}")
    print(f"Reset: {reddit.auth.limits['reset_timestamp']}")
except Exception as e:
    print(f"Error: {e}")
```

### Simple Rate Limiter
```python
import time

def rate_limited_request(func, *args, **kwargs):
    """Execute function with 1 second delay"""
    result = func(*args, **kwargs)
    time.sleep(1)  # 1 request per second = 60 per minute
    return result

# Usage
posts = rate_limited_request(reddit.subreddit('python').hot, limit=10)
```

---

## Common Filters

### Filter by Flair
```python
# Get all posts with specific flair
subreddit = reddit.subreddit('python')
for post in subreddit.search('flair:"Discussion"', limit=25):
    print(post.title)
```

### Filter by Score
```python
for post in subreddit.hot(limit=100):
    if post.score > 100:
        print(f"{post.title} - Score: {post.score}")
```

### Filter by Time
```python
from datetime import datetime, timedelta

cutoff_time = datetime.now().timestamp() - (24 * 3600)  # Last 24 hours

for post in subreddit.new(limit=100):
    if post.created_utc > cutoff_time:
        print(post.title)
```

### Filter by Keywords (Search)
```python
# Search within subreddit
for post in subreddit.search('machine learning', limit=25):
    print(post.title)

# Search with time filter
for post in subreddit.search('AI', time_filter='week', limit=25):
    print(post.title)
```

### Filter NSFW Content
```python
for post in subreddit.hot(limit=100):
    if not post.over_18:  # Filter out NSFW
        print(post.title)
```

---

## Error Handling

### Basic Try-Catch
```python
import prawcore

try:
    post = reddit.submission(id='abc123')
    print(post.title)
except prawcore.exceptions.NotFound:
    print("Post not found")
except prawcore.exceptions.Forbidden:
    print("Access forbidden")
except prawcore.exceptions.ServerError:
    print("Reddit server error")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Rate Limit Handling
```python
import time
import prawcore

def safe_request(func, *args, **kwargs):
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except prawcore.exceptions.TooManyRequests as e:
            wait_time = 60  # Wait 1 minute
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except prawcore.exceptions.ServerError:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Server error. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")

# Usage
posts = safe_request(reddit.subreddit('python').hot, limit=10)
```

---

## Useful Attributes

### Submission (Post) Attributes
```python
submission = reddit.submission(id='abc123')

# Basic info
submission.id              # Post ID
submission.title           # Post title
submission.selftext        # Text content (for self posts)
submission.url             # URL (for link posts)
submission.permalink       # Reddit permalink

# Metadata
submission.author          # Author username (or None if deleted)
submission.subreddit       # Subreddit object
submission.created_utc     # Creation timestamp
submission.edited          # Edit timestamp (or False)

# Engagement
submission.score           # Net score (upvotes - downvotes)
submission.upvote_ratio    # Ratio of upvotes (0.0 to 1.0)
submission.num_comments    # Number of comments

# Flags
submission.is_self         # True if text post
submission.stickied        # True if pinned
submission.over_18         # True if NSFW
submission.spoiler         # True if marked as spoiler
submission.locked          # True if locked

# Flair
submission.link_flair_text # Post flair text
submission.link_flair_css_class  # Flair CSS class

# Awards
submission.gilded          # Number of Reddit Gold awards
submission.all_awardings   # List of all award types
```

### Comment Attributes
```python
comment = reddit.comment(id='xyz789')

# Basic info
comment.id                 # Comment ID
comment.body               # Comment text
comment.author             # Author username (or None)
comment.permalink          # Comment permalink

# Engagement
comment.score              # Comment score
comment.controversiality   # Controversy score (0 or 1)

# Structure
comment.parent_id          # Parent comment/post ID
comment.depth              # Nesting depth
comment.replies            # RepliesForest object

# Flags
comment.is_submitter       # True if comment by post author
comment.stickied           # True if pinned
comment.edited             # Edit timestamp (or False)

# Awards
comment.gilded             # Number of awards
```

### Subreddit Attributes
```python
subreddit = reddit.subreddit('python')

# Basic info
subreddit.display_name     # Subreddit name
subreddit.title            # Subreddit title
subreddit.public_description  # Short description
subreddit.description      # Full description (markdown)

# Statistics
subreddit.subscribers      # Number of subscribers
subreddit.active_user_count  # Current active users

# Metadata
subreddit.created_utc      # Creation timestamp
subreddit.over18           # True if NSFW
```

---

## Common Patterns

### Get Submission by URL
```python
url = "https://reddit.com/r/python/comments/abc123/title"
submission = reddit.submission(url=url)
```

### Get User's Posts
```python
user = reddit.redditor('username')
for post in user.submissions.new(limit=10):
    print(post.title)
```

### Get User's Comments
```python
user = reddit.redditor('username')
for comment in user.comments.new(limit=10):
    print(comment.body)
```

### Stream New Posts (Real-time)
```python
subreddit = reddit.subreddit('python')
for post in subreddit.stream.submissions():
    print(f"New post: {post.title}")
```

### Stream New Comments (Real-time)
```python
subreddit = reddit.subreddit('python')
for comment in subreddit.stream.comments():
    print(f"New comment: {comment.body[:50]}")
```

---

## Pagination

### Manual Pagination (Before/After)
```python
subreddit = reddit.subreddit('python')
after = None

for page in range(3):  # Get 3 pages
    posts = list(subreddit.hot(limit=25, params={'after': after}))
    
    for post in posts:
        print(post.title)
    
    if posts:
        after = posts[-1].fullname  # fullname format: t3_abc123
    else:
        break
```

### Get All Available Posts
```python
subreddit = reddit.subreddit('python')
all_posts = []

for post in subreddit.hot(limit=None):  # limit=None gets all available
    all_posts.append(post)
    if len(all_posts) >= 1000:  # Reddit limit
        break

print(f"Collected {len(all_posts)} posts")
```

---

## Data Export

### Export to CSV
```python
import csv

posts = reddit.subreddit('python').hot(limit=100)

with open('reddit_posts.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Title', 'Score', 'Comments', 'URL'])
    
    for post in posts:
        writer.writerow([
            post.id,
            post.title,
            post.score,
            post.num_comments,
            post.permalink
        ])
```

### Export to JSON
```python
import json

posts = reddit.subreddit('python').hot(limit=100)

data = []
for post in posts:
    data.append({
        'id': post.id,
        'title': post.title,
        'score': post.score,
        'num_comments': post.num_comments,
        'url': post.permalink
    })

with open('reddit_posts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
```

---

## Tips and Tricks

### Check if Subreddit Exists
```python
try:
    subreddit = reddit.subreddit('python')
    _ = subreddit.id  # Trigger API call
    print("Subreddit exists")
except prawcore.exceptions.NotFound:
    print("Subreddit not found")
```

### Get Random Post
```python
subreddit = reddit.subreddit('python')
random_post = subreddit.random()
print(random_post.title)
```

### Check if User Exists
```python
try:
    user = reddit.redditor('username')
    _ = user.id  # Trigger API call
    print(f"User exists. Karma: {user.link_karma + user.comment_karma}")
except prawcore.exceptions.NotFound:
    print("User not found")
```

### Get Subreddit Rules
```python
subreddit = reddit.subreddit('python')
for rule in subreddit.rules:
    print(f"{rule.short_name}: {rule.description}")
```

---

For more detailed information, see:
- [Best Practices Guide](./REDDIT_SCRAPING_BEST_PRACTICES.md)
- [Getting Started Guide](./GETTING_STARTED.md)
- [PRAW Documentation](https://praw.readthedocs.io/)
