def trending_hashtags(posts):

    hashtag_count = {}

    for post in posts:

        hashtags = post.hashtags.split(",")

        for tag in hashtags:

            tag = tag.strip().lower()

            if tag not in hashtag_count:
                hashtag_count[tag] = 0

            hashtag_count[tag] += 1

    return sorted(
        hashtag_count.items(),
        key=lambda x: x[1],
        reverse=True
    )
