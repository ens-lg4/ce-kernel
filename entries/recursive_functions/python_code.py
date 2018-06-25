#!/usr/bin/env python3

# Example recursive functions

def fibonacci(n):
    if n==0 or n==1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)


def factorial(n):
    if n<1:
        return 1
    else:
        return n * factorial(n-1)


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    for i in range(7):
        print("fibonacci({}) = {}".format(i, fibonacci(i)))
    print("")

    for i in range(7):
        print("factorial({}) = {}".format(i, factorial(i)))
    print("")
