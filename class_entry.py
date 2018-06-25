#!/usr/bin/env python3

import os
import utils

class Entry:
    def __init__(self, entry_name, entry_path):
        self.entry_name = entry_name
        self.entry_path = entry_path
        self.load_own_meta()            # FIXME: switch to lazy-loading for efficiency
        self.load_own_parameters()      # FIXME: switch to lazy-loading for efficiency


    def get_name(self):
        return self.entry_name


    def get_path(self, filename=None):
        if filename:
            return os.path.join(self.entry_path, filename)
        else:
            return self.entry_path


    def load_own_parameters(self):
        self.parameters = utils.quietly_load_json_config( self.get_path('parameters.json') )


    def load_own_meta(self):
        self.meta = utils.quietly_load_json_config( self.get_path('meta.json') )


    def get_param(self, param_name):

        return self.parameters.get(param_name, None)


    def set_param(self, param_name, param_value):

        self.parameters[param_name] = param_value


    def overlay_params(self, overlaying_dict):

        underlying_dict = self.parameters

        if len(overlaying_dict):
            return { k : overlaying_dict.get(k, underlying_dict.get(k) ) for k in set(overlaying_dict) | set(underlying_dict) }
        else:
            return underlying_dict


    def call(self, function_name, given_arg_dict):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and possibly also **kwargs.
        """

        module_object   = utils.get_cached_module(self.entry_name, self.entry_path)
        merged_params   = self.overlay_params( given_arg_dict )

        return utils.access(module_object, function_name, merged_params)


if __name__ == '__main__':

    foo_entry = Entry('foo_entry', 'entries/foo_entry')

    p, q = foo_entry.call('foo', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    foo_entry.set_param('fourth', 'vierte')

    foo2 = foo_entry.get_param('second')
    foo4 = foo_entry.get_param('fourth')
    print("foo2 = {}, foo4 = {}\n".format(foo2, foo4))

    dir_path    = foo_entry.get_path()
    file_path   = foo_entry.get_path('abracadabra.txt')
    print("dir_path = {}, file_path = {}\n".format(dir_path, file_path))


    iterative_entry = Entry('iterative_functions', 'entries/iterative_functions')
    recursive_entry = Entry('recursive_functions', 'entries/recursive_functions')

    for funcs_entry in (iterative_entry, recursive_entry):
        entry_name  = funcs_entry.get_name()
        fib_n       = funcs_entry.call('fibonacci', {} )
        fact_n      = funcs_entry.call('factorial', {} )
        print("{} : fib(n) = {}, fact(n) = {}\n".format(entry_name, fib_n, fact_n))

    print("State of weather : {}\n".format(foo_entry.meta.get('weather')))
