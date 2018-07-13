#!/usr/bin/env python3

# Just show all the received parameters


def latin_only(**params):

    for name in sorted(params):
        print('latin_only.Param {} : {}'.format(name,params[name]))

    # return all the parameters as a dictionary:
    #
    return params


def both(**params):

    for name in sorted(params):
        print('both_latin.Param {} : {}'.format(name,params[name]))

    # return all the parameters as a dictionary:
    #
    return params

