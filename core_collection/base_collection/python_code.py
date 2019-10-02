#!/usr/bin/env python3

""" Find a given entry_name in the given or stored index
"""


def show_map(name_2_path):
    """ Show the whole name_2_path index of this collection.
    """

    from pprint import pprint
    pprint(name_2_path)


def byname(entry_name, name_2_path, collections_searchpath, __entry__=None, __kernel__=None):
    """ Find a relative path of the named entry in this collection entry's index.
    """

    relative_path   = name_2_path.get(entry_name)

    if relative_path:
        if __entry__:
            full_path = __entry__.get_path(relative_path)
            return __kernel__.bypath( full_path )
        else:
            return relative_path
    elif collections_searchpath:
        for subcollection_name in collections_searchpath:
            subcollection_local     = name_2_path.get(subcollection_name)
            subcollection_object    = __kernel__.byname(subcollection_name, __entry__ if subcollection_local else None)
            found_object            = __kernel__.byname(entry_name, subcollection_object)
            if found_object:
                return found_object
    
    return None


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #

    show_map({"alpha" : 10, "beta" : 200})

    returned_path = byname('second', { "first" : "relative/path/to/the/first", "second" : "relative/path/to/the/second" })
    print("returned_path = {}\n".format(returned_path))
