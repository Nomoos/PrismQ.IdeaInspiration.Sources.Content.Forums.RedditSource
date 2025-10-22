# Reddit Scraping Best Practices

## Table of Contents
1. [Overview](#overview)
2. [API vs Web Scraping](#api-vs-web-scraping)
3. [Authentication and Rate Limiting](#authentication-and-rate-limiting)
4. [Data Extraction Patterns](#data-extraction-patterns)
5. [Post Metadata Collection](#post-metadata-collection)
6. [Engagement Metrics](#engagement-metrics)
7. [Comment Analysis](#comment-analysis)
8. [Trending Topics and Subreddits](#trending-topics-and-subreddits)
9. [Community Sentiment Analysis](#community-sentiment-analysis)
10. [Legal and Ethical Considerations](#legal-and-ethical-considerations)
11. [Implementation Recommendations](#implementation-recommendations)

---

## Overview

Reddit is one of the largest social media platforms with rich community-driven content. This document outlines best practices for collecting and analyzing Reddit data for idea inspiration and content sources.

### Key Data Points to Capture
- Post metadata (title, content, subreddit, author)
- Engagement metrics (upvotes, comments, awards)
- Comment threads and discussions
- Trending subreddits and topics
- Community sentiment and reactions

---

## API vs Web Scraping

### Reddit Official API (Recommended)

**Advantages:**
- Official and supported by Reddit
- Structured JSON responses
- No HTML parsing required
- More stable and reliable
- Clear rate limits and documentation

**API Endpoints:**
- `https://oauth.reddit.com` - OAuth2 authenticated API
- `https://www.reddit.com/.json` - Public JSON feeds (limited)

**Best Practice:** Always prefer the official Reddit API over web scraping.

### Web Scraping (Fallback)

Only consider web scraping when:
- API rate limits are exhausted
- Historical data not available via API
- Specific data points not exposed via API

**Risks:**
- Violates Reddit's Terms of Service
- Subject to anti-scraping measures
- HTML structure changes frequently
- May result in IP bans

---

## Authentication and Rate Limiting

### OAuth2 Authentication

Reddit requires OAuth2 authentication for most API operations.

**Steps:**
1. Register application at https://www.reddit.com/prefs/apps
2. Obtain client ID and client secret
3. Choose appropriate OAuth2 flow:
   - **Script application**: For personal use, single user
   - **Web application**: For web services with multiple users
   - **Installed application**: For mobile/desktop apps

**Authentication Example (Python):**
```python
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="YourApp/1.0 by /u/yourusername",
    username="your_username",  # Optional for read-only
    password="your_password"   # Optional for read-only
)
```

### Rate Limiting Best Practices

**Official API Rate Limits:**
- 60 requests per minute for OAuth authenticated requests
- 10 requests per minute for unauthenticated requests
- Rate limits are per OAuth client

**Implementation Strategies:**

1. **Respect Rate Limits:**
```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=60, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        # Remove old requests outside time window
        self.requests = [req for req in self.requests 
                        if now - req < timedelta(seconds=self.time_window)]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = (self.requests[0] + 
                         timedelta(seconds=self.time_window) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time + 0.1)
        
        self.requests.append(now)
```

2. **Implement Exponential Backoff:**
```python
import time
import random

def exponential_backoff(attempt, base_delay=1, max_delay=60):
    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
    time.sleep(delay)
```

3. **Monitor Rate Limit Headers:**
```python
# Check response headers
# X-Ratelimit-Remaining: requests remaining
# X-Ratelimit-Reset: epoch time when limit resets
# X-Ratelimit-Used: requests used
```

4. **Use Batch Operations:**
- Request multiple items in single API call when possible
- Use subreddit multireddit feature: `/r/sub1+sub2+sub3`

---

## Data Extraction Patterns

### Pagination

Reddit uses two pagination methods:

**1. Listing Pagination (Before/After):**
```python
# Get next page
after_token = None
all_posts = []

while True:
    params = {'limit': 100, 'after': after_token}
    response = reddit.subreddit('python').hot(limit=100, params=params)
    posts = list(response)
    
    if not posts:
        break
    
    all_posts.extend(posts)
    after_token = posts[-1].fullname
```

**2. Time-based Pagination:**
```python
import time

end_time = int(time.time())
start_time = end_time - (7 * 24 * 60 * 60)  # Last 7 days

# Using Pushshift API (third-party)
params = {
    'subreddit': 'python',
    'after': start_time,
    'before': end_time,
    'size': 100
}
```

### Data Freshness

**Strategies:**
1. **Streaming approach**: Monitor new posts in real-time
2. **Polling approach**: Fetch new content at regular intervals
3. **Historical approach**: Collect historical data once, then incremental updates

**Real-time Streaming Example:**
```python
def stream_submissions(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in subreddit.stream.submissions(skip_existing=True):
        process_submission(submission)
```

---

## Post Metadata Collection

### Essential Post Attributes

**Basic Metadata:**
```python
post_data = {
    'id': submission.id,
    'title': submission.title,
    'selftext': submission.selftext,  # Text content for self posts
    'url': submission.url,            # External URL for link posts
    'permalink': submission.permalink, # Reddit URL
    'subreddit': submission.subreddit.display_name,
    'author': str(submission.author) if submission.author else '[deleted]',
    'created_utc': submission.created_utc,
    'edited': submission.edited,      # False or timestamp
}
```

**Post Types:**
- **Self posts**: Text-based posts (`is_self=True`)
- **Link posts**: External URL posts
- **Image posts**: Direct image uploads
- **Video posts**: Reddit-hosted videos
- **Poll posts**: Reddit polls
- **Crosspost**: Shared from another subreddit

**Type Detection:**
```python
def classify_post_type(submission):
    if submission.is_self:
        return 'self'
    elif submission.is_video:
        return 'video'
    elif hasattr(submission, 'post_hint'):
        if submission.post_hint == 'image':
            return 'image'
        elif submission.post_hint == 'link':
            return 'link'
    return 'other'
```

### Content Extraction

**Text Content:**
```python
# For self posts
content = submission.selftext

# For link posts, may need to fetch external content
if not submission.is_self:
    external_url = submission.url
    # Fetch and parse external content (respect robots.txt)
```

**Metadata Enrichment:**
```python
enriched_data = {
    **post_data,
    'num_comments': submission.num_comments,
    'score': submission.score,
    'upvote_ratio': submission.upvote_ratio,
    'gilded': submission.gilded,
    'stickied': submission.stickied,
    'spoiler': submission.spoiler,
    'nsfw': submission.over_18,
    'flair': submission.link_flair_text,
    'domain': submission.domain,
    'awards': len(submission.all_awardings) if hasattr(submission, 'all_awardings') else 0,
}
```

---

## Engagement Metrics

### Core Metrics

**1. Score (Upvotes - Downvotes):**
```python
score = submission.score
# Note: Reddit fuzzes exact upvote/downvote counts
```

**2. Upvote Ratio:**
```python
upvote_ratio = submission.upvote_ratio  # 0.0 to 1.0
estimated_upvotes = score / (2 * upvote_ratio - 1)  # Approximation
```

**3. Comment Count:**
```python
num_comments = submission.num_comments
```

**4. Awards:**
```python
if hasattr(submission, 'all_awardings'):
    awards = {
        'total_awards': len(submission.all_awardings),
        'total_coins': sum(award['coin_price'] for award in submission.all_awardings),
        'award_types': [award['name'] for award in submission.all_awardings]
    }
```

### Engagement Velocity

Track how quickly posts gain engagement:

```python
from datetime import datetime

def calculate_engagement_velocity(submission):
    age_hours = (datetime.utcnow().timestamp() - submission.created_utc) / 3600
    
    if age_hours == 0:
        return 0
    
    return {
        'score_per_hour': submission.score / age_hours,
        'comments_per_hour': submission.num_comments / age_hours,
        'age_hours': age_hours
    }
```

### Engagement Quality Indicators

```python
def calculate_engagement_quality(submission):
    """
    High quality engagement indicators:
    - High comment-to-upvote ratio (discussion)
    - Awards (community recognition)
    - High upvote ratio (community agreement)
    """
    
    if submission.score == 0:
        return 0
    
    comment_ratio = submission.num_comments / max(submission.score, 1)
    award_score = len(submission.all_awardings) if hasattr(submission, 'all_awardings') else 0
    
    quality_score = (
        (comment_ratio * 100) +              # Discussion indicator
        (submission.upvote_ratio * 100) +    # Agreement indicator
        (award_score * 10)                   # Recognition indicator
    ) / 3
    
    return quality_score
```

---

## Comment Analysis

### Comment Retrieval

**Basic Comment Fetching:**
```python
submission.comments.replace_more(limit=0)  # Remove "load more comments" objects
all_comments = submission.comments.list()   # Flatten comment tree
```

**Controlled Comment Fetching:**
```python
# Limit the number of "more comments" objects to expand
submission.comments.replace_more(limit=10)

# Access comment tree
for top_level_comment in submission.comments:
    if isinstance(top_level_comment, praw.models.Comment):
        process_comment(top_level_comment)
        
        # Process replies
        for reply in top_level_comment.replies:
            if isinstance(reply, praw.models.Comment):
                process_reply(reply)
```

### Comment Metadata

```python
def extract_comment_data(comment):
    return {
        'id': comment.id,
        'body': comment.body,
        'author': str(comment.author) if comment.author else '[deleted]',
        'created_utc': comment.created_utc,
        'score': comment.score,
        'edited': comment.edited,
        'parent_id': comment.parent_id,
        'depth': comment.depth,  # Nesting level
        'is_submitter': comment.is_submitter,  # Author is OP
        'stickied': comment.stickied,
        'gilded': comment.gilded,
        'controversiality': comment.controversiality,  # 0 or 1
    }
```

### Comment Thread Analysis

**Thread Depth Analysis:**
```python
def analyze_comment_thread(submission):
    submission.comments.replace_more(limit=0)
    comments = submission.comments.list()
    
    if not comments:
        return {'max_depth': 0, 'avg_depth': 0}
    
    depths = [c.depth for c in comments]
    
    return {
        'total_comments': len(comments),
        'max_depth': max(depths),
        'avg_depth': sum(depths) / len(depths),
        'top_level_comments': sum(1 for c in comments if c.depth == 0)
    }
```

**Top Comments Extraction:**
```python
def get_top_comments(submission, limit=10, min_score=5):
    submission.comments.replace_more(limit=0)
    comments = submission.comments.list()
    
    # Filter and sort by score
    filtered_comments = [c for c in comments 
                        if isinstance(c, praw.models.Comment) and c.score >= min_score]
    sorted_comments = sorted(filtered_comments, key=lambda x: x.score, reverse=True)
    
    return sorted_comments[:limit]
```

### Comment Sentiment

```python
from textblob import TextBlob  # or use other sentiment libraries

def analyze_comment_sentiment(comment_text):
    blob = TextBlob(comment_text)
    
    return {
        'polarity': blob.sentiment.polarity,      # -1 to 1
        'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
        'sentiment': 'positive' if blob.sentiment.polarity > 0.1 
                    else 'negative' if blob.sentiment.polarity < -0.1 
                    else 'neutral'
    }
```

---

## Trending Topics and Subreddits

### Discovering Trending Subreddits

**1. Popular/All Feed:**
```python
# Get trending posts from r/all
for submission in reddit.subreddit('all').hot(limit=100):
    subreddit_name = submission.subreddit.display_name
    # Track subreddit frequency
```

**2. Trending Subreddits Endpoint:**
```python
# Reddit has a trending subreddits page
trending = reddit.subreddit('trendingsubreddits')
for submission in trending.new(limit=10):
    # Parse trending subreddits from post content
    pass
```

**3. Subreddit Growth Tracking:**
```python
def get_subreddit_stats(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    
    return {
        'name': subreddit.display_name,
        'subscribers': subreddit.subscribers,
        'active_users': subreddit.active_user_count,
        'created_utc': subreddit.created_utc,
        'description': subreddit.public_description,
        'activity_rate': subreddit.active_user_count / max(subreddit.subscribers, 1)
    }
```

### Topic Extraction

**Keyword Extraction from Titles:**
```python
from collections import Counter
import re

def extract_trending_keywords(submissions, top_n=20):
    # Combine all titles
    all_text = ' '.join([s.title for s in submissions])
    
    # Simple tokenization (improve with NLP libraries)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
    
    # Remove common stop words
    stop_words = {'the', 'is', 'in', 'and', 'to', 'of', 'for', 'with', 'on', 'this'}
    words = [w for w in words if w not in stop_words]
    
    # Count frequency
    word_counts = Counter(words)
    return word_counts.most_common(top_n)
```

**Topic Modeling (Advanced):**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def extract_topics(texts, n_topics=5, n_top_words=10):
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf = vectorizer.fit_transform(texts)
    
    # LDA topic modeling
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(tfidf)
    
    # Extract top words per topic
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        topics.append({
            'topic_id': topic_idx,
            'keywords': top_words
        })
    
    return topics
```

### Hashtag/Flair Analysis

```python
def analyze_flairs(subreddit_name, time_filter='week'):
    subreddit = reddit.subreddit(subreddit_name)
    flair_counter = Counter()
    
    for submission in subreddit.top(time_filter=time_filter, limit=500):
        if submission.link_flair_text:
            flair_counter[submission.link_flair_text] += 1
    
    return flair_counter.most_common(20)
```

---

## Community Sentiment Analysis

### Post-Level Sentiment

**Sentiment from Engagement:**
```python
def analyze_post_sentiment_from_engagement(submission):
    # Upvote ratio as sentiment proxy
    if submission.upvote_ratio > 0.85:
        engagement_sentiment = 'very_positive'
    elif submission.upvote_ratio > 0.70:
        engagement_sentiment = 'positive'
    elif submission.upvote_ratio > 0.55:
        engagement_sentiment = 'neutral'
    else:
        engagement_sentiment = 'negative'
    
    return {
        'engagement_sentiment': engagement_sentiment,
        'upvote_ratio': submission.upvote_ratio,
        'controversy_score': submission.num_comments / max(submission.score, 1)
    }
```

**Text-Based Sentiment:**
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_text_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    
    return {
        'positive': scores['pos'],
        'neutral': scores['neu'],
        'negative': scores['neg'],
        'compound': scores['compound'],  # Overall sentiment
        'classification': 'positive' if scores['compound'] > 0.05 
                         else 'negative' if scores['compound'] < -0.05 
                         else 'neutral'
    }
```

### Community-Level Sentiment

```python
def analyze_community_sentiment(subreddit_name, limit=100):
    subreddit = reddit.subreddit(subreddit_name)
    submissions = list(subreddit.hot(limit=limit))
    
    # Aggregate metrics
    avg_upvote_ratio = sum(s.upvote_ratio for s in submissions) / len(submissions)
    avg_controversy = sum(s.num_comments / max(s.score, 1) for s in submissions) / len(submissions)
    
    # Text sentiment
    analyzer = SentimentIntensityAnalyzer()
    text_sentiments = []
    
    for s in submissions:
        text = f"{s.title} {s.selftext}"
        sentiment = analyzer.polarity_scores(text)
        text_sentiments.append(sentiment['compound'])
    
    avg_text_sentiment = sum(text_sentiments) / len(text_sentiments)
    
    return {
        'avg_upvote_ratio': avg_upvote_ratio,
        'avg_controversy': avg_controversy,
        'avg_text_sentiment': avg_text_sentiment,
        'overall_sentiment': 'positive' if avg_text_sentiment > 0.05 
                            else 'negative' if avg_text_sentiment < -0.05 
                            else 'neutral'
    }
```

### Emotion Detection

```python
# Using text2emotion or similar libraries
import text2emotion as te

def detect_emotions(text):
    emotions = te.get_emotion(text)
    
    return {
        'happy': emotions.get('Happy', 0),
        'angry': emotions.get('Angry', 0),
        'surprise': emotions.get('Surprise', 0),
        'sad': emotions.get('Sad', 0),
        'fear': emotions.get('Fear', 0),
        'dominant_emotion': max(emotions.items(), key=lambda x: x[1])[0] if emotions else 'neutral'
    }
```

---

## Legal and Ethical Considerations

### Terms of Service Compliance

**Reddit API Terms:**
1. **Use OAuth2 for authentication** - Never scrape without proper authentication
2. **Respect rate limits** - Do not circumvent or exceed rate limits
3. **Cache API responses** - Don't make redundant requests
4. **Identify your application** - Use descriptive User-Agent strings
5. **Don't interfere with Reddit's operation** - No DDoS or abusive behavior

**User Agent Format:**
```
<platform>:<app ID>:<version string> (by /u/<reddit username>)
Example: web:com.example.myapp:v1.2.3 (by /u/yourusername)
```

### Privacy Considerations

**1. User Privacy:**
- Respect deleted content and accounts
- Don't deanonymize users
- Handle personally identifiable information (PII) carefully
- Comply with GDPR and other privacy regulations

**2. Data Handling:**
```python
def sanitize_user_data(data):
    """Remove or hash sensitive information"""
    if 'author' in data:
        # Consider hashing usernames for analytics
        data['author_hash'] = hash(data['author'])
        # Option: Remove author entirely for privacy
        # del data['author']
    
    if 'email' in data:
        del data['email']
    
    return data
```

**3. Content Attribution:**
- Always attribute content to Reddit and the original author
- Include links back to original Reddit posts
- Respect Creative Commons licenses where applicable

### Ethical Data Collection

**Best Practices:**

1. **Transparency:**
   - Clearly state what data you're collecting
   - Explain how data will be used
   - Provide opt-out mechanisms where possible

2. **Purpose Limitation:**
   - Only collect data necessary for your use case
   - Don't repurpose data for unintended uses
   - Delete data when no longer needed

3. **Data Minimization:**
```python
def collect_minimal_data(submission):
    """Only collect essential fields"""
    return {
        'id': submission.id,
        'title': submission.title,
        'score': submission.score,
        'created_utc': submission.created_utc,
        'subreddit': submission.subreddit.display_name,
        # Omit: author, detailed content if not needed
    }
```

4. **Respect Community Norms:**
   - Some subreddits may have policies against data collection
   - Check subreddit rules before scraping
   - Contact moderators if unsure

### GDPR and Data Protection

If operating in EU or handling EU users' data:

1. **Legal Basis:** Establish legal basis for processing (legitimate interest, consent, etc.)
2. **Data Subject Rights:** Support rights to access, rectification, erasure
3. **Data Retention:** Implement retention policies and automatic deletion
4. **Data Security:** Encrypt data in transit and at rest

```python
from datetime import datetime, timedelta

class DataRetentionPolicy:
    def __init__(self, retention_days=90):
        self.retention_days = retention_days
    
    def should_delete(self, created_timestamp):
        age = datetime.utcnow().timestamp() - created_timestamp
        age_days = age / (24 * 60 * 60)
        return age_days > self.retention_days
```

---

## Implementation Recommendations

### Recommended Libraries

**Python:**
1. **PRAW (Python Reddit API Wrapper)** - Official Python wrapper
   ```bash
   pip install praw
   ```

2. **Pushshift API** - Historical data and advanced search (third-party)
   ```bash
   pip install psaw
   ```

3. **Sentiment Analysis:**
   ```bash
   pip install vaderSentiment textblob
   ```

4. **NLP and Topic Modeling:**
   ```bash
   pip install scikit-learn nltk spacy
   ```

**Node.js:**
1. **Snoowrap** - Reddit API wrapper
   ```bash
   npm install snoowrap
   ```

**Other Languages:**
- **Java**: JRAW (Java Reddit API Wrapper)
- **C#**: Reddit.NET
- **Ruby**: redd
- **Go**: go-reddit

### Architecture Pattern

**Recommended Architecture:**

```
┌─────────────────┐
│  API Client     │ ← Rate limiting, authentication
└────────┬────────┘
         │
┌────────▼────────┐
│  Data Collector │ ← Fetch posts, comments, metadata
└────────┬────────┘
         │
┌────────▼────────┐
│  Data Processor │ ← Clean, normalize, enrich
└────────┬────────┘
         │
┌────────▼────────┐
│  Analyzer       │ ← Sentiment, topics, trends
└────────┬────────┘
         │
┌────────▼────────┐
│  Storage        │ ← Database, cache
└─────────────────┘
```

### Sample Implementation Workflow

```python
import praw
from datetime import datetime
import json

class RedditDataCollector:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.rate_limiter = RateLimiter()
    
    def collect_subreddit_data(self, subreddit_name, limit=100):
        """Collect posts from a subreddit"""
        self.rate_limiter.wait_if_needed()
        
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        for submission in subreddit.hot(limit=limit):
            post_data = self.extract_post_data(submission)
            posts.append(post_data)
        
        return posts
    
    def extract_post_data(self, submission):
        """Extract relevant data from a submission"""
        return {
            'id': submission.id,
            'title': submission.title,
            'selftext': submission.selftext,
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'subreddit': submission.subreddit.display_name,
            'author': str(submission.author) if submission.author else '[deleted]',
            'url': submission.url,
            'permalink': f"https://reddit.com{submission.permalink}",
            'flair': submission.link_flair_text,
            'gilded': submission.gilded,
            'stickied': submission.stickied,
            'over_18': submission.over_18,
        }
    
    def collect_comments(self, submission_id, max_comments=100):
        """Collect comments from a submission"""
        self.rate_limiter.wait_if_needed()
        
        submission = self.reddit.submission(id=submission_id)
        submission.comments.replace_more(limit=0)
        
        comments = []
        for comment in submission.comments.list()[:max_comments]:
            if isinstance(comment, praw.models.Comment):
                comment_data = self.extract_comment_data(comment)
                comments.append(comment_data)
        
        return comments
    
    def extract_comment_data(self, comment):
        """Extract relevant data from a comment"""
        return {
            'id': comment.id,
            'body': comment.body,
            'score': comment.score,
            'created_utc': comment.created_utc,
            'author': str(comment.author) if comment.author else '[deleted]',
            'parent_id': comment.parent_id,
            'depth': comment.depth,
        }

# Usage
collector = RedditDataCollector(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    user_agent='YourApp/1.0'
)

# Collect posts
posts = collector.collect_subreddit_data('python', limit=50)

# Collect comments for a specific post
comments = collector.collect_comments(posts[0]['id'])
```

### Error Handling

```python
import praw.exceptions
import prawcore.exceptions

def safe_api_call(func, *args, max_retries=3, **kwargs):
    """Wrapper for safe API calls with retry logic"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        
        except prawcore.exceptions.TooManyRequests as e:
            # Rate limit exceeded
            wait_time = int(e.response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        
        except prawcore.exceptions.ServerError as e:
            # Reddit server error
            print(f"Server error: {e}. Retrying in {2 ** attempt} seconds...")
            exponential_backoff(attempt)
        
        except prawcore.exceptions.RequestException as e:
            # Network or request error
            print(f"Request error: {e}. Retrying...")
            exponential_backoff(attempt)
        
        except Exception as e:
            # Unexpected error
            print(f"Unexpected error: {e}")
            if attempt == max_retries - 1:
                raise
            exponential_backoff(attempt)
    
    raise Exception("Max retries exceeded")
```

### Data Storage Recommendations

**Database Schema Example:**

```sql
-- Posts table
CREATE TABLE reddit_posts (
    id VARCHAR(20) PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    score INTEGER,
    upvote_ratio FLOAT,
    num_comments INTEGER,
    created_utc TIMESTAMP,
    subreddit VARCHAR(100),
    author VARCHAR(100),
    url TEXT,
    permalink TEXT,
    flair VARCHAR(100),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE reddit_comments (
    id VARCHAR(20) PRIMARY KEY,
    post_id VARCHAR(20) REFERENCES reddit_posts(id),
    body TEXT,
    score INTEGER,
    created_utc TIMESTAMP,
    author VARCHAR(100),
    parent_id VARCHAR(20),
    depth INTEGER,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sentiment analysis table
CREATE TABLE sentiment_analysis (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(20) REFERENCES reddit_posts(id),
    sentiment VARCHAR(20),
    polarity FLOAT,
    subjectivity FLOAT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_posts_subreddit ON reddit_posts(subreddit);
CREATE INDEX idx_posts_created ON reddit_posts(created_utc);
CREATE INDEX idx_comments_post ON reddit_comments(post_id);
```

### Monitoring and Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('RedditScraper')

# Log important events
logger.info(f"Started collecting from r/{subreddit_name}")
logger.warning(f"Rate limit approaching: {remaining_requests} requests left")
logger.error(f"Failed to fetch submission {submission_id}: {error}")
```

### Performance Optimization

**1. Caching:**
```python
from functools import lru_cache
import pickle
import time

@lru_cache(maxsize=1000)
def get_subreddit_info(subreddit_name):
    """Cache subreddit info to avoid redundant API calls"""
    return reddit.subreddit(subreddit_name)

# File-based caching for persistence
class ResponseCache:
    def __init__(self, cache_file='cache.pkl', ttl=3600):
        self.cache_file = cache_file
        self.ttl = ttl
        self.cache = self.load_cache()
    
    def load_cache(self):
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())
        self.save_cache()
```

**2. Batch Processing:**
```python
def batch_collect(subreddit_names, batch_size=5):
    """Collect from multiple subreddits in batches"""
    results = {}
    
    for i in range(0, len(subreddit_names), batch_size):
        batch = subreddit_names[i:i+batch_size]
        
        for subreddit_name in batch:
            results[subreddit_name] = collect_subreddit_data(subreddit_name)
        
        # Pause between batches
        time.sleep(2)
    
    return results
```

**3. Parallel Processing:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_collect(subreddit_names, max_workers=5):
    """Collect from multiple subreddits in parallel"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_subreddit = {
            executor.submit(collect_subreddit_data, name): name 
            for name in subreddit_names
        }
        
        for future in as_completed(future_to_subreddit):
            subreddit_name = future_to_subreddit[future]
            try:
                results[subreddit_name] = future.result()
            except Exception as e:
                logger.error(f"Error collecting {subreddit_name}: {e}")
    
    return results
```

---

## Summary Checklist

When implementing Reddit data collection, ensure you:

- [ ] Use Reddit's official API (PRAW or equivalent)
- [ ] Implement proper OAuth2 authentication
- [ ] Respect rate limits (60 req/min for authenticated)
- [ ] Implement exponential backoff for retries
- [ ] Use descriptive User-Agent strings
- [ ] Cache API responses to avoid redundant requests
- [ ] Collect essential post metadata (title, content, subreddit, score)
- [ ] Track engagement metrics (upvotes, comments, awards)
- [ ] Implement comment analysis with depth limits
- [ ] Extract trending topics using NLP techniques
- [ ] Perform sentiment analysis on text and engagement
- [ ] Follow Terms of Service and API guidelines
- [ ] Respect user privacy and handle PII carefully
- [ ] Implement proper error handling and logging
- [ ] Store data efficiently with appropriate indexes
- [ ] Monitor collection performance and rate limits
- [ ] Document your data collection practices
- [ ] Implement data retention policies

---

## Additional Resources

### Official Documentation
- Reddit API Documentation: https://www.reddit.com/dev/api/
- PRAW Documentation: https://praw.readthedocs.io/
- OAuth2 Guide: https://github.com/reddit-archive/reddit/wiki/OAuth2

### Third-Party Tools
- Pushshift API: https://pushshift.io/
- Reddit Archive: https://www.reddit.com/r/pushshift/
- Reddit Metrics: https://redditmetrics.com/

### Community Resources
- r/redditdev - Reddit API development community
- r/datasets - Data sharing community
- r/datascience - Data science discussions

### Libraries and Tools
- PRAW: https://github.com/praw-dev/praw
- Snoowrap: https://github.com/not-an-aardvark/snoowrap
- Reddit Search Tools: https://redditsearch.io/

---

**Last Updated:** October 2025
**Version:** 1.0
