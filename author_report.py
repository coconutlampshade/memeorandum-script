#!/usr/bin/env python3
"""
Boing Boing Author Performance Report

Usage:
    python3 author_report.py [YYYY-MM]

Examples:
    python3 author_report.py           # Current month
    python3 author_report.py 2025-11   # November 2025
    python3 author_report.py 2025-12   # December 2025

Requires WP_ACCESS_TOKEN environment variable to be set.
"""
import json
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# Configuration
SITE_ID = "87954168"  # boingboing.net
BASE_URL = "https://public-api.wordpress.com/rest/v1.1"

def get_token():
    token = os.environ.get("WP_ACCESS_TOKEN")
    if not token:
        print("Error: WP_ACCESS_TOKEN environment variable not set")
        print("Set it with: export WP_ACCESS_TOKEN='your_token_here'")
        sys.exit(1)
    return token

def api_request(url, token):
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print("API Error: {} {}".format(e.code, e.reason))
        sys.exit(1)

def fetch_stats(token, date_str):
    url = "{}/sites/{}/stats/top-authors?period=month&date={}".format(BASE_URL, SITE_ID, date_str)
    return api_request(url, token)

def fetch_posts(token, after_date, before_date):
    posts = []
    offset = 0
    while True:
        url = "{}/sites/{}/posts?number=100&offset={}&after={}&before={}&fields=ID,author,date,title".format(
            BASE_URL, SITE_ID, offset, after_date, before_date
        )
        data = api_request(url, token)
        batch = data.get("posts", [])
        if not batch:
            break
        posts.extend(batch)
        offset += 100
        if len(batch) < 100:
            break
    return {"posts": posts}

def main():
    # Parse command line argument for month
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1] + "-15", "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM (e.g., 2025-11)")
            sys.exit(1)
    else:
        target_date = datetime.now()

    # Calculate month boundaries
    year = target_date.year
    month = target_date.month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1)
    else:
        last_day = datetime(year, month + 1, 1)

    after_date = first_day.strftime("%Y-%m-%dT00:00:00")
    before_date = last_day.strftime("%Y-%m-%dT00:00:00")
    stats_date = first_day.strftime("%Y-%m-%d")

    token = get_token()

    print("Fetching stats for {}...".format(first_day.strftime("%B %Y")))
    stats_data = fetch_stats(token, target_date.strftime("%Y-%m-%d"))

    print("Fetching posts...")
    posts_data = fetch_posts(token, after_date, before_date)
    print("Found {} posts\n".format(len(posts_data.get("posts", []))))

    # Build post ID to author mapping and count posts per author
    author_post_counts = {}
    for post in posts_data.get("posts", []):
        author_name = post.get("author", {}).get("name", "Unknown")
        author_post_counts[author_name] = author_post_counts.get(author_name, 0) + 1

    # Get the month key from stats data
    month_key = list(stats_data["days"].keys())[0]
    authors_data = stats_data["days"][month_key]["authors"]

    # Format the month name
    month_date = datetime.strptime(month_key, "%Y-%m-%d")
    month_name = month_date.strftime("%B %Y")

    print("=" * 70)
    print("BOING BOING AUTHOR PERFORMANCE REPORT - {}".format(month_name))
    print("=" * 70)
    print()

    # Build a set of post IDs from this month
    month_post_ids = set()
    for post in posts_data.get("posts", []):
        month_post_ids.add(post["ID"])

    # Build views per author from stats
    results = []
    for author in authors_data:
        name = author["name"]

        # Skip "Boing Boing" and "Boing Boing's Shop" as authors
        if name in ["Boing Boing", "Boing Boing's Shop"]:
            continue

        # Use actual post count from posts API
        num_posts = author_post_counts.get(name, 0)

        if num_posts == 0:
            continue

        # Total views from stats API (includes all posts, new and old)
        all_views = author["views"]

        # Views from posts written this month only
        month_views = sum(p["views"] for p in author["posts"] if p["id"] in month_post_ids)

        # Average views per new post
        avg_new = month_views / num_posts

        # Evergreen score: all views divided by new posts written
        evergreen = all_views / num_posts

        results.append((name, num_posts, month_views, avg_new, all_views, evergreen))

    # Sort by evergreen score descending
    results.sort(key=lambda x: x[5], reverse=True)

    header = "{:<20} {:>6} {:>12} {:>10} {:>12} {:>12}".format(
        "Author", "Posts", "New Views", "Avg/New", "All Views", "Evergreen"
    )
    print(header)
    print("-" * 80)

    for name, num_posts, month_views, avg_new, all_views, evergreen in results:
        row = "{:<20} {:>6} {:>12,} {:>10,.0f} {:>12,} {:>12,.0f}".format(
            name, num_posts, month_views, avg_new, all_views, evergreen
        )
        print(row)

    print()
    print("=" * 80)
    print()
    print("Posts: Articles written this month")
    print("New Views: Views on posts written this month")
    print("Avg/New: Average views per new post")
    print("All Views: Total views across all posts (new + evergreen)")
    print("Evergreen: All views divided by new posts (higher = stronger back catalog)")

    # Collect all posts with views from stats data
    all_posts_with_views = []
    post_id_to_author = {}
    for post in posts_data.get("posts", []):
        post_id_to_author[post["ID"]] = post.get("author", {}).get("name", "Unknown")

    for author in authors_data:
        author_name = author["name"]
        if author_name in ["Boing Boing", "Boing Boing's Shop"]:
            continue
        for post in author["posts"]:
            if post["id"] in month_post_ids:
                all_posts_with_views.append({
                    "title": post["title"],
                    "views": post["views"],
                    "author": author_name
                })

    # Sort by views and get top 3
    all_posts_with_views.sort(key=lambda x: x["views"], reverse=True)
    top_posts = all_posts_with_views[:3]

    if top_posts:
        print()
        print("TOP 3 POSTS THIS MONTH")
        print("-" * 80)
        for i, post in enumerate(top_posts, 1):
            title = post["title"]
            if len(title) > 50:
                title = title[:47] + "..."
            print("{}. {:,} views - {} ({})".format(i, post["views"], title, post["author"]))

if __name__ == "__main__":
    main()
