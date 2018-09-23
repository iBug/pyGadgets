def to_b(n, l):
    return [int(i) for i in "{{:0{}b}}".format(l).format(n)]


def search_i(f, l):
    return [i for i in range(2**l) if f(* (to_b(i, l)))]


def search(f, l):
    print(" ".join(str(i) for i in search_i(f, l)))
