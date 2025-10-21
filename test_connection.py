"""
Simple test script to validate Reddit API connection
Run this after setting up your credentials to ensure everything works.

Usage:
    python test_connection.py
"""

import sys

def test_praw_import():
    """Test if PRAW is installed"""
    try:
        import praw
        print("✓ PRAW is installed")
        return True
    except ImportError:
        print("✗ PRAW is not installed")
        print("  Install with: pip install praw")
        return False


def test_reddit_connection():
    """Test Reddit API connection"""
    try:
        import praw
        
        print("\n--- Testing Reddit API Connection ---")
        print("\nNote: Replace these with your actual credentials!")
        print("Get credentials at: https://www.reddit.com/prefs/apps\n")
        
        # These are placeholder values - user needs to replace them
        client_id = input("Enter your client_id (or 'skip' to skip): ").strip()
        
        if client_id.lower() == 'skip':
            print("\nSkipping connection test.")
            print("To test properly, you need to:")
            print("1. Register an app at https://www.reddit.com/prefs/apps")
            print("2. Get your client_id and client_secret")
            print("3. Run this script again with your credentials")
            return True
        
        client_secret = input("Enter your client_secret: ").strip()
        user_agent = input("Enter your user_agent (e.g., 'TestApp/1.0 by /u/yourname'): ").strip()
        
        if not client_id or not client_secret or not user_agent:
            print("✗ Missing credentials")
            return False
        
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test connection by accessing r/python
        print("\nTesting connection to r/python...")
        subreddit = reddit.subreddit('python')
        
        # This will trigger an API call
        print(f"✓ Connected successfully!")
        print(f"  Subreddit: r/{subreddit.display_name}")
        print(f"  Subscribers: {subreddit.subscribers:,}")
        
        # Test fetching posts
        print("\nFetching top 3 hot posts...")
        for i, submission in enumerate(subreddit.hot(limit=3), 1):
            print(f"\n{i}. {submission.title}")
            print(f"   Score: {submission.score} | Comments: {submission.num_comments}")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nCommon issues:")
        print("- Invalid client_id or client_secret")
        print("- Invalid user_agent format")
        print("- Network connectivity issues")
        print("- Reddit API is down")
        return False


def test_optional_dependencies():
    """Test if optional dependencies are installed"""
    print("\n--- Checking Optional Dependencies ---")
    
    dependencies = [
        ('vaderSentiment', 'Sentiment analysis'),
        ('textblob', 'Text processing'),
        ('scikit-learn', 'Machine learning'),
        ('pandas', 'Data manipulation'),
    ]
    
    all_installed = True
    
    for package, description in dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed ({description})")
        except ImportError:
            print(f"○ {package} is not installed ({description})")
            all_installed = False
    
    if not all_installed:
        print("\nOptional packages can be installed with:")
        print("  pip install -r requirements.txt")
    
    return True


def main():
    """Main test function"""
    print("="*60)
    print("Reddit API Connection Test")
    print("="*60)
    
    # Test PRAW installation
    if not test_praw_import():
        sys.exit(1)
    
    # Test optional dependencies
    test_optional_dependencies()
    
    # Test Reddit connection
    test_reddit_connection()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the documentation in README.md")
    print("2. Check out examples in examples.py")
    print("3. Read GETTING_STARTED.md for detailed setup")
    print("4. Refer to QUICK_REFERENCE.md for common tasks")


if __name__ == '__main__':
    main()
