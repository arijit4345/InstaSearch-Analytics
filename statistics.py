def get_statistics(posts):

    total_posts = len(posts)

    # Safety check: If there are no posts, return all zeros immediately to prevent a crash
    if total_posts == 0:
        return {
            "avg_likes": 0,
            "avg_comments": 0,
            "avg_shares": 0,
            "avg_engagement": 0
        }

    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_engagement = 0

    for post in posts:

        total_likes += post.likes
        total_comments += post.comments
        total_shares += post.shares

        total_engagement += (
            post.likes +
            post.comments +
            post.shares
        )

    avg_likes = total_likes / total_posts
    avg_comments = total_comments / total_posts
    avg_shares = total_shares / total_posts
    avg_engagement = total_engagement / total_posts

    return {
        "avg_likes": round(avg_likes, 2),
        "avg_comments": round(avg_comments, 2),
        "avg_shares": round(avg_shares, 2),
        "avg_engagement": round(avg_engagement, 2)
    }