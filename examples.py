"""
Reddit Data Collection Examples
================================

Practical examples for collecting and analyzing Reddit data following best practices.

Requirements:
    pip install praw vaderSentiment textblob scikit-learn
"""

import praw
import time
import logging
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any, Optional
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RedditCollector')


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Rate limiter to respect Reddit API limits (60 requests/minute)"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Remove old requests outside time window
        cutoff = now - timedelta(seconds=self.time_window)
        self.requests = [req for req in self.requests if req > cutoff]
        
        # Wait if at limit
        if len(self.requests) >= self.max_requests:
            sleep_time = (self.requests[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time + 0.1)
                self.requests = []
        
        self.requests.append(now)


# ============================================================================
# MAIN COLLECTOR CLASS
# ============================================================================

class RedditDataCollector:
    """Main class for collecting Reddit data"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit API client
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: Descriptive user agent string
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.rate_limiter = RateLimiter()
        logger.info("RedditDataCollector initialized")
    
    def collect_posts(self, subreddit_name: str, limit: int = 100, 
                     sort_by: str = 'hot', time_filter: str = 'day') -> List[Dict[str, Any]]:
        """
        Collect posts from a subreddit
        
        Args:
            subreddit_name: Name of the subreddit (without r/)
            limit: Maximum number of posts to collect
            sort_by: Sort method ('hot', 'new', 'top', 'rising')
            time_filter: Time filter for 'top' ('hour', 'day', 'week', 'month', 'year', 'all')
        
        Returns:
            List of post dictionaries
        """
        self.rate_limiter.wait_if_needed()
        
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        try:
            # Get submissions based on sort method
            if sort_by == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort_by == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort_by == 'top':
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_by == 'rising':
                submissions = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid sort_by value: {sort_by}")
            
            for submission in submissions:
                post_data = self._extract_post_data(submission)
                posts.append(post_data)
                
            logger.info(f"Collected {len(posts)} posts from r/{subreddit_name}")
            
        except Exception as e:
            logger.error(f"Error collecting posts from r/{subreddit_name}: {e}")
        
        return posts
    
    def _extract_post_data(self, submission) -> Dict[str, Any]:
        """Extract relevant data from a Reddit submission"""
        return {
            'id': submission.id,
            'title': submission.title,
            'selftext': submission.selftext if submission.is_self else '',
            'url': submission.url,
            'permalink': f"https://reddit.com{submission.permalink}",
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'created_datetime': datetime.fromtimestamp(submission.created_utc).isoformat(),
            'subreddit': submission.subreddit.display_name,
            'author': str(submission.author) if submission.author else '[deleted]',
            'flair': submission.link_flair_text,
            'gilded': submission.gilded,
            'stickied': submission.stickied,
            'over_18': submission.over_18,
            'is_self': submission.is_self,
            'domain': submission.domain,
        }
    
    def collect_comments(self, post_id: str, max_comments: int = 100) -> List[Dict[str, Any]]:
        """
        Collect comments from a post
        
        Args:
            post_id: Reddit post ID
            max_comments: Maximum number of comments to collect
        
        Returns:
            List of comment dictionaries
        """
        self.rate_limiter.wait_if_needed()
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "load more" objects
            
            comments = []
            for comment in submission.comments.list()[:max_comments]:
                if isinstance(comment, praw.models.Comment):
                    comment_data = self._extract_comment_data(comment)
                    comments.append(comment_data)
            
            logger.info(f"Collected {len(comments)} comments from post {post_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Error collecting comments from post {post_id}: {e}")
            return []
    
    def _extract_comment_data(self, comment) -> Dict[str, Any]:
        """Extract relevant data from a Reddit comment"""
        return {
            'id': comment.id,
            'body': comment.body,
            'score': comment.score,
            'created_utc': comment.created_utc,
            'created_datetime': datetime.fromtimestamp(comment.created_utc).isoformat(),
            'author': str(comment.author) if comment.author else '[deleted]',
            'parent_id': comment.parent_id,
            'depth': comment.depth,
            'is_submitter': comment.is_submitter,
            'gilded': comment.gilded,
        }
    
    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """
        Get information about a subreddit
        
        Args:
            subreddit_name: Name of the subreddit (without r/)
        
        Returns:
            Dictionary with subreddit information
        """
        self.rate_limiter.wait_if_needed()
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            return {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'created_utc': subreddit.created_utc,
                'created_datetime': datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                'over_18': subreddit.over18,
                'activity_rate': subreddit.active_user_count / max(subreddit.subscribers, 1),
            }
            
        except Exception as e:
            logger.error(f"Error getting info for r/{subreddit_name}: {e}")
            return {}


# ============================================================================
# ENGAGEMENT ANALYSIS
# ============================================================================

class EngagementAnalyzer:
    """Analyze engagement metrics from Reddit posts"""
    
    @staticmethod
    def calculate_engagement_velocity(post: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how quickly a post gains engagement"""
        created_utc = post['created_utc']
        age_hours = (datetime.now().timestamp() - created_utc) / 3600
        
        if age_hours <= 0:
            age_hours = 0.1  # Avoid division by zero
        
        return {
            'age_hours': age_hours,
            'score_per_hour': post['score'] / age_hours,
            'comments_per_hour': post['num_comments'] / age_hours,
        }
    
    @staticmethod
    def calculate_engagement_quality(post: Dict[str, Any]) -> float:
        """
        Calculate engagement quality score
        Higher score indicates more discussion and community recognition
        """
        score = max(post['score'], 1)
        comment_ratio = post['num_comments'] / score
        upvote_ratio = post['upvote_ratio']
        
        # Quality factors
        discussion_score = min(comment_ratio * 100, 100)  # Cap at 100
        agreement_score = upvote_ratio * 100
        
        quality_score = (discussion_score + agreement_score) / 2
        return quality_score
    
    @staticmethod
    def is_trending(post: Dict[str, Any], min_velocity: float = 10.0) -> bool:
        """Determine if a post is trending based on engagement velocity"""
        velocity = EngagementAnalyzer.calculate_engagement_velocity(post)
        return velocity['score_per_hour'] >= min_velocity


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

class SentimentAnalyzer:
    """Analyze sentiment from Reddit posts and comments"""
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
            self.vader_available = True
        except ImportError:
            logger.warning("vaderSentiment not available. Install with: pip install vaderSentiment")
            self.vader_available = False
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if not self.vader_available or not text:
            return {
                'compound': 0.0,
                'positive': 0.0,
                'neutral': 1.0,
                'negative': 0.0,
                'classification': 'neutral'
            }
        
        scores = self.vader.polarity_scores(text)
        
        # Classify based on compound score
        if scores['compound'] > 0.05:
            classification = 'positive'
        elif scores['compound'] < -0.05:
            classification = 'negative'
        else:
            classification = 'neutral'
        
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'classification': classification
        }
    
    def analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of a post (title + content)"""
        text = f"{post['title']} {post['selftext']}"
        return self.analyze_text(text)
    
    def analyze_engagement_sentiment(self, post: Dict[str, Any]) -> Dict[str, str]:
        """Analyze sentiment based on engagement metrics"""
        upvote_ratio = post['upvote_ratio']
        
        if upvote_ratio > 0.85:
            sentiment = 'very_positive'
        elif upvote_ratio > 0.70:
            sentiment = 'positive'
        elif upvote_ratio > 0.55:
            sentiment = 'neutral'
        else:
            sentiment = 'negative'
        
        # Calculate controversy (high comments relative to score)
        controversy = post['num_comments'] / max(post['score'], 1)
        
        return {
            'engagement_sentiment': sentiment,
            'controversy_level': 'high' if controversy > 1.0 else 'normal'
        }


# ============================================================================
# TOPIC EXTRACTION
# ============================================================================

class TopicExtractor:
    """Extract trending topics and keywords from Reddit posts"""
    
    # Common English stop words
    STOP_WORDS = {
        'the', 'is', 'in', 'and', 'to', 'of', 'for', 'with', 'on', 'this', 
        'that', 'are', 'was', 'be', 'by', 'at', 'from', 'or', 'an', 'as',
        'it', 'can', 'will', 'but', 'not', 'you', 'your', 'we', 'my', 'me',
        'i', 'a', 'has', 'have', 'had', 'what', 'when', 'where', 'who', 'how'
    }
    
    @staticmethod
    def extract_keywords(posts: List[Dict[str, Any]], top_n: int = 20) -> List[tuple]:
        """
        Extract most common keywords from post titles
        
        Args:
            posts: List of post dictionaries
            top_n: Number of top keywords to return
        
        Returns:
            List of (keyword, count) tuples
        """
        # Combine all titles
        all_text = ' '.join([post['title'] for post in posts])
        
        # Tokenize (simple word extraction)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Remove stop words
        words = [w for w in words if w not in TopicExtractor.STOP_WORDS]
        
        # Count frequency
        word_counts = Counter(words)
        return word_counts.most_common(top_n)
    
    @staticmethod
    def extract_trending_flairs(posts: List[Dict[str, Any]], top_n: int = 10) -> List[tuple]:
        """
        Extract most common post flairs
        
        Args:
            posts: List of post dictionaries
            top_n: Number of top flairs to return
        
        Returns:
            List of (flair, count) tuples
        """
        flairs = [post['flair'] for post in posts if post.get('flair')]
        flair_counts = Counter(flairs)
        return flair_counts.most_common(top_n)
    
    @staticmethod
    def get_top_posts_by_engagement(posts: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top posts sorted by engagement quality"""
        analyzer = EngagementAnalyzer()
        
        # Calculate quality scores
        posts_with_quality = []
        for post in posts:
            post_copy = post.copy()
            post_copy['quality_score'] = analyzer.calculate_engagement_quality(post)
            posts_with_quality.append(post_copy)
        
        # Sort by quality score
        sorted_posts = sorted(posts_with_quality, key=lambda x: x['quality_score'], reverse=True)
        return sorted_posts[:top_n]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_basic_collection():
    """Example: Basic data collection"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Post Collection")
    print("="*80)
    
    # Initialize collector (replace with your credentials)
    collector = RedditDataCollector(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="RedditResearch/1.0 by /u/yourusername"
    )
    
    # Collect hot posts from r/python
    posts = collector.collect_posts('python', limit=10, sort_by='hot')
    
    # Display results
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Score: {post['score']} | Comments: {post['num_comments']}")
        print(f"   URL: {post['permalink']}")


def example_engagement_analysis():
    """Example: Analyze engagement metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Engagement Analysis")
    print("="*80)
    
    collector = RedditDataCollector(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="RedditResearch/1.0 by /u/yourusername"
    )
    
    posts = collector.collect_posts('technology', limit=20, sort_by='hot')
    analyzer = EngagementAnalyzer()
    
    print("\nTop Posts by Engagement Velocity:")
    for post in posts[:5]:
        velocity = analyzer.calculate_engagement_velocity(post)
        quality = analyzer.calculate_engagement_quality(post)
        
        print(f"\n- {post['title'][:60]}...")
        print(f"  Score/hour: {velocity['score_per_hour']:.2f}")
        print(f"  Comments/hour: {velocity['comments_per_hour']:.2f}")
        print(f"  Quality score: {quality:.2f}")


def example_sentiment_analysis():
    """Example: Sentiment analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Sentiment Analysis")
    print("="*80)
    
    collector = RedditDataCollector(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="RedditResearch/1.0 by /u/yourusername"
    )
    
    posts = collector.collect_posts('technology', limit=10)
    sentiment_analyzer = SentimentAnalyzer()
    
    print("\nPost Sentiment Analysis:")
    for post in posts[:5]:
        text_sentiment = sentiment_analyzer.analyze_post(post)
        engagement_sentiment = sentiment_analyzer.analyze_engagement_sentiment(post)
        
        print(f"\n- {post['title'][:60]}...")
        print(f"  Text sentiment: {text_sentiment['classification']} (compound: {text_sentiment['compound']:.2f})")
        print(f"  Engagement sentiment: {engagement_sentiment['engagement_sentiment']}")
        print(f"  Controversy: {engagement_sentiment['controversy_level']}")


def example_topic_extraction():
    """Example: Extract trending topics"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Topic Extraction")
    print("="*80)
    
    collector = RedditDataCollector(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="RedditResearch/1.0 by /u/yourusername"
    )
    
    posts = collector.collect_posts('technology', limit=50)
    
    # Extract keywords
    keywords = TopicExtractor.extract_keywords(posts, top_n=15)
    print("\nTop Keywords:")
    for keyword, count in keywords:
        print(f"  - {keyword}: {count}")
    
    # Extract trending flairs
    flairs = TopicExtractor.extract_trending_flairs(posts, top_n=10)
    print("\nTop Flairs:")
    for flair, count in flairs:
        print(f"  - {flair}: {count}")


def example_multi_subreddit_analysis():
    """Example: Analyze multiple subreddits"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Multi-Subreddit Analysis")
    print("="*80)
    
    collector = RedditDataCollector(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="RedditResearch/1.0 by /u/yourusername"
    )
    
    subreddits = ['python', 'javascript', 'programming']
    
    print("\nSubreddit Statistics:")
    for subreddit_name in subreddits:
        info = collector.get_subreddit_info(subreddit_name)
        if info:
            print(f"\nr/{info['name']}")
            print(f"  Subscribers: {info['subscribers']:,}")
            print(f"  Active users: {info['active_users']:,}")
            print(f"  Activity rate: {info['activity_rate']:.4f}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("Reddit Data Collection Examples")
    print("="*80)
    print("\nNOTE: Update client_id, client_secret, and user_agent before running")
    print("Register your app at: https://www.reddit.com/prefs/apps")
    print("="*80)
    
    # Uncomment to run examples (after adding your credentials)
    # example_basic_collection()
    # example_engagement_analysis()
    # example_sentiment_analysis()
    # example_topic_extraction()
    # example_multi_subreddit_analysis()
