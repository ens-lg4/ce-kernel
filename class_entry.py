#!/usr/bin/env python3

__version__ = '0.0.4'   # Try not to forget to update it!

import os
import utils


core_repository_path = os.path.dirname( os.path.realpath(__file__) )    # depends on relative position of THIS FILE in the repository
base_collection_path = os.path.join(core_repository_path, 'core_collection', 'base_collection')
core_collection_path = os.path.join(core_repository_path, 'core_collection')
user_collection_path = os.path.join(core_repository_path, 'words_collection')


class MicroKernel:
    def __init__(self, parameters_location=('parameters.json',[]), code_container_name='python_code'):
        self.parameters_location    = parameters_location
        self.code_container_name    = code_container_name
        self.entry_cache            = {}

        self.collection_search_order = [ base_collection_path, core_collection_path, user_collection_path ]

    def get_version(self):
        return __version__


    def get_cached(self, entry_name):
        if entry_name in self.entry_cache:              # FIXME: make sure to spot-clear the cache as we add/remove/move entries on disk
            print('CACHE ------> {}'.format(entry_name))
            return self.entry_cache[entry_name]
        else:
            return None


    def encache_entry(self, entry_name, entry_object):
        print('CACHE <====== {}'.format(entry_name))
        self.entry_cache[entry_name] = entry_object


    def find_Entry(self, entry_name):
        print("find_Entry({})".format(entry_name))

        cached_entry = self.get_cached(entry_name)     # FIXME: make sure to spot-clear the cache as we add/remove/move entries on disk
        if not cached_entry:

            full_path = None
            for collection_path in self.collection_search_order:

                collection_obj = Entry(collection_path, kernel=self)

                if collection_obj.reach_method('find'):     # FIXME: maybe preserve the function_object once found, to run it faster?
                    full_path = collection_obj.call('find', { 'entry_name' : entry_name} )
                    if full_path:
                        break
                else:
                    print("{} doesn't implement or inherit the 'find' method".format(collection_path))

            if full_path:
                cached_entry = Entry(full_path, kernel=self)
        return cached_entry


default_kernel_instance = MicroKernel()


class Entry:
    def __new__(cls, entry_path=None, own_parameters=None, kernel=default_kernel_instance):

        entry_name = None
        if entry_path:
            entry_name = os.path.basename(entry_path)

            cached_entry = kernel.get_cached(entry_name)
            if cached_entry:
                return cached_entry

        self = super(Entry, cls).__new__(cls)

        print("__new__ Entry({})".format(entry_path))
        self.entry_path     = entry_path
        self.kernel         = kernel
        self.own_parameters = own_parameters

        ## Placeholders for lazy loading:
        #

        self.parent_entry   = None
        self.module_object  = None

        if entry_name:
            kernel.encache_entry( entry_name, self )

        return self


    def get_path(self, filename=None):
        if filename:
            return os.path.join(self.entry_path, filename)
        else:
            return self.entry_path


    def get_name(self):
        return self.entry_path and os.path.basename(self.entry_path)


    def parameters_loaded(self):
        if self.own_parameters==None:       # lazy-loading condition
            parameters_rel_path, parameters_struct_path = self.kernel.parameters_location
            self.own_parameters, _ = utils.quietly_load_json_config( self.get_path(parameters_rel_path), parameters_struct_path )

        return self.own_parameters


    def parent_loaded(self):
        if self.parent_entry==None:     # lazy-loading condition
            parent_entry_name = self.parameters_loaded().get('parent_entry_name', None)
            if parent_entry_name:
                self.parent_entry = self.kernel.find_Entry(parent_entry_name)   # in case we get a False, it should stick and not cause another find_Entry() in future
            else:
                self.parent_entry = False

        return self.parent_entry


    def __getitem__(self, param_name):
        own_parameters = self.parameters_loaded()

        if param_name in own_parameters:
            return own_parameters[param_name]
        elif self.parent_loaded():
            return self.parent_entry[param_name]
        else:
            return None


    def __setitem__(self, param_name, param_value):
        self.parameters_loaded()[param_name] = param_value


    def get_module_object(self):
        if self.module_object==None:    # lazy-loading condition
            self.module_object = utils.get_entrys_python_module(self.entry_path, code_container_name=self.kernel.code_container_name) or False

        return self.module_object


    def reach_method(self, function_name, _ancestry_path=None):
        """ Find a method for the given entry - either its own or belonging to one of its parents.
        """

        if _ancestry_path == None:
            _ancestry_path = []

        _ancestry_path += [ self.get_name() ]
        try:
            module_object   = self.get_module_object()
            function_object = getattr(module_object, function_name)
        except (ImportError, AttributeError) as e:
            if self.parent_loaded():
                return self.parent_entry.reach_method(function_name, _ancestry_path)
            else:
                raise NameError( "could not find the method '{}' along the ancestry path '{}'".format(function_name, ' --> '.join(_ancestry_path) ) )

        return function_object


    def generate_merged_parameters(self):
        own_parameters = self.parameters_loaded()

        if self.parent_loaded():
            return utils.merged_dictionaries(self.parent_entry.parameters_loaded(), own_parameters)
        else:
            return own_parameters


    def call(self, function_name, call_specific_params=None, entry_wide_params=None):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and possibly also **kwargs.
        """

        function_object     = self.reach_method(function_name)

        entry_wide_params   = entry_wide_params or self.generate_merged_parameters()
        merged_params       = utils.merged_dictionaries(entry_wide_params, call_specific_params) if call_specific_params else entry_wide_params

        merged_params.update( {             # These special parameters are non-overridable at the moment. Should they be?
            '__kernel__'    : self.kernel,
            '__entry__'     : self,
        } )

        return utils.free_access(function_object, merged_params)


if __name__ == '__main__':

    print("Kernel version = {}".format(default_kernel_instance.get_version()))

    print(core_repository_path)

    uncached_entry = Entry(own_parameters={'son': 'Lenny', 'daughter': 'Isabella'})
    print("Son: {}, Daughter: {}".format(uncached_entry['son'], uncached_entry['daughter']))

    foo_entry = Entry(core_collection_path + '/foo_entry')

    p, q = foo_entry.call('foo', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    foo_entry['fourth'] = 'vierte'

    foo2 = foo_entry['second']
    foo4 = foo_entry['fourth']
    print("foo2 = {}, foo4 = {}\n".format(foo2, foo4))

    dir_path    = foo_entry.get_path()
    file_path   = foo_entry.get_path('abracadabra.txt')
    print("dir_path = {}, file_path = {}\n".format(dir_path, file_path))

    bar_entry = Entry(core_collection_path + '/bar_entry')

    p, q = bar_entry.call('bar', { 'alpha' : 100, 'beta' : 200, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_bar = {}, Q_bar = {}\n".format(p,q))


    ## Switching to another kernel_instance would mean all other classes (including collections would have to comply with changes!)
    #
#    iter_entry_kernel_instance = MicroKernel( parameters_location=('parameters.json',["alternative", "place", 1]) )
#    iterative_entry = iter_entry_kernel_instance.find_Entry('iterative_functions')

    iterative_entry = default_kernel_instance.find_Entry('iterative_functions')
    recursive_entry = default_kernel_instance.find_Entry('recursive_functions')

    for funcs_entry in (iterative_entry, recursive_entry):
        entry_name  = funcs_entry.get_name()
        fib_n       = funcs_entry.call('fibonacci', {} )
        fact_n      = funcs_entry.call('factorial', {} )
        print("{} : fib(n) = {}, fact(n) = {}\n".format(entry_name, fib_n, fact_n))

    params_entry    = default_kernel_instance.find_Entry('params_entry')
    params_dict     = params_entry.call('show', {'alpha' : 'Hello', 'gamma' : 'World', 'delta' : 420} )
    print(" 'show' method when called via API returned : {}\n".format(params_dict))

    try:
        params_entry.call('nonexistent_func', { 'alpha' : 123 })
    except NameError as e:
        print(str(e) + "\n")

    ## direct inheritance from param_entry (via parent_entry_name):
    #
    latin = default_kernel_instance.find_Entry('latin')
    print(latin.generate_merged_parameters())
    print("")

    ## direct inheritance from latin (and so indirect from param_entry):
    #
    english = default_kernel_instance.find_Entry('english')
    print(english.generate_merged_parameters())
    print("")

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


    ## what happens if the entry could not be found?
    #
    gaelic_entry = default_kernel_instance.find_Entry('gaelic')
    print(gaelic_entry)
    print("")

    help_entry = default_kernel_instance.find_Entry('help')
    help_entry.call('entry', { 'entry_name': 'kaware'})
    help_entry.call('method', { 'entry_name': 'cli_parser', 'method_name': 'cli_parse'})
