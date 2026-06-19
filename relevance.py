def relevance_search(posts, keyword):

    keyword = keyword.lower()

    scored_posts = []

    for post in posts:

        score = 0

        score += post.caption.lower().count(keyword)

        score += post.hashtags.lower().count(keyword)

        score += post.creator.lower().count(keyword)

        if score > 0:
            scored_posts.append(
                (score, post)
            )

    scored_posts.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        post
        for score, post
        in scored_posts
    ]