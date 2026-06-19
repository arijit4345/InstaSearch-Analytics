def popular_creators(posts):

    creators = {}

    for post in posts:

        creator = post.creator

        engagement = (
            post.likes +
            post.comments +
            post.shares
        )

        if creator not in creators:
            creators[creator] = 0

        creators[creator] += engagement

    ranked = sorted(
        creators.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked