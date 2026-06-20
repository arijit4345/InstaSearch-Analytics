def get_statistics(posts):

    total_posts = len(posts)

    # Safety check: If there are no posts, return all zeros immediately to prevent a crash
    if total_posts == 0:
        return {
            "total_posts": 0,
            "total_creators": 0,
            "avg_likes": 0,
            "avg_engagement": 0
        }

    creators = set()
    total_likes = 0
    total_engagement = 0

    for post in posts:

        creators.add(post.creator)
        total_likes += post.likes

        total_engagement += (
            post.likes +
            post.comments +
            post.shares
        )

    avg_likes = total_likes / total_posts
    avg_engagement = total_engagement / total_posts

    return {
        "total_posts": total_posts,
        "total_creators": len(creators),
        "avg_likes": round(avg_likes, 2),
        "avg_engagement": round(avg_engagement, 2)
    }