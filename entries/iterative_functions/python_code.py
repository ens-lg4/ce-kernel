#!/usr/bin/env python3

# Example iterative functions

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a


def factorial(n):
    prod = 1
    for i in range(1,n+1):
        prod *= i
    return prod


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    for i in range(7):
        print("fibonacci({}) = {}".format(i, fibonacci(i)))
    print("")

    for i in range(7):
        print("factorial({}) = {}".format(i, factorial(i)))
    print("")
