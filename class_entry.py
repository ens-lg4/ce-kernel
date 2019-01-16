#!/usr/bin/env python3

import os
import utils


core_repository_path = os.path.dirname( os.path.realpath(__file__) )    # depends on relative position of THIS FILE in the repository
base_collection_path = os.path.join(core_repository_path, 'core_collection', 'base_collection')
core_collection_path = os.path.join(core_repository_path, 'core_collection')
user_collection_path = os.path.join(core_repository_path, 'words_collection')


class MicroKernel:
    def __init__(self, parameters_location=('parameters.json',[]), meta_location=('meta.json',[]), code_container_name='python_code'):
        self.parameters_location    = parameters_location
        self.meta_location          = meta_location
        self.code_container_name    = code_container_name
        self.entry_cache            = {}

        self.collection_search_order = [ base_collection_path, core_collection_path, user_collection_path ]

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

                collection_obj.get_metas()
                if collection_obj.has_meta:         # FIXME: better check if the entry ->CAN('find_one')
                    local_path = collection_obj.call('find_one', { 'name' : entry_name} )
                    if local_path:
                        full_path = collection_obj.get_path(local_path)
                        break
                else:
                    print("{} doesn't contain meta".format(collection_path))

            if full_path:
                cached_entry = Entry(full_path, kernel=self)
        return cached_entry


default_kernel_instance = MicroKernel()


class Entry:
    def __new__(cls, entry_path, entry_name=None, parent_entry=None, kernel=default_kernel_instance):

        entry_name = entry_name or os.path.basename(entry_path)

        cached_entry = kernel.get_cached(entry_name)
        if cached_entry:
            return cached_entry
        else:
            self = super(Entry, cls).__new__(cls)

            print("__new__ Entry({})".format(entry_path))
            self.entry_path     = entry_path
            self.entry_name     = entry_name
            self.parent_entry   = parent_entry
            self.kernel         = kernel

            ## Placeholders for lazy loading:
            #
            self.module_object  = None
            self.meta           = None
            self.has_meta       = None
            self.parameters     = None

            kernel.encache_entry( self.entry_name, self )

            return self


    def get_path(self, filename=None):
        if filename:
            return os.path.join(self.entry_path, filename)
        else:
            return self.entry_path


    def get_name(self):
        if not self.entry_name:
            self.entry_name = os.path.basename(self.entry_path)

        return self.entry_name


    def get_module_object(self):
        self.module_object = self.module_object or utils.get_entrys_python_module(self.entry_path, code_container_name=self.kernel.code_container_name)

        return self.module_object


    def parent_loaded(self):
        if self.parent_entry==None:     # lazy-loading condition
            parent_entry_name = self.get_metas().get('parent_entry_name', None)
            if parent_entry_name:
                self.parent_entry = self.kernel.find_Entry(parent_entry_name)   # in case we get a False, it should stick and not cause another find_Entry() in future
            else:
                self.parent_entry = False

        return self.parent_entry


    def get_metas(self):
        if self.meta==None:             # lazy-loading condition
            meta_rel_path, meta_struct_path = self.kernel.meta_location
            self.meta, self.has_meta = utils.quietly_load_json_config( self.get_path(meta_rel_path), meta_struct_path )

        return self.meta


    def get_parameters(self):
        if self.parameters==None:       # lazy-loading condition
            parameters_rel_path, parameters_struct_path = self.kernel.parameters_location
            own_parameters, has_parameters = utils.quietly_load_json_config( self.get_path(parameters_rel_path), parameters_struct_path )

            if self.parent_loaded():
                self.parameters = utils.merged_dictionaries(self.parent_entry.get_parameters(), own_parameters)
            else:
                self.parameters = own_parameters

        return self.parameters


    def get_param(self, param_name):
        return self.get_parameters().get(param_name, None)


    def set_param(self, param_name, param_value):
        self.get_parameters()[param_name] = param_value


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


    def print_help(self, function_name):
        """ Print available information about the named method.
        """

        print( "Method: {}".format( function_name ) )
        try:
            ancestry_path = []
            function_object = self.reach_method(function_name, _ancestry_path=ancestry_path)
            print( "Defined in: {}".format( function_object.__module__ ))
            print( "Ancestry path: {}".format( ' --> '.join(ancestry_path) ))
            print( "DocString: {}".format( function_object.__doc__ ))
        except NameError as e:
            print( str(e) )


    def call(self, function_name, override_params=None, main_params=None):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and possibly also **kwargs.
        """

        main_params     = main_params or self.get_parameters()
        merged_params   = utils.merged_dictionaries(main_params, override_params) if override_params else main_params

        function_object = self.reach_method(function_name)
        return utils.free_access(function_object, merged_params)


if __name__ == '__main__':

    print(core_repository_path)
    foo_entry = Entry(core_collection_path + '/foo_entry')

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

    ## direct inheritance from param_entry (via meta.parent_entry_name):
    #
    latin = default_kernel_instance.find_Entry('latin')
    print(latin.get_parameters())
    print("")

    ## direct inheritance from latin (and so indirect from param_entry):
    #
    english = default_kernel_instance.find_Entry('english')
    print(english.get_parameters())
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

    params_entry.print_help('show')

    core_collection_entry = default_kernel_instance.find_Entry('core_collection')
    core_collection_entry.print_help('show_map')
    core_collection_entry.print_help('find_one')

    core_collection_entry.print_help('find_two')
