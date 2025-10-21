# RedditSource

Reddit content source for community discussions and trends.

## Description

Captures trending discussions, posts, and community sentiment from Reddit to inspire ideas and track emerging topics.

## Type

**Content → Forums**

## Data Points

This source captures the following data from Reddit:

- **Post metadata** (title, content, subreddit, author, timestamps)
- **Upvotes and engagement metrics** (score, upvote ratio, awards, comments)
- **Comment analysis** (thread depth, top comments, discussion quality)
- **Trending subreddits and topics** (popular communities, keyword extraction, topic modeling)
- **Community sentiment** (positive/negative sentiment, emotional tone, controversy indicators)

## Implementation Guide

For detailed best practices, implementation guidelines, and code examples, see:

**[Reddit Scraping Best Practices](./REDDIT_SCRAPING_BEST_PRACTICES.md)**

This comprehensive guide covers:
- Reddit API authentication and rate limiting
- Data extraction patterns and pagination
- Post and comment collection strategies
- Engagement metrics and sentiment analysis
- Trending topic detection and analysis
- Legal, ethical, and privacy considerations
- Production-ready code examples

## Quick Start

### Using Reddit API (Recommended)

1. **Register your application** at https://www.reddit.com/prefs/apps
2. **Install PRAW** (Python Reddit API Wrapper):
   ```bash
   pip install praw
   ```

3. **Basic Usage:**
   ```python
   import praw

   # Initialize Reddit API client
   reddit = praw.Reddit(
       client_id="YOUR_CLIENT_ID",
       client_secret="YOUR_CLIENT_SECRET",
       user_agent="YourApp/1.0 by /u/yourusername"
   )

   # Collect posts from a subreddit
   subreddit = reddit.subreddit('python')
   for submission in subreddit.hot(limit=10):
       print(f"{submission.title} - Score: {submission.score}")
   ```

### Key Features

- ✅ **Official API Support** - Uses Reddit's official API for reliable data access
- ✅ **Rate Limit Handling** - Built-in rate limiting and exponential backoff
- ✅ **Rich Metadata** - Captures comprehensive post and user engagement data
- ✅ **Sentiment Analysis** - Text and engagement-based sentiment detection
- ✅ **Topic Detection** - Keyword extraction and trend analysis
- ✅ **Privacy Compliant** - Follows GDPR and privacy best practices

## Architecture

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

## API Rate Limits

- **Authenticated requests**: 60 requests per minute
- **Unauthenticated requests**: 10 requests per minute
- **Best practice**: Always use OAuth2 authentication

## Legal & Ethical Considerations

⚠️ **Important**: Always comply with:
- Reddit's Terms of Service and API Terms
- Rate limits and respectful API usage
- User privacy and data protection (GDPR, etc.)
- Content attribution to original authors
- Subreddit-specific rules and policies

See the [Best Practices Guide](./REDDIT_SCRAPING_BEST_PRACTICES.md#legal-and-ethical-considerations) for detailed information.

## Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [PRAW Documentation](https://praw.readthedocs.io/)
- [Reddit Developer Community (r/redditdev)](https://www.reddit.com/r/redditdev/)
- [OAuth2 Guide](https://github.com/reddit-archive/reddit/wiki/OAuth2)

## License

Please ensure compliance with Reddit's Terms of Service and API usage guidelines.