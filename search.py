def linear_search(posts, keyword):

    results = []

    keyword = keyword.lower()

    for post in posts:

        if (keyword in post.caption.lower() or
            keyword in post.creator.lower() or
            keyword in post.hashtags.lower()):

            results.append(post)

    return results