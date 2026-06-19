def merge_sort(posts, key):

    if len(posts) <= 1:
        return posts

    mid = len(posts) // 2

    left = merge_sort(posts[:mid], key)
    right = merge_sort(posts[mid:], key)

    return merge(left, right, key)


def merge(left, right, key):

    result = []

    i = 0
    j = 0

    while i < len(left) and j < len(right):

        if getattr(left[i], key) > getattr(right[j], key):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result