def linear_search(posts, search_query):
    results = []
    
    # 1. Parse the smart query string
    tokens = search_query.split()
    target_creator = ""
    target_hashtags = []
    target_text_tokens = []
    
    for token in tokens:
        if token.startswith("@") and not target_creator:
            target_creator = token[1:].lower() # Take the first @ user
        elif token.startswith("#"):
            target_hashtags.append(token[1:].lower())
        else:
            target_text_tokens.append(token.lower())
            
    # Combine remaining text into one string
    target_keyword = " ".join(target_text_tokens)

    # 2. Run the logic
    for post in posts:
        match = True
        
        # Rule A: Creator check
        if target_creator and target_creator not in post.creator.lower():
            match = False
            
        # Rule B: Hashtags check (Post must contain ALL requested tags)
        if match and target_hashtags:
            post_tags = post.hashtags.lower()
            if not all(tag in post_tags for tag in target_hashtags):
                match = False
                
        # Rule C: Text check (Searches across caption, creator, OR hashtags)
        if match and target_keyword:
            if (target_keyword not in post.caption.lower() and
                target_keyword not in post.creator.lower() and
                target_keyword not in post.hashtags.lower()):
                match = False
                
        if match:
            results.append(post)

    return results