#!/usr/bin/env python3

# Just show all the received parameters


def english_only(**params):

    for name in sorted(params):
        print('english_only.Param {} : {}'.format(name,params[name]))

    # return all the parameters as a dictionary:
    #
    return params


def both(**params):

    for name in sorted(params):
        print('both_english.Param {} : {}'.format(name,params[name]))

    # return all the parameters as a dictionary:
    #
    return params

