from functools import reduce

def guess_path(tree, words):
    def build_path(acc, word):
        tree, path_parts = acc

        path_parts[-1].append(word)

        key = ' '.join(path_parts[-1])
        if key in tree:
            tree = tree[key]
            #path_parts[-1] = key 
            path_parts.append([])

        return (tree, path_parts)

    tree, path_lists = reduce(build_path, words, (tree, [[]]))
    return [' '.join(p) for p in path_lists if p]
    
