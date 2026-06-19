from post import Post

def load_posts(filename):

    posts = []

    with open(filename, "r", encoding="utf-8") as file:

        next(file)  # Skip header

        for line in file:

            data = line.strip().split("|")

            post = Post(
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],
                data[5],
                data[6],
                data[7]
            )

            posts.append(post)

    return posts