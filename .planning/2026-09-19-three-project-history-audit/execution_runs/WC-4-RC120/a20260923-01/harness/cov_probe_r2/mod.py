def branchy(x):
    if x:
        return 1
    return 0


def never_called(a, b, c, d):
    total = a + b
    if total > 10:
        total -= 1
    for _ in range(3):
        total += c
    while c > 0:
        c -= 1
        total += d
    return total


print(branchy(1))
