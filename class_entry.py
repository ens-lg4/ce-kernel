#!/usr/bin/env python3

import os
import utils
from collections import namedtuple


core_repository_path = os.path.dirname( os.path.realpath(__file__) )    # depends on relative position of THIS FILE in the repository


CollectionProperties = namedtuple('CollectionProperties', ['pathfinder_func', 'parameters_location', 'meta_location', 'code_container_name'])


def default_pathfinder(entry_name):
    return os.path.join(core_repository_path, 'entries', entry_name)


default_collection_properties = CollectionProperties(pathfinder_func=default_pathfinder, parameters_location=('parameters.json',[]), meta_location=('meta.json',[]), code_container_name='python_code')



def smart_pathfinder(entry_name):
    core_collection_path    = os.path.join(core_repository_path, 'entries')
    user_collection_path    = os.path.join(core_repository_path, 'entries', 'words_collection')
    collection_search_order = [ core_collection_path, user_collection_path ]

    for collection_path in collection_search_order:
        collection_obj = Entry(os.path.basename(collection_path), entry_path=collection_path)
        collection_obj.get_metas()
        if collection_obj.has_meta:         # FIXME: better check if the entry ->CAN('find_one')
            local_path = collection_obj.call('find_one', { 'name' : entry_name} )
            if local_path:
                full_path = os.path.join(collection_obj.get_path(), local_path)
                print("found {} in {} : {}".format(entry_name, collection_path, full_path))
                return full_path
            else:
                print("not found {} in {}".format(entry_name, collection_path))
        else:
            print("{} doesn't contain meta".format(collection_path))

    return None


def find_Entry(entry_name):
    smart_entry_properties=CollectionProperties(pathfinder_func=smart_pathfinder, parameters_location=('parameters.json',[]), meta_location=('meta.json',[]), code_container_name='python_code')

    entry_object = Entry(entry_name, properties=smart_entry_properties)

    return entry_object


class Entry:
    def __init__(self, entry_name, entry_path=None, parent_entry=None, properties=default_collection_properties):
        self.entry_name     = entry_name
        self.entry_path     = entry_path or properties.pathfinder_func(entry_name)
        self.parent_entry   = parent_entry
        self.properties     = properties

        ## Placeholders for lazy loading:
        #
        self.module_object  = None
        self.meta           = None
        self.has_meta       = None
        self.parameters     = None


    def get_name(self):
        return self.entry_name


    def get_path(self, filename=None):
        if filename:
            return os.path.join(self.entry_path, filename)
        else:
            return self.entry_path


    def get_module_object(self):
        self.module_object = self.module_object or utils.get_entrys_python_module(self.entry_path, code_container_name=self.properties.code_container_name)

        return self.module_object


    def parent_loaded(self):
        if not self.parent_entry:
            parent_entry_name = self.get_metas().get('parent_entry_name', None)
            if parent_entry_name:
                self.parent_entry = Entry(parent_entry_name, properties=self.properties)

        return self.parent_entry


    def get_metas(self):
        if not self.meta:
            meta_rel_path, meta_struct_path = self.properties.meta_location
            self.meta, self.has_meta = utils.quietly_load_json_config( self.get_path(meta_rel_path), meta_struct_path )

        return self.meta


    def get_parameters(self):
        if not self.parameters:
            parameters_rel_path, parameters_struct_path = self.properties.parameters_location
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


    def call(self, function_name, override_params=None, main_params=None):
        """ Call a given function of a given entry and feed it with arguments from a given dictionary.

            The function can be declared as having positional args, named args with defaults and possibly also **kwargs.
        """

        main_params     = main_params or self.get_parameters()
        merged_params   = utils.merged_dictionaries(main_params, override_params) if override_params else main_params

        try:
            module_object   = self.get_module_object()
            return utils.free_access(module_object, function_name, merged_params)
        except (ImportError, NameError) as e:   # if we don't have own code at all, or just no own function_name defined, ask the parent
            if self.parent_loaded():
                return self.parent_entry.call(function_name, main_params=merged_params)
            else:
                raise e                         # perhaps, better error reporting is needed ("no such method along the inheritance path")


if __name__ == '__main__':

    foo_entry = Entry('foo_entry')

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

    bar_entry = Entry('bar_entry')

    p, q = bar_entry.call('bar', { 'alpha' : 100, 'beta' : 200, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_bar = {}, Q_bar = {}\n".format(p,q))


    iter_entry_properties=CollectionProperties(pathfinder_func=default_pathfinder, parameters_location=('parameters.json',["alternative", "place", 1]), meta_location=('meta.json',[]), code_container_name='python_code')

    iterative_entry = Entry('iterative_functions', properties=iter_entry_properties)
    recursive_entry = Entry('recursive_functions')

    for funcs_entry in (iterative_entry, recursive_entry):
        entry_name  = funcs_entry.get_name()
        fib_n       = funcs_entry.call('fibonacci', {} )
        fact_n      = funcs_entry.call('factorial', {} )
        print("{} : fib(n) = {}, fact(n) = {}\n".format(entry_name, fib_n, fact_n))

    params_entry    = Entry('params_entry')
    params_dict     = params_entry.call('show', {'alpha' : 'Hello', 'gamma' : 'World', 'delta' : 420} )
    print(" 'show' method when called via API returned : {}\n".format(params_dict))

    try:
        params_entry.call('nonexistent_func', { 'alpha' : 123 })
    except NameError as e:
        print(str(e) + "\n")

    ## direct inheritance from param_entry (via meta.parent_entry_name):
    #
    latin = find_Entry('latin')
    print(latin.get_parameters())
    print("")

    ## direct inheritance from latin (and so indirect from param_entry):
    #
    english = find_Entry('english')
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
    gaelic_entry = find_Entry('gaelic')
    print(gaelic_entry)
    print("")
