def is_subsquence(a,b):
    b = iter(b)
    return all(i in b for i in a)



