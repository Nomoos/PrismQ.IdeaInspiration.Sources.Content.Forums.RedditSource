# Quick Start: Loading Data from Reddit API

## Is Reddit API Free? 💰

**Yes, Reddit API is FREE** with the following conditions:
- ✅ Free for personal and commercial use
- ✅ 60 requests per minute (authenticated)
- ✅ No cost for API access
- ✅ Unlimited data collection within rate limits

**No credit card required, no paid tiers.**

---

## How to Load Data (5-Minute Setup)

### Step 1: Register Your App (2 minutes)

1. Go to: https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Fill in:
   - **Name**: MyRedditApp
   - **App type**: Select "script"
   - **Redirect URI**: http://localhost:8080
4. Click "create app"
5. Note your **client_id** (under app name) and **client_secret**

### Step 2: Install PRAW (1 minute)

```bash
pip install praw
```

### Step 3: Load Data (2 minutes)

```python
import praw

# Initialize Reddit API
reddit = praw.Reddit(
    client_id="your_client_id_here",
    client_secret="your_client_secret_here",
    user_agent="MyApp/1.0 by /u/yourusername"
)

# Load posts from any subreddit
subreddit = reddit.subreddit('python')

# Get top posts
for post in subreddit.top(limit=10):
    print(f"Title: {post.title}")
    print(f"Score: {post.score}")
    print(f"Comments: {post.num_comments}")
    print(f"URL: {post.url}")
    print()
```

**That's it! You're now loading data from Reddit API.**

---

## What Data Do You Get? 📊

### Post Data (20+ Fields)

```python
post = reddit.submission(id='example123')

# Basic Info
post.id                  # Unique ID
post.title               # Post title
post.selftext           # Post content (for text posts)
post.url                # URL (for link posts)
post.permalink          # Reddit URL

# Author Info
post.author             # Username (or None if deleted)
post.author_flair_text  # Author's flair

# Timestamps
post.created_utc        # Creation time (Unix timestamp)
post.edited             # Edit time (or False)

# Engagement Metrics
post.score              # Net score (upvotes - downvotes)
post.upvote_ratio       # Ratio of upvotes (0.0 to 1.0)
post.num_comments       # Number of comments
post.gilded             # Number of awards

# Categorization
post.subreddit          # Subreddit name
post.link_flair_text    # Post flair/category

# Flags
post.is_self            # True if text post
post.over_18            # True if NSFW
post.stickied           # True if pinned
post.locked             # True if locked
post.spoiler            # True if marked spoiler
```

### Comment Data

```python
# Get all comments from a post
submission = reddit.submission(id='example123')
submission.comments.replace_more(limit=0)

for comment in submission.comments.list():
    print(comment.body)        # Comment text
    print(comment.author)      # Comment author
    print(comment.score)       # Comment score
    print(comment.created_utc) # When posted
    print(comment.depth)       # Nesting level
    print(comment.parent_id)   # Parent comment/post
```

### Subreddit Data

```python
subreddit = reddit.subreddit('python')

subreddit.display_name      # Subreddit name
subreddit.subscribers       # Number of subscribers
subreddit.active_user_count # Current active users
subreddit.description       # Subreddit description
subreddit.created_utc       # When created
```

### User Data

```python
user = reddit.redditor('username')

user.link_karma        # Post karma
user.comment_karma     # Comment karma
user.created_utc       # Account creation date
user.is_gold           # Has Reddit Premium
```

---

## Complete Example: Load Top Posts

```python
import praw
from datetime import datetime

# Initialize
reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="DataCollector/1.0 by /u/yourusername"
)

# Load top posts from r/python
subreddit = reddit.subreddit('python')

print("Top 20 Posts from r/python:\n")

for i, post in enumerate(subreddit.top(time_filter='week', limit=20), 1):
    # Extract all available data
    post_data = {
        'rank': i,
        'title': post.title,
        'score': post.score,
        'upvote_ratio': post.upvote_ratio,
        'num_comments': post.num_comments,
        'author': str(post.author),
        'created': datetime.fromtimestamp(post.created_utc),
        'url': f"https://reddit.com{post.permalink}",
        'flair': post.link_flair_text,
        'is_video': post.is_video,
        'domain': post.domain,
    }
    
    # Display
    print(f"{i}. {post_data['title'][:60]}...")
    print(f"   Score: {post_data['score']:,} | Comments: {post_data['num_comments']:,}")
    print(f"   Upvote Ratio: {post_data['upvote_ratio']:.1%}")
    print(f"   Author: u/{post_data['author']}")
    print(f"   Posted: {post_data['created']}")
    print(f"   Flair: {post_data['flair']}")
    print(f"   URL: {post_data['url']}")
    print()
```

**Output Example:**
```
Top 20 Posts from r/python:

1. Python 3.13 is now available...
   Score: 15,234 | Comments: 987
   Upvote Ratio: 98.5%
   Author: u/pythondev
   Posted: 2025-10-20 14:23:45
   Flair: News
   URL: https://reddit.com/r/python/comments/abc123

2. I built a CLI tool to automate data scraping...
   Score: 8,567 | Comments: 423
   Upvote Ratio: 96.2%
   Author: u/developer123
   Posted: 2025-10-19 09:15:22
   Flair: Projects
   URL: https://reddit.com/r/python/comments/def456
...
```

---

## Data Collection Methods

### 1. Hot Posts (Most Popular Right Now)
```python
for post in subreddit.hot(limit=100):
    print(post.title)
```

### 2. New Posts (Latest)
```python
for post in subreddit.new(limit=100):
    print(post.title)
```

### 3. Top Posts (Highest Scored)
```python
# time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
for post in subreddit.top(time_filter='week', limit=100):
    print(post.title)
```

### 4. Rising Posts (Trending)
```python
for post in subreddit.rising(limit=100):
    print(post.title)
```

### 5. Search Posts
```python
for post in subreddit.search('machine learning', limit=100):
    print(post.title)
```

### 6. Real-Time Streaming
```python
# Get new posts as they're created
for post in subreddit.stream.submissions():
    print(f"New post: {post.title}")
```

---

## Rate Limits & Costs

### Free Tier (Default)
- ✅ **60 requests per minute** (authenticated)
- ✅ **10 requests per minute** (unauthenticated)
- ✅ Unlimited total requests
- ✅ No cost whatsoever

### What Counts as 1 Request?
- Getting 100 posts = 1 request
- Getting 1 post = 1 request
- Getting comments from 1 post = 1 request
- Getting subreddit info = 1 request

### Example: How Much Can You Get?
**In 1 minute (60 requests):**
- 6,000 posts (60 requests × 100 posts each)
- Or 60 posts with all their comments
- Or mix of posts, comments, and subreddit data

**In 1 hour:**
- 360,000 posts
- Plenty for most use cases!

**No costs, no limits on total data.**

---

## Saving Data to Files

### Save to JSON
```python
import json

posts_data = []
for post in subreddit.top(limit=100):
    posts_data.append({
        'title': post.title,
        'score': post.score,
        'url': post.url,
        'created': post.created_utc,
    })

# Save to file
with open('reddit_posts.json', 'w') as f:
    json.dump(posts_data, f, indent=2)
```

### Save to CSV
```python
import csv

with open('reddit_posts.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Score', 'Comments', 'URL'])
    
    for post in subreddit.top(limit=100):
        writer.writerow([
            post.title,
            post.score,
            post.num_comments,
            post.url
        ])
```

---

## Common Use Cases

### 1. Track Trending Topics
```python
from collections import Counter

# Get keywords from top posts
words = []
for post in subreddit.top(limit=100):
    words.extend(post.title.lower().split())

# Most common words
common = Counter(words).most_common(10)
print("Trending keywords:", common)
```

### 2. Sentiment Analysis
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

for post in subreddit.top(limit=50):
    sentiment = analyzer.polarity_scores(post.title)
    print(f"{post.title}: {sentiment['compound']}")
```

### 3. Monitor New Posts
```python
# Monitor for specific keywords
keywords = ['python', 'data science', 'machine learning']

for post in subreddit.stream.submissions():
    if any(kw in post.title.lower() for kw in keywords):
        print(f"MATCH: {post.title}")
        print(f"URL: https://reddit.com{post.permalink}")
```

---

## Full Data Fields Reference

Here's **every field** you can access from a post:

```python
# Content
post.title                    # Post title
post.selftext                # Text content (self posts)
post.url                     # External URL (link posts)
post.permalink               # Reddit permalink
post.shortlink               # Short Reddit link

# Author
post.author                  # Author username (or None)
post.author_flair_text       # Author flair
post.author_flair_css_class  # Author flair CSS

# Metadata
post.id                      # Unique ID
post.name                    # Full ID (t3_xyz)
post.subreddit               # Subreddit object
post.subreddit_name_prefixed # r/subreddit

# Timestamps
post.created                 # Creation time (local)
post.created_utc             # Creation time (UTC)
post.edited                  # Edit time or False

# Engagement
post.score                   # Net score
post.upvote_ratio            # Upvote ratio (0-1)
post.num_comments            # Comment count
post.num_crossposts          # Crosspost count
post.view_count              # View count (if available)

# Awards
post.gilded                  # Gold awards count
post.all_awardings           # All award details
post.total_awards_received   # Total awards

# Flags
post.is_self                 # Text post
post.is_video                # Video post
post.is_original_content     # Marked as OC
post.over_18                 # NSFW
post.spoiler                 # Spoiler
post.stickied                # Pinned
post.locked                  # Locked
post.archived                # Archived
post.hidden                  # Hidden
post.saved                   # Saved (by you)
post.clicked                 # Clicked (by you)

# Flair
post.link_flair_text         # Post flair
post.link_flair_css_class    # Flair CSS class
post.link_flair_richtext     # Rich flair data

# Media
post.thumbnail               # Thumbnail URL
post.media                   # Media metadata
post.media_embed             # Embed metadata
post.secure_media            # Secure media
post.preview                 # Preview images

# Domain
post.domain                  # Link domain
post.is_reddit_media_domain  # Is Reddit hosted

# Moderation
post.approved_by             # Moderator who approved
post.banned_by               # Moderator who removed
post.removal_reason          # Removal reason
post.report_reasons          # Report reasons
post.num_reports             # Number of reports

# And more...
```

**Total: 60+ data fields per post!**

---

## FAQ

### Q: Do I need to pay?
**A: No, Reddit API is completely free.**

### Q: What are the limits?
**A: 60 requests/minute when authenticated. No total limit.**

### Q: Can I use it for commercial projects?
**A: Yes, free for personal and commercial use.**

### Q: What if I need more than 60 req/min?
**A: Use multiple API keys, or batch your requests (get 100 posts per request).**

### Q: Is web scraping better?
**A: No. Web scraping violates Reddit ToS, is unreliable, and gives you less data.**

### Q: How do I get my API credentials?
**A: Register at https://www.reddit.com/prefs/apps (takes 2 minutes, free)**

### Q: Can I get historical data?
**A: Yes, use Pushshift API (third-party, also free) for historical data.**

### Q: What programming languages are supported?
**A: Python (PRAW), JavaScript (Snoowrap), Java (JRAW), C# (Reddit.NET), Ruby, Go, and more.**

---

## Next Steps

1. **Get Started**: See `GETTING_STARTED.md` for detailed setup
2. **Code Examples**: See `examples.py` for production-ready code
3. **Quick Reference**: See `QUICK_REFERENCE.md` for common tasks
4. **Best Practices**: See `REDDIT_SCRAPING_BEST_PRACTICES.md` for comprehensive guide

---

## Summary

✅ **Reddit API is FREE**
- No cost, no credit card
- 60 requests/minute
- Unlimited total data

✅ **Rich Data Available**
- 60+ fields per post
- Complete comment trees
- User and subreddit info
- Real-time streaming

✅ **Easy to Use**
- 5-minute setup
- Simple Python code
- Excellent documentation

**Start now:** https://www.reddit.com/prefs/apps

---

**Last Updated:** October 2025  
**Version:** 1.0
