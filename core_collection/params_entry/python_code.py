#!/usr/bin/env python3

# Just show all the received parameters


def show(**params):

    for name in sorted(params):
        print('Param {} : {}'.format(name,params[name]))

    # return all the parameters as a dictionary:
    #
    return params


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    r = show(alpha='hello', gamma='world', delta=42)
    print("'show' method returned : {}\n".format(r))
