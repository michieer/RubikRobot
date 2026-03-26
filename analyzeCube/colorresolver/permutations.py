def permutations(iterable, r=None):
    """
    From https://github.com/python/cpython/blob/master/Modules/itertoolsmodule.c
    """
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    indices = list(range(n))
    cycles = list(range(n - r + 1, n + 1))[::-1]
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(list(range(r))):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i + 1 :] + indices[i : i + 1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return


odd_cube_center_color_permutations = (
    ("Wh", "OR", "Gr", "Rd", "Bu", "Ye"),
    ("Wh", "Gr", "Rd", "Bu", "OR", "Ye"),
    ("Wh", "Bu", "OR", "Gr", "Rd", "Ye"),
    ("Wh", "Rd", "Bu", "OR", "Gr", "Ye"),
    ("Ye", "Bu", "Rd", "Gr", "OR", "Wh"),
    ("Ye", "Gr", "OR", "Bu", "Rd", "Wh"),
    ("Ye", "Rd", "Gr", "OR", "Bu", "Wh"),
    ("Ye", "OR", "Bu", "Rd", "Gr", "Wh"),
    ("OR", "Ye", "Gr", "Wh", "Bu", "Rd"),
    ("OR", "Wh", "Bu", "Ye", "Gr", "Rd"),
    ("OR", "Gr", "Wh", "Bu", "Ye", "Rd"),
    ("OR", "Bu", "Ye", "Gr", "Wh", "Rd"),
    ("Gr", "Ye", "Rd", "Wh", "OR", "Bu"),
    ("Gr", "Wh", "OR", "Ye", "Rd", "Bu"),
    ("Gr", "Rd", "Wh", "OR", "Ye", "Bu"),
    ("Gr", "OR", "Ye", "Rd", "Wh", "Bu"),
    ("Rd", "Ye", "Bu", "Wh", "Gr", "OR"),
    ("Rd", "Wh", "Gr", "Ye", "Bu", "OR"),
    ("Rd", "Bu", "Wh", "Gr", "Ye", "OR"),
    ("Rd", "Gr", "Ye", "Bu", "Wh", "OR"),
    ("Bu", "Wh", "Rd", "Ye", "OR", "Gr"),
    ("Bu", "Ye", "OR", "Wh", "Rd", "Gr"),
    ("Bu", "Rd", "Ye", "OR", "Wh", "Gr"),
    ("Bu", "OR", "Wh", "Rd", "Ye", "Gr"),
)

len_even_cube_center_color_permutations = 432

even_cube_center_color_permutations = ""  # Not used for 3x3x3
