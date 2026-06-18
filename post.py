class Post:

    def __init__(self, post_id, creator,
                 hashtags, caption,
                 likes, comments,
                 shares, date):

        self.post_id = post_id
        self.creator = creator
        self.hashtags = hashtags
        self.caption = caption
        self.likes = int(likes)
        self.comments = int(comments)
        self.shares = int(shares)
        self.date = date