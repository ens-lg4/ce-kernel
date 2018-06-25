#!/usr/bin/env python3

import os
import utils

class Entry:
    def __init__(self, entry_name, entry_path):
        self.entry_name = entry_name
        self.entry_path = entry_path


    def get_name(self):
        return self.entry_name


    def get_path(self, filename=None):
        if filename:
            return os.path.join(self.entry_path, filename)
        else:
            return self.entry_path


    def call(self, function_name, given_arg_dict):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and possibly also **kwargs.
        """

        module_object   = utils.get_cached_module(self.entry_name, self.entry_path)

        return utils.access(module_object, function_name, given_arg_dict)


if __name__ == '__main__':

    foo_entry = Entry('foo_entry', 'entries/foo_entry')

    p, q = foo_entry.call('foo', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    dir_path    = foo_entry.get_path()
    file_path   = foo_entry.get_path('abracadabra.txt')
    print("dir_path = {}, file_path = {}\n".format(dir_path, file_path))


    iterative_entry = Entry('iterative_functions', 'entries/iterative_functions')
    recursive_entry = Entry('recursive_functions', 'entries/recursive_functions')

    for funcs_entry in (iterative_entry, recursive_entry):
        entry_name      = funcs_entry.get_name()
        fib_5           = funcs_entry.call('fibonacci', {'n':5} )
        fact_5          = funcs_entry.call('factorial', {'n':5} )
        print("{} : fib(5) = {}, fact(5) = {}\n".format(entry_name, fib_5, fact_5))
