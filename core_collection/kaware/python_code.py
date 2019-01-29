#!/usr/bin/env python3

""" An example entry to test the kernel/entry awareness feature.
"""

def show(__kernel__=None, __entry__=None):
    """ This entry can perform some introspection and see if it has access to 'kernel' and 'entry'
    """

    print("Hello, I am kaware entry, my kernel is '{}', my entry is '{}'".format(__kernel__, __entry__))

    if __kernel__:
        core_collection_entry = __kernel__.get_cached('core_collection')
        print("Cached core_collection = {}".format(core_collection_entry))

    if __entry__:
        print("This entry's name is {}".format(__entry__.get_name()))
        print("This entry's path is {}".format(__entry__.get_path()))


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    #
    show()

