#!/usr/bin/env python3


kernel  = None
entry   = None

def show():
    """ This entry can perform some introspection and see if it has access to 'kernel' and 'entry'
    """

    print("Hello, I am kaware entry, my kernel is '{}', my entry is '{}'".format(kernel, entry))

    if kernel:
        core_collection_entry = kernel.get_cached('core_collection')
        print("Cached core_collection = {}".format(core_collection_entry))

    if entry:
        print("This entry's name is {}".format(entry.get_name()))
        print("This entry's path is {}".format(entry.get_path()))


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    #
    show()

