import os


def simple_add(a, b):
    return a + b


def classify_number(x):
    if x < 0:
        return "negative"
    elif x == 0:
        return "zero"
    elif x < 10:
        return "small"
    elif x < 100:
        return "medium"
    else:
        return "large"


def complicated_process(data):
    total = 0

    for item in data:
        if item > 0:
            if item % 2 == 0:
                total += item
            else:
                total -= item
        else:
            if item == 0:
                total += 1
            else:
                total -= 1

    return total