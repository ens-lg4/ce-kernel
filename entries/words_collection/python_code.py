#!/usr/bin/env python3

# Example bar_entry's code


def find_one(name, name_2_path):
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
    returned_path = find_one('first', { "first" : "path/to/the/first", "second" : "path/to/the/second" })
    print("returned_path = {}\n".format(returned_path))
