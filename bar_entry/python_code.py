#!/usr/bin/env python3

""" Another example entry that is not a part of any collection
"""


def bar(alpha, beta, gamma, **rest):
    """ bar() method with its positional and **rest parameters
    """
    print('alpha = "{}", beta = "{}", gamma = "{}"'.format(alpha,beta,gamma))
    print('---- Rest: ----')
    for k in rest:
        print('Rest {} : {}'.format(k,rest[k]))
    return 123, 456


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    r = bar(10, 20, gamma=30, delta=40)
    print("R_bar = {}\n".format(r))
