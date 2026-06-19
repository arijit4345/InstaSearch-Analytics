def get_statistics(posts):

    total_posts = len(posts)

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