def product(*args, repeat=1):
    pools = [tuple(pool) for pool in args] * repeat
    results = [[]]

    for pool in pools:
        results = [x + [y] for x in results for y in pool]

    return results
