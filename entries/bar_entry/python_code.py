#!/usr/bin/env python3

# Example bar_entry's code


def bar(alpha, beta, gamma, delta, **rest):
    print('alpha = "{}", beta = "{}", gamma = "{}", delta = "{}"'.format(alpha,beta,gamma,delta))
    for k in rest:
        print('Rest {} : {}'.format(k,rest[k]))
    return 123, 456


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    r = bar(10, 20, 30, 40)
    print("R_bar = {}\n".format(r))
