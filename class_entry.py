#!/usr/bin/env python3

""" The kernel of the CE system.
    Provides two classes, MicroKernel and Entry.
"""

__version__ = '0.1.9'   # Try not to forget to update it!

import os
import utils


core_repository_path = os.path.dirname( os.path.realpath(__file__) )    # depends on relative position of THIS FILE in the repository


class MicroKernel:
    def __init__(self, parameters_location=('parameters.json',[]), code_container_name='python_code', entry_cache=None):
        self.parameters_location    = parameters_location
        self.code_container_name    = code_container_name
        self.entry_cache            = entry_cache


    def version(self):
        """
            Usage example:
                clip version
        """
        return __version__


    def get_kernel_path(self, file_name=None):
        """
            Usage example:
                clip get_kernel_path
                clip get_kernel_path --file_name=working_collection
        """
        if file_name:
            return os.path.join(core_repository_path, file_name)
        else:
            return core_repository_path


    def bypath(self, path, *args, **kwargs):
        """
            Usage example:
                clip bypath --path=foo_entry , foo --alpha=12 --beta=23 --gamma=34
        """
        print("KERNEL.bypath({}, {}, {})".format(path, args, kwargs))
        return Entry(*args, **kwargs, entry_path=path, kernel=self)


    def cached(self, entry_name):
        # entry_cache cannot be populated during __init__() because of circular references, so we lazy-load it
        if self.entry_cache==None:
            print("KERNEL.cached({}) - populating entry_cache".format(entry_name))
            self.entry_cache = {}
            self.entry_cache['core_collection']     = self.bypath( self.get_kernel_path('core_collection') )
            self.entry_cache['working_collection']  = self.bypath( self.get_kernel_path('working_collection') )

        return self.entry_cache.get(entry_name)


    def working_collection(self):
        return self.cached('working_collection')


    def byname(self, entry_name, collection_object=None):
        """
            Usage example:
                clip byname --entry_name=iterative_functions , factorial --n=6 , fibonacci --n=8
        """
        print("KERNEL.byname({})".format(entry_name))

        if not collection_object:
            cached_object = self.cached(entry_name)
            if cached_object:
                print("KERNEL.byname({}) was found in cache".format(entry_name))
                return cached_object
            else:
                collection_object = self.working_collection()

        return collection_object.call('byname', { 'entry_name' : entry_name} )


default_kernel_instance = MicroKernel()


class Entry:
    def __init__(self, entry_path=None, parent_entry=None, own_parameters=None, kernel=default_kernel_instance):
        print("__init__ Entry({}) -> {}".format(entry_path, self))
        self.entry_path     = entry_path
        self.parent_entry   = parent_entry
        self.own_parameters = own_parameters
        self.kernel         = kernel

        ## Placeholder(s) for lazy loading:
        #

        self.module_object  = None


    def get_path(self, file_name=None):
        """
            Usage example:
                clip byname --entry_name=words_collection , get_path
        """
        if file_name:
            if file_name.startswith('/'):
                return file_name
            else:
                return os.path.join(self.entry_path, file_name)
        else:
            return self.entry_path


    def get_name(self):
        return self.entry_path and os.path.basename(self.entry_path)


    def print(self, params=None, template=None):
        """
            Usage example:
                clip bypath foo_entry , print '--template=premier -> {} et troisieme -> {}' --params,=first,third
        """
        if params==None:
            params = sorted(self.parameters_loaded())

        if template==None:
            print( ', '.join([ "{}: {}".format(p, repr(self[p])) for p in params]))
        else:
            values = [repr(self[p]) for p in params]
            print(template.format(*values))


    def parameters_loaded(self):
        if self.own_parameters==None:       # lazy-loading condition
            parameters_rel_path, parameters_struct_path = self.kernel.parameters_location
            self.own_parameters, _ = utils.quietly_load_json_config( self.get_path(parameters_rel_path), parameters_struct_path )

        return self.own_parameters


    def update(self, data=None):   # FIXME: currently ignoring parameters_struct_path
        """
            Usage example:
                clip byname --entry_name=xyz , update --data.baz=beta
        """
        own_parameters = self.parameters_loaded()
        if data:
            own_parameters.update( data)

        parameters_rel_path, parameters_struct_path = self.kernel.parameters_location
        utils.store_structure_to_json_file(own_parameters, self.get_path(parameters_rel_path))

        return own_parameters


    def parent_loaded(self):
        if self.parent_entry==None:     # lazy-loading condition
            parent_entry_name = self.parameters_loaded().get('parent_entry_name', None)
            if parent_entry_name:
                if parent_entry_name.find('/')>=0:  # FIXME: parent_entry_name is a bad name
                    self.parent_entry = self.kernel.bypath( parent_entry_name )
                else:   # in case we get a False, it should stick   and not cause another byname() in future
                    self.parent_entry = self.kernel.byname( parent_entry_name )
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


    def help(self, method_name=None):
        """
            Usage example:
                clip byname --entry_name=download_entry , help
                clip byname --entry_name=download_entry , help --method_name=download
        """
        print( "Entry:         {}".format( self.get_name() ) )
        print( "EntryPath:     {}".format( self.get_path() ) )

        if method_name:
            print( "Method:        {}".format( method_name ) )
            try:
                ancestry_path   = []
                function_object = self.reach_method(method_name, _ancestry_path=ancestry_path) # the method may not be reachable

                required_arg_names, optional_arg_names, method_defaults, varargs, varkw = utils.expected_call_structure(function_object)

                signature = ', '.join(required_arg_names + [optional_arg_names[i]+'='+str(method_defaults[i]) for i in range(len(optional_arg_names))] )
                if varargs:
                    signature += ', *'+varargs
                if varkw:
                    signature += ', **'+varkw

                print( "MethodPath:    {}".format( function_object.__module__ ))
                print( "Ancestry path: {}".format( ' --> '.join(ancestry_path) ))
                print( "Signature:     {}({})".format( method_name, signature ))
                print( "DocString:    {}".format( function_object.__doc__ ))
            except Exception as e:
                print( str(e) )
        else:
            try:
                module_object   = self.get_module_object()  # the entry may not contain any code...
                doc_string      = module_object.__doc__     # the module may not contain any DocString...
                print( "DocString:    {}".format(doc_string))
            except ImportError:
                parent_may_know = ", but you may want to check its parent: "+self.parent_entry.get_name() if self.parent_loaded() else ""
                print("This entry has no code of its own" + parent_may_know)
            except Exception as e:
                print( str(e) )


    def generate_merged_parameters(self):
        own_parameters = self.parameters_loaded()

        if self.parent_loaded():
            return utils.merged_dictionaries(self.parent_entry.parameters_loaded(), own_parameters)
        else:
            return own_parameters


    def call(self, function_name, call_specific_params=None, pos_params=None, entry_wide_params=None):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and optionally **kwargs.
        """

        try:
            pos_params          = pos_params or []
            function_object     = self.reach_method(function_name)

            entry_wide_params   = entry_wide_params or self.generate_merged_parameters()
            merged_params       = utils.merged_dictionaries(entry_wide_params, call_specific_params) if call_specific_params else entry_wide_params

            merged_params.update( {             # These special parameters are non-overridable at the moment. Should they be?
                '__kernel__'    : self.kernel,
                '__entry__'     : self,
            } )

            result = utils.free_access(function_object, pos_params, merged_params)
        except NameError as method_not_found_e:
            try:
                entry_method_object = getattr(self, function_name)
                result = utils.free_access(entry_method_object, pos_params, call_specific_params, class_method=True)
            except AttributeError:
                try:
                    kernel_method_object = getattr(self.kernel, function_name)
                    result = utils.free_access(kernel_method_object, pos_params, call_specific_params, class_method=True)
                except AttributeError:
                    raise method_not_found_e

        return result


if __name__ == '__main__':

    print("Kernel version = {}".format(default_kernel_instance.version()))

    print(core_repository_path)

    uncached_entry = Entry(own_parameters={'son': 'Lenny', 'daughter': 'Isabella'})
    print("Son: {}, Daughter: {}".format(uncached_entry['son'], uncached_entry['daughter']))

    foo_entry = Entry(core_repository_path + '/foo_entry')

    p, q = foo_entry.call('foo', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    foo_entry['fourth'] = 'vierte'

    foo2 = foo_entry['second']
    foo4 = foo_entry['fourth']
    print("foo2 = {}, foo4 = {}\n".format(foo2, foo4))

    dir_path    = foo_entry.get_path()
    file_path   = foo_entry.get_path('abracadabra.txt')
    print("dir_path = {}, file_path = {}\n".format(dir_path, file_path))

    bar_entry = default_kernel_instance.bypath(core_repository_path + '/bar_entry')

    p, q = bar_entry.call('bar', { 'alpha' : 100, 'beta' : 200, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_bar = {}, Q_bar = {}\n".format(p,q))


    ## Switching to another kernel_instance would mean all other classes (including collections would have to comply with changes!)
    #
#    iter_entry_kernel_instance = MicroKernel( parameters_location=('parameters.json',["alternative", "place", 1]) )
#    iterative_entry = iter_entry_kernel_instance.byname('iterative_functions')

    iterative_entry = default_kernel_instance.byname('iterative_functions')
    recursive_entry = default_kernel_instance.byname('recursive_functions')

    for funcs_entry in (iterative_entry, recursive_entry):
        entry_name  = funcs_entry.get_name()
        fib_n       = funcs_entry.call('fibonacci', {} )
        fact_n      = funcs_entry.call('factorial', {} )
        print("{} : fib(n) = {}, fact(n) = {}\n".format(entry_name, fib_n, fact_n))

    params_entry    = default_kernel_instance.byname('params_entry')
    params_dict     = params_entry.call('show', {'alpha' : 'Hello', 'gamma' : 'World', 'delta' : 420} )
    print(" 'show' method when called via API returned : {}\n".format(params_dict))

    try:
        params_entry.call('nonexistent_func', { 'alpha' : 123 })
    except NameError as e:
        print(str(e) + "\n")

    ## direct inheritance from param_entry (via parent_entry_name):
    #
    latin = default_kernel_instance.byname('latin')
    print(latin.generate_merged_parameters())
    print("")

    ## direct inheritance from latin (and so indirect from param_entry):
    #
    english = default_kernel_instance.byname('english')
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
    gaelic_entry = default_kernel_instance.byname('gaelic')
    print(gaelic_entry)
    print("")

    download_entry = default_kernel_instance.byname('download_entry')
    download_entry.help()
    download_entry.help(method_name='download')
