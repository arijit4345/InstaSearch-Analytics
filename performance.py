import time

from search import linear_search
from hashmap_search import creator_search


def compare_search(posts, creator_index):

    keyword = "alex"

    # Linear Search Timing
    start = time.perf_counter()

    linear_search(posts, keyword)

    linear_time = time.perf_counter() - start

    # Hash Search Timing
    start = time.perf_counter()

    creator_search(
        creator_index,
        keyword
    )

    hash_time = time.perf_counter() - start

    return {
        "linear_time": linear_time,
        "hash_time": hash_time
    }