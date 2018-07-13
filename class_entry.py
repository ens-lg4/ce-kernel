#!/usr/bin/env python3

import os
import utils

class Entry:
    def __init__(self, entry_path, entry_name=None, parent_entry=None, parameters_location=('parameters.json',[]), meta_location=('meta.json',[]) ):
        self.entry_path     = entry_path
        self.entry_name     = entry_name or os.path.basename(self.entry_path)
        self.parent_entry   = parent_entry

        ## Placeholders for lazy loading:
        #
        self.module_object  = None
        self.meta           = None
        self.parameters     = None

        self.parameters_rel_path, self.parameters_struct_path   = parameters_location
        self.meta_rel_path, self.meta_struct_path               = meta_location


    def get_name(self):
        return self.entry_name


    def get_path(self, filename=None):
        if filename:
            return os.path.join(self.entry_path, filename)
        else:
            return self.entry_path


    def get_module_object(self):
        self.module_object = self.module_object or utils.get_entrys_python_module(self.entry_path)

        return self.module_object


    def get_metas(self):
        self.meta = self.meta or utils.quietly_load_json_config( self.get_path(self.meta_rel_path), self.meta_struct_path )

        return self.meta


    def get_parameters(self):
        if not self.parameters:
            own_parameters = utils.quietly_load_json_config( self.get_path(self.parameters_rel_path), self.parameters_struct_path )

            if self.parent_entry:
                self.parameters = utils.merged_dictionaries(self.parent_entry.get_parameters(), own_parameters)
            else:
                self.parameters = own_parameters

        return self.parameters


    def get_param(self, param_name):

        return self.get_parameters().get(param_name, None)


    def set_param(self, param_name, param_value):

        self.get_parameters()[param_name] = param_value


    def call(self, function_name, override_params=None, main_params=None):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and possibly also **kwargs.
        """

        module_object   = self.get_module_object()
        main_params     = main_params or self.get_parameters()
        merged_params   = utils.merged_dictionaries(main_params, override_params) if override_params else main_params

        try:
            return utils.free_access(module_object, function_name, merged_params)
        except NameError as e:
            if self.parent_entry:
                self.parent_entry.call(function_name, main_params=merged_params)
            else:
                raise e


if __name__ == '__main__':

    foo_entry = Entry('entries/foo_entry')

    p, q = foo_entry.call('foo', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    foo_entry.set_param('fourth', 'vierte')

    foo2 = foo_entry.get_param('second')
    foo4 = foo_entry.get_param('fourth')
    print("foo2 = {}, foo4 = {}\n".format(foo2, foo4))

    dir_path    = foo_entry.get_path()
    file_path   = foo_entry.get_path('abracadabra.txt')
    print("dir_path = {}, file_path = {}\n".format(dir_path, file_path))
    print("State of weather : {}\n".format(foo_entry.get_metas().get('weather')))

    bar_entry = Entry('entries/bar_entry')

    p, q = bar_entry.call('bar', { 'alpha' : 100, 'beta' : 200, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_bar = {}, Q_bar = {}\n".format(p,q))


    iterative_entry = Entry('entries/iterative_functions', parameters_location=('parameters.json',["alternative", "place", 1]))
    recursive_entry = Entry('entries/recursive_functions')

    for funcs_entry in (iterative_entry, recursive_entry):
        entry_name  = funcs_entry.get_name()
        fib_n       = funcs_entry.call('fibonacci', {} )
        fact_n      = funcs_entry.call('factorial', {} )
        print("{} : fib(n) = {}, fact(n) = {}\n".format(entry_name, fib_n, fact_n))

    params_entry    = Entry('entries/params_entry')
    params_dict     = params_entry.call('show', {'alpha' : 'Hello', 'gamma' : 'World', 'delta' : 420} )
    print(" 'show' method when called via API returned : {}\n".format(params_dict))

    try:
        params_entry.call('nonexistent_func', { 'alpha' : 123 })
    except NameError as e:
        print(str(e) + "\n")

    ## direct inheritance from param_entry:
    #
    latin = Entry('entries/latin_words', parent_entry=params_entry)
    print(latin.get_parameters())

    ## direct inheritance from latin (and so indirect from param_entry):
    #
    english = Entry('entries/english_words', parent_entry=latin)
    print(english.get_parameters())

    latin.call('latin_only', { 'alpha' : 'Hello' })
    print("")
    latin.call('both', { 'alpha' : 'Hello' })
    print("")
    english.call('latin_only', { 'alpha' : 'Hello' })
    print("")
    english.call('english_only', { 'alpha' : 'Hello' })
    print("")
    english.call('both', { 'alpha' : 'Hello' })
    print("")
    english.call('show', { 'alpha' : 'Hello' })
    print("")
    try:
        english.call('neither', { 'nu' : 789, 'omega' : 890 })
    except NameError as e:
        print(str(e) + "\n")
