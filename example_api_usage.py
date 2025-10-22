"""
Example script demonstrating the Reddit Source API and database operations.

This script shows how to:
1. Initialize the database
2. Create records from Reddit data
3. Query and update records
4. Use the database context for CRUD operations
"""

from Model.db_context import DBContext
import json


def main():
    """Main example function."""
    print("="*70)
    print("Reddit Source API Example")
    print("="*70)
    print()
    
    # Initialize database
    db_path = "reddit_example.db"
    print(f"1. Initializing database at: {db_path}")
    db = DBContext(db_path)
    print(f"   ✓ Database initialized")
    print()
    
    # Create sample Reddit posts
    print("2. Creating sample Reddit posts...")
    
    posts = [
        {
            'source': 'reddit',
            'source_id': 'r/python_post_123',
            'title': 'Best Python libraries for data analysis',
            'description': 'Looking for recommendations on Python libraries...',
            'tags': 'python,data,analysis,pandas,numpy',
            'score': 95.5,
            'score_dictionary': {
                'upvotes': 1500,
                'comments': 250,
                'awards': 12,
                'engagement_rate': 0.92
            }
        },
        {
            'source': 'reddit',
            'source_id': 'r/learnprogramming_456',
            'title': 'How to get started with web development in 2025',
            'description': 'Complete roadmap for beginners...',
            'tags': 'webdev,javascript,react,learning',
            'score': 88.3,
            'score_dictionary': {
                'upvotes': 980,
                'comments': 180,
                'awards': 8,
                'engagement_rate': 0.85
            }
        },
        {
            'source': 'reddit',
            'source_id': 'r/programming_789',
            'title': 'Understanding async/await in modern JavaScript',
            'description': 'Deep dive into asynchronous programming...',
            'tags': 'javascript,async,programming,tutorial',
            'score': 92.1,
            'score_dictionary': {
                'upvotes': 1200,
                'comments': 200,
                'awards': 10,
                'engagement_rate': 0.89
            }
        }
    ]
    
    for post in posts:
        record = db.upsert(**post)
        print(f"   ✓ Created: {record.title[:50]}...")
    print()
    
    # Query records
    print("3. Querying records...")
    print(f"   Total records: {db.count()}")
    print(f"   Reddit records: {db.count_by_source('reddit')}")
    print()
    
    # List top posts by score
    print("4. Top posts by score:")
    top_posts = db.list_all(limit=3, order_by='score', ascending=False)
    for i, post in enumerate(top_posts, 1):
        score_dict = post.get_score_dict()
        print(f"   {i}. {post.title}")
        print(f"      Score: {post.score} | Upvotes: {score_dict.get('upvotes', 0)} | "
              f"Comments: {score_dict.get('comments', 0)}")
    print()
    
    # Read specific post
    print("5. Reading specific post...")
    post = db.read('reddit', 'r/python_post_123')
    if post:
        print(f"   Title: {post.title}")
        print(f"   Description: {post.description}")
        print(f"   Tags: {post.tags}")
        print(f"   Score: {post.score}")
        print(f"   Processed: {post.processed}")
        score_dict = post.get_score_dict()
        print(f"   Score details: {json.dumps(score_dict, indent=6)}")
    print()
    
    # Update a post
    print("6. Updating post processing status...")
    updated = db.update(
        source='reddit',
        source_id='r/python_post_123',
        processed=True
    )
    if updated:
        print(f"   ✓ Post marked as processed")
    print()
    
    # Convert to dictionary
    print("7. Exporting post to dictionary format...")
    post_dict = post.to_dict()
    print(f"   {json.dumps(post_dict, indent=3, default=str)}")
    print()
    
    # Close database
    db.close()
    print("="*70)
    print("Example completed successfully!")
    print("="*70)
    print()
    print(f"Database created at: {db_path}")
    print("You can explore it with: sqlite3 reddit_example.db")


if __name__ == '__main__':
    main()
