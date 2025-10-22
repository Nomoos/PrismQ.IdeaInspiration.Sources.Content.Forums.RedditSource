# Getting Started with Reddit Data Collection

This guide will help you get started with collecting and analyzing Reddit data.

## Prerequisites

- Python 3.8 or higher
- A Reddit account
- Basic knowledge of Python

## Step 1: Register a Reddit Application

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." at the bottom
3. Fill in the form:
   - **Name**: Your application name (e.g., "MyRedditAnalyzer")
   - **App type**: Select "script" (for personal use)
   - **Description**: Brief description of what your app does
   - **About URL**: Can leave blank or add your website
   - **Redirect URI**: Use `http://localhost:8080` for script apps
4. Click "create app"
5. Note down your **client_id** (under the app name) and **client_secret**

## Step 2: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

## Step 3: Configure Your Credentials

1. Copy the configuration template:
   ```bash
   cp config.ini.template config.ini
   ```

2. Edit `config.ini` and add your credentials:
   ```ini
   [reddit]
   client_id = your_client_id_here
   client_secret = your_client_secret_here
   user_agent = MyApp/1.0 by /u/your_reddit_username
   ```

**Important**: Never commit `config.ini` to version control! It's already in `.gitignore`.

## Step 4: Test Your Setup

Create a simple test script `test_connection.py`:

```python
import praw

# Initialize Reddit API
reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="MyApp/1.0 by /u/yourusername"
)

# Test connection
print("Testing Reddit API connection...")
subreddit = reddit.subreddit('python')
print(f"Connected! r/python has {subreddit.subscribers:,} subscribers")

# Get a few posts
print("\nTop 5 hot posts:")
for i, submission in enumerate(subreddit.hot(limit=5), 1):
    print(f"{i}. {submission.title} (Score: {submission.score})")
```

Run the test:
```bash
python test_connection.py
```

## Step 5: Use the Example Code

The `examples.py` file contains several usage examples:

### Example 1: Collect Posts from a Subreddit

```python
from examples import RedditDataCollector

collector = RedditDataCollector(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="MyApp/1.0 by /u/yourusername"
)

# Collect hot posts
posts = collector.collect_posts('python', limit=20, sort_by='hot')

for post in posts:
    print(f"{post['title']} - Score: {post['score']}")
```

### Example 2: Analyze Engagement

```python
from examples import RedditDataCollector, EngagementAnalyzer

collector = RedditDataCollector(...)
analyzer = EngagementAnalyzer()

posts = collector.collect_posts('technology', limit=50)

for post in posts:
    velocity = analyzer.calculate_engagement_velocity(post)
    quality = analyzer.calculate_engagement_quality(post)
    
    print(f"{post['title']}")
    print(f"  Velocity: {velocity['score_per_hour']:.2f} score/hour")
    print(f"  Quality: {quality:.2f}")
```

### Example 3: Sentiment Analysis

```python
from examples import RedditDataCollector, SentimentAnalyzer

collector = RedditDataCollector(...)
sentiment_analyzer = SentimentAnalyzer()

posts = collector.collect_posts('worldnews', limit=30)

for post in posts:
    sentiment = sentiment_analyzer.analyze_post(post)
    print(f"{post['title']}")
    print(f"  Sentiment: {sentiment['classification']} ({sentiment['compound']:.2f})")
```

### Example 4: Extract Topics

```python
from examples import RedditDataCollector, TopicExtractor

collector = RedditDataCollector(...)
posts = collector.collect_posts('technology', limit=100)

# Get trending keywords
keywords = TopicExtractor.extract_keywords(posts, top_n=20)
print("Top Keywords:")
for keyword, count in keywords:
    print(f"  {keyword}: {count}")

# Get trending flairs
flairs = TopicExtractor.extract_trending_flairs(posts)
print("\nTop Flairs:")
for flair, count in flairs:
    print(f"  {flair}: {count}")
```

## Step 6: Understand Rate Limits

Reddit API has strict rate limits:
- **Authenticated**: 60 requests per minute
- **Unauthenticated**: 10 requests per minute

The `RateLimiter` class in `examples.py` automatically handles rate limiting for you. It will pause your requests if you approach the limit.

## Step 7: Best Practices

1. **Always authenticate**: Use OAuth2 for better rate limits
2. **Respect rate limits**: Don't circumvent or exceed limits
3. **Use meaningful User-Agent**: Identify your app properly
4. **Cache responses**: Don't make redundant requests
5. **Handle errors gracefully**: Implement retry logic
6. **Respect privacy**: Don't collect unnecessary personal data
7. **Follow ToS**: Comply with Reddit's Terms of Service

## Common Issues and Solutions

### Issue: "ResponseException: received 401 HTTP response"
**Solution**: Check your client_id and client_secret are correct

### Issue: "ResponseException: received 429 HTTP response"
**Solution**: You've exceeded rate limits. Wait and reduce request frequency

### Issue: "prawcore.exceptions.RequestException: error with request"
**Solution**: Check your internet connection and Reddit's status

### Issue: "ImportError: No module named 'praw'"
**Solution**: Install dependencies: `pip install -r requirements.txt`

## Advanced Topics

For more advanced usage, see the [Best Practices Guide](./REDDIT_SCRAPING_BEST_PRACTICES.md):

- Pagination and batch processing
- Historical data collection
- Real-time streaming
- Advanced sentiment analysis
- Topic modeling with LDA
- Database integration
- Production deployment

## Resources

- **Reddit API Documentation**: https://www.reddit.com/dev/api/
- **PRAW Documentation**: https://praw.readthedocs.io/
- **Reddit Developer Community**: https://www.reddit.com/r/redditdev/
- **Best Practices Guide**: [REDDIT_SCRAPING_BEST_PRACTICES.md](./REDDIT_SCRAPING_BEST_PRACTICES.md)

## Need Help?

- Check the [Best Practices Guide](./REDDIT_SCRAPING_BEST_PRACTICES.md) for detailed documentation
- Visit r/redditdev for developer discussions
- Review PRAW documentation at https://praw.readthedocs.io/
- Check Reddit API documentation at https://www.reddit.com/dev/api/

## Legal Notice

Always comply with:
- Reddit's Terms of Service
- Reddit's API Terms
- User privacy and data protection laws (GDPR, etc.)
- Subreddit-specific rules

See the [Legal and Ethical Considerations](./REDDIT_SCRAPING_BEST_PRACTICES.md#legal-and-ethical-considerations) section in the Best Practices Guide.
