"""
Practical Demonstration: Reddit API vs Web Scraping
===================================================

This script demonstrates the difference between using Reddit's API (PRAW)
and web scraping for collecting data from r/AmItheAsshole.

⚠️ WARNING: Web scraping violates Reddit's Terms of Service.
            This is for educational comparison only.

✅ RECOMMENDED: Use the Reddit API (PRAW) for all real applications.

Usage:
    python demo_api_vs_scraping.py

Requirements:
    pip install praw beautifulsoup4 requests
"""

import sys
import time
from datetime import datetime

# Flag to enable/disable scraping demo (disabled by default for ToS compliance)
ENABLE_SCRAPING_DEMO = False


def demo_api_approach():
    """
    Demonstrate data collection using Reddit's official API (PRAW)
    ✅ This is the RECOMMENDED approach
    """
    print("\n" + "="*80)
    print("APPROACH 1: Reddit Official API (PRAW)")
    print("="*80)
    print("✅ Legal and complies with Reddit's Terms of Service")
    print("✅ Reliable and stable")
    print("✅ Easy to maintain\n")
    
    try:
        import praw
        
        print("Note: You need Reddit API credentials to run this demo.")
        print("Get them at: https://www.reddit.com/prefs/apps\n")
        
        client_id = input("Enter your client_id (or 'demo' for code preview): ").strip()
        
        if client_id.lower() == 'demo':
            print("\n--- CODE EXAMPLE ---")
            print("""
import praw

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="AITAAnalyzer/1.0 by /u/yourusername"
)

# Fetch top posts from r/AmItheAsshole
subreddit = reddit.subreddit('AmItheAsshole')

print("Top Posts from r/AmItheAsshole:\\n")
for i, submission in enumerate(subreddit.top(time_filter='week', limit=10), 1):
    print(f"{i}. {submission.title}")
    print(f"   Score: {submission.score}")
    print(f"   Comments: {submission.num_comments}")
    print(f"   Flair: {submission.link_flair_text}")
    print(f"   Author: {submission.author}")
    print(f"   Upvote Ratio: {submission.upvote_ratio:.2%}")
    print(f"   Created: {datetime.fromtimestamp(submission.created_utc)}")
    print(f"   URL: https://reddit.com{submission.permalink}")
    print()
            """)
            
            print("\n✅ Advantages:")
            print("   • Clean, simple code (only ~15 lines)")
            print("   • Rich metadata available")
            print("   • Reliable and won't break")
            print("   • Predictable rate limits (60 req/min)")
            print("   • Production-ready")
            return
        
        client_secret = input("Enter your client_secret: ").strip()
        user_agent = input("Enter your user_agent (e.g., 'TestApp/1.0'): ").strip()
        
        if not client_id or not client_secret or not user_agent:
            print("\n⚠️ Missing credentials. Showing code example instead.\n")
            demo_api_approach()
            return
        
        print("\nInitializing Reddit API connection...")
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        print("✓ Connected to Reddit API")
        print("\nFetching top posts from r/AmItheAsshole...\n")
        
        subreddit = reddit.subreddit('AmItheAsshole')
        
        start_time = time.time()
        posts_collected = 0
        
        for i, submission in enumerate(subreddit.top(time_filter='week', limit=10), 1):
            posts_collected += 1
            print(f"{i}. {submission.title[:70]}...")
            print(f"   Score: {submission.score:,} | Comments: {submission.num_comments:,}")
            print(f"   Flair: {submission.link_flair_text}")
            print(f"   Upvote Ratio: {submission.upvote_ratio:.2%}")
            print(f"   Author: u/{submission.author}")
            print(f"   Created: {datetime.fromtimestamp(submission.created_utc)}")
            print(f"   URL: https://reddit.com{submission.permalink}")
            print()
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Successfully collected {posts_collected} posts in {elapsed:.2f} seconds")
        print(f"✅ All data is structured and reliable")
        print(f"✅ Code is maintainable and won't break")
        
    except ImportError:
        print("\n⚠️ PRAW not installed. Install with: pip install praw")
        print("Showing code example instead...\n")
        demo_api_approach()
        
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        print("This might be due to invalid credentials or network issues.")


def demo_scraping_approach():
    """
    Demonstrate web scraping approach
    ❌ This is NOT RECOMMENDED and violates Reddit's ToS
    """
    print("\n" + "="*80)
    print("APPROACH 2: Web Scraping (BeautifulSoup + Requests)")
    print("="*80)
    print("❌ Violates Reddit's Terms of Service")
    print("❌ Unreliable (breaks when HTML changes)")
    print("❌ Difficult to maintain")
    print("❌ Risk of IP ban\n")
    
    if not ENABLE_SCRAPING_DEMO:
        print("⚠️ Scraping demo is DISABLED by default (ToS compliance)")
        print("\nCode example (DO NOT USE IN PRODUCTION):")
        print("""
import requests
from bs4 import BeautifulSoup

# ⚠️ WARNING: This violates Reddit's Terms of Service
url = 'https://www.reddit.com/r/AmItheAsshole/top/?t=week'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Problems with this approach:
# 1. HTML structure is complex and changes frequently
# 2. Reddit uses JavaScript for dynamic loading
# 3. Limited data accessible compared to API
# 4. VIOLATES Terms of Service
# 5. Risk of permanent IP ban
# 6. No access to:
#    - Exact upvote counts
#    - Upvote ratios
#    - Precise timestamps
#    - Author details
#    - Easy comment access
#    - Pagination helpers

# Parsing would require 100+ lines of fragile code
# that breaks every time Reddit updates their UI

# Example of fragile selectors (likely already broken):
posts = soup.find_all('div', {'data-testid': 'post-container'})
for post in posts:
    try:
        title = post.find('h3').text  # May not exist
        score = post.find('div', string=re.compile(r'\\d+')).text  # Fragile
        # Many more fragile selectors...
    except AttributeError:
        # Selectors broke again...
        pass
        """)
        
        print("\n❌ Disadvantages:")
        print("   • 100+ lines of complex, fragile code")
        print("   • Breaks frequently with UI updates")
        print("   • Limited metadata (no upvote ratio, exact times, etc.)")
        print("   • High maintenance burden")
        print("   • VIOLATES TERMS OF SERVICE")
        print("   • Risk of IP ban")
        print("   • NOT production-ready")
        print("\n⚠️ DO NOT USE web scraping for Reddit data collection")
        return
    
    # If scraping demo is enabled (educational purposes only)
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print("⚠️ Attempting to scrape (for comparison only)...\n")
        
        url = 'https://www.reddit.com/r/AmItheAsshole/top/?t=week'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        start_time = time.time()
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Status Code: {response.status_code}")
        
        # Attempt to parse (this will likely fail or be incomplete)
        print("\nAttempting to parse HTML structure...")
        print("⚠️ This is fragile and will break with Reddit UI updates\n")
        
        # Modern Reddit uses heavy JavaScript - scraping gets incomplete data
        posts = soup.find_all('div', {'data-testid': 'post-container'})
        
        if not posts:
            print("❌ Could not find posts (HTML structure changed or JavaScript required)")
            print("   This is a common problem with web scraping")
        else:
            posts_collected = 0
            for i, post in enumerate(posts[:10], 1):
                posts_collected += 1
                try:
                    # These selectors are examples and likely won't work
                    title_elem = post.find('h3')
                    title = title_elem.text if title_elem else "Could not extract title"
                    
                    print(f"{i}. {title[:70]}...")
                    print(f"   Score: Unable to extract reliably")
                    print(f"   Comments: Unable to extract reliably")
                    print(f"   Flair: Unable to extract")
                    print(f"   Upvote Ratio: ❌ Not available via scraping")
                    print(f"   Exact timestamp: ❌ Not available")
                    print()
                except Exception as e:
                    print(f"   ❌ Error parsing post: {e}")
                    print()
        
        elapsed = time.time() - start_time
        
        print(f"\n⚠️ Attempted to scrape data in {elapsed:.2f} seconds")
        print(f"❌ Data is incomplete and unreliable")
        print(f"❌ Code will break when Reddit updates UI")
        print(f"❌ VIOLATES Reddit's Terms of Service")
        
    except ImportError:
        print("\n⚠️ BeautifulSoup or Requests not installed")
        print("But you shouldn't install them for Reddit scraping anyway!")
        print("Use PRAW instead: pip install praw")
    except Exception as e:
        print(f"\n❌ Scraping failed: {e}")
        print("This is common with web scraping - sites change frequently")


def show_comparison_summary():
    """Show side-by-side comparison"""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    
    comparison = [
        ("Aspect", "Reddit API (PRAW) ✅", "Web Scraping ❌"),
        ("-" * 20, "-" * 30, "-" * 30),
        ("Legal Status", "✅ Complies with ToS", "❌ Violates ToS"),
        ("Reliability", "✅ Stable & maintained", "❌ Breaks frequently"),
        ("Code Complexity", "✅ Simple (~15 lines)", "❌ Complex (100+ lines)"),
        ("Data Quality", "✅ Complete metadata", "❌ Limited data"),
        ("Maintenance", "✅ Low effort", "❌ High effort"),
        ("Rate Limits", "✅ 60 req/min (clear)", "❌ Undefined (risk ban)"),
        ("Error Handling", "✅ Clear exceptions", "❌ Generic errors"),
        ("Upvote Ratio", "✅ Available", "❌ Not available"),
        ("Exact Timestamps", "✅ Available", "❌ Approximate only"),
        ("Comment Access", "✅ Easy (full tree)", "❌ Difficult"),
        ("Pagination", "✅ Built-in", "❌ Manual & complex"),
        ("Production Ready", "✅ Yes", "❌ No"),
        ("Risk of Ban", "✅ No risk", "❌ High risk"),
        ("Documentation", "✅ Excellent", "❌ None (unofficial)"),
    ]
    
    # Calculate column widths
    col_widths = [
        max(len(row[0]) for row in comparison),
        max(len(row[1]) for row in comparison),
        max(len(row[2]) for row in comparison),
    ]
    
    # Print table
    for row in comparison:
        print(f"{row[0]:{col_widths[0]}} | {row[1]:{col_widths[1]}} | {row[2]:{col_widths[2]}}")
    
    print("\n" + "="*80)
    print("RECOMMENDATION: Always use Reddit API (PRAW)")
    print("="*80)
    print("\n✅ Reasons to use PRAW:")
    print("   1. Legal and complies with Terms of Service")
    print("   2. Reliable - won't break with UI updates")
    print("   3. Complete data access")
    print("   4. Easy to use and maintain")
    print("   5. Production-ready with good documentation")
    print("   6. No risk of IP ban")
    print("\n❌ Reasons NOT to use web scraping:")
    print("   1. Violates Reddit's Terms of Service")
    print("   2. Unreliable - breaks frequently")
    print("   3. Limited data compared to API")
    print("   4. Complex and hard to maintain")
    print("   5. High risk of IP ban")
    print("   6. Not suitable for production use")


def main():
    """Main demo function"""
    print("\n" + "="*80)
    print("Reddit Data Collection: API vs Web Scraping Comparison")
    print("="*80)
    print("\nThis demo compares two approaches for collecting Reddit data:")
    print("1. ✅ Reddit Official API (PRAW) - RECOMMENDED")
    print("2. ❌ Web Scraping - NOT RECOMMENDED (violates ToS)")
    print("\nExample: Fetching top posts from r/AmItheAsshole")
    
    while True:
        print("\n" + "-"*80)
        print("Choose a demo:")
        print("1. Reddit API (PRAW) approach - ✅ RECOMMENDED")
        print("2. Web scraping approach - ❌ NOT RECOMMENDED (educational only)")
        print("3. Show comparison summary")
        print("4. Exit")
        print("-"*80)
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            demo_api_approach()
        elif choice == '2':
            demo_scraping_approach()
        elif choice == '3':
            show_comparison_summary()
        elif choice == '4':
            print("\nThank you for reviewing this comparison!")
            print("Remember: Always use Reddit's official API (PRAW) ✅")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print("\n" + "="*80)
    print("Resources:")
    print("="*80)
    print("• PRAW Documentation: https://praw.readthedocs.io/")
    print("• Reddit API: https://www.reddit.com/dev/api/")
    print("• Register App: https://www.reddit.com/prefs/apps")
    print("• Community: r/redditdev")
    print("\n✅ For detailed comparison, see: API_VS_SCRAPING_COMPARISON.md")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
