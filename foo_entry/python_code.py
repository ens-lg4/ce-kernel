#!/usr/bin/env python3

""" Example entry that is not a part of any collection
"""


def foo(alpha, beta, gamma, delta=4444, epsilon=55555, zeta=666666):
    """ foo() method with its positional and optional parameters
    """
    print('alpha = "{}", beta = "{}", gamma = "{}", delta = "{}", epsilon = "{}", zeta = "{}"'.format(alpha,beta,gamma,delta,epsilon,zeta))
    return 99, 88


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    r1 = foo(10, 20, 30, epsilon=70)
    print("R_foo = {}\n".format(r1))
