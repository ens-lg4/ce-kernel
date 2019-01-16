#!/usr/bin/env python3

# Find a given name in the given or stored index

def show_map(name_2_path):
    """ Show the whole name_2_path index of this collection.
    """

    from pprint import pprint
    pprint(name_2_path)


def find_one(name, name_2_path):
    """ Find a relative path of the named entry in this collection entry's index.
    """

    print('requested entry name = "{}"'.format(name))
    path = name_2_path.get(name)
    if path:
        print('found entry path = "{}"'.format(path))
    else:
        print('entry path not found')

    return path


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #

    show_map({"alpha" : 10, "beta" : 200})

    returned_path = find_one('second', { "first" : "path/to/the/first", "second" : "path/to/the/second" })
    print("returned_path = {}\n".format(returned_path))
