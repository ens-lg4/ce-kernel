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
            if subcollection_name.find('/')>=0:
                subcollection_object    = __kernel__.bypath(subcollection_name)
            else:
                subcollection_local     = name_2_path.get(subcollection_name)
                subcollection_object    = __kernel__.byname(subcollection_name, __entry__ if subcollection_local else None)

            found_object            = __kernel__.byname(entry_name, subcollection_object)
            if found_object:
                return found_object
    
    return None


def add_entry(entry_name, data=None, __entry__=None, __kernel__=None):
    """
        Usage example:
            clip byname --entry_name=words_collection add_entry --entry_name=xyz --data.foo.bar=1234 --data.baz=alpha
    """
    import os

    # Create the physical directory for the new entry:
    new_entry_full_path = __entry__.get_path(entry_name)
    print("add_entry: new_entry_full_path="+new_entry_full_path)
    os.makedirs(new_entry_full_path)      # FIXME: fail gracefully if directory path existed

    # Add the new entry to collection:
    __entry__.parameters_loaded()['name_2_path'][entry_name] = entry_name
    __entry__.update()

    if data==None:
        data = {}

    # Update parameters of the new entry:
    new_entry = __kernel__.bypath(new_entry_full_path)
    new_entry.parameters_loaded().update( data )
    new_entry.update()

    return new_entry


def delete_entry(entry_name, __entry__=None, __kernel__=None):
    """
        Usage example:
            clip byname --entry_name=words_collection delete_entry --entry_name=xyz
    """
    import shutil

    name_2_path = __entry__.parameters_loaded()['name_2_path']
    old_entry_full_path = __entry__.get_path(name_2_path[entry_name])
    print("delete_entry: old_entry_full_path="+old_entry_full_path)

    # Remove the old entry from collection:
    del name_2_path[entry_name]
    __entry__.update()

    # Remove the physical directory of the old entry:
    shutil.rmtree(old_entry_full_path)

    return __entry__


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #

    show_map({"alpha" : 10, "beta" : 200})

    returned_path = byname('second', { "first" : "relative/path/to/the/first", "second" : "relative/path/to/the/second" })
    print("returned_path = {}\n".format(returned_path))
