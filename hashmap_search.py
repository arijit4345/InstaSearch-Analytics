def build_creator_index(posts):

    creator_index = {}

    for post in posts:

        creator = post.creator.lower()

        if creator not in creator_index:
            creator_index[creator] = []

        creator_index[creator].append(post)

    return creator_index

def build_hashtag_index(posts):

    hashtag_index = {}

    for post in posts:

        hashtags = post.hashtags.split(",")

        for tag in hashtags:

            tag = tag.lower().strip()

            if tag not in hashtag_index:
                hashtag_index[tag] = []

            hashtag_index[tag].append(post)

    return hashtag_index

def creator_search(index, creator):

    return index.get(
        creator.lower(),
        []
    )

def hashtag_search(index, hashtag):

    return index.get(
        hashtag.lower(),
        []
    )