#!/usr/bin/env python3

#   Accessing an (almost) random python function in CK way (passing in a dictionary) :
#
#   Thanks for this SO entry for inspiration:
#       https://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-python-function-receives

import os           # to manipulate file paths
import sys          # to obtain Python's version
import imp          # to import modules dynamically
import json         # to load JSON-based config files
import inspect      # to obtain a random function's signature


def merged_dictionaries(under_dict, over_dict):
    """Just merge without spoiling the original.

    """
    merged_dict = under_dict.copy()
    merged_dict.update( over_dict )
    return merged_dict


def get_entrys_python_module(module_path, code_container_name='python_code'):
    """ Find and load a python module given the path and filename.

    """
    (open_file_descriptor, path_to_module, module_description) = imp.find_module(code_container_name, [module_path])

    module_object = imp.load_module(path_to_module, open_file_descriptor, path_to_module, module_description)

    return module_object


def expected_call_structure(function_object, class_method=False):
    """ Get the expected parameters of a function and their default values.
    """

    if sys.version_info[0] < 3:
        supported_arg_names, varargs, varkw, defaults = inspect.getargspec(function_object)
    else:
        supported_arg_names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(function_object)

    defaults = defaults or tuple()

    if class_method:
        supported_arg_names.pop(0)

    num_required        = len(supported_arg_names) - len(defaults)
    required_arg_names  = supported_arg_names[:num_required]
    optional_arg_names  = supported_arg_names[num_required:]

    return required_arg_names, optional_arg_names, defaults, varargs, varkw


def free_access(function_object, given_arg_list, given_arg_dict, class_method=False):
    """ Call a given function_object and feed it with arguments from given list and dictionary.

        The function can be declared as having named args, defaults and optionally **kwargs.
    """

    required_arg_names, optional_arg_names, defaults, varargs, varkw = expected_call_structure(function_object, class_method)

    non_listed_required_arg_names = required_arg_names[len(given_arg_list):]
    missing_args_set    = set(non_listed_required_arg_names) - set(given_arg_dict)

    if missing_args_set:
        raise TypeError( 'The "{}" function IS NOT callable with {} and {}. Missing required positional supported_arg_names: {}'
                        .format(function_object.__name__, given_arg_list, given_arg_dict, list(missing_args_set))
        )
    else:
        if varkw:   # only leave out the required parameters without defaults:

            relevant_dict_names = set(given_arg_dict) - set(non_listed_required_arg_names)

        else:       # only take relevant optional parameters and leave gaps for the signature's defaults to mix in:

            relevant_dict_names = set(given_arg_dict) & set(optional_arg_names)

        arg_values_passed_as_list   = given_arg_list + [given_arg_dict[k] for k in non_listed_required_arg_names]
        args_passed_as_dict         = { k : given_arg_dict[k] for k in relevant_dict_names }

        ret_values = function_object(*arg_values_passed_as_list, **args_passed_as_dict)
        return ret_values


def quietly_load_json_config( filepath, structpath=[] ):

    if os.path.isfile( filepath ):
        with open( filepath ) as fd:
            struct_ptr = json.load(fd)
            for syll in structpath:
                if type(struct_ptr)==dict:
                    struct_ptr = struct_ptr.get(syll, {})
                else:
                    struct_ptr = struct_ptr[syll]

            return struct_ptr, True
    else:
        return {}, False


def store_structure_to_json_file( structure, filepath, json_indent=4 ):
    with open(filepath, "w") as json_file:
        json_file.write( json.dumps(structure, indent=json_indent)+'\n' )


def baz(alpha, beta=22, gamma=333):
    print('alpha = "{}", beta = "{}", gamma = "{}"'.format(alpha,beta,gamma))
    return 987, 654, 321


if __name__ == '__main__':

    under   = { 'alpha' : 10,   'beta' : 20              }
    over    = { 'alpha' : 100,              'gamma': 300 }
    merged  = merged_dictionaries(under, over)
    print("UNDER: {}".format(under))
    print("OVER: {}".format(over))
    print("MERGED: {}\n".format(merged))

    foo_module  = get_entrys_python_module('foo_entry')
    bar_module  = get_entrys_python_module('bar_entry')

    # a direct call of a remote function:
    r = foo_module.foo(10, 20, 30, epsilon=70)
    print("R_foo = {}\n".format(r))

    # a direct call of another remote function:
    r = bar_module.bar(10, 20, 30)
    print("R_bar = {}\n".format(r))

    # a direct call of a local function:
    r = baz(10, 20)
    print("R_baz = {}\n".format(r))


    # a remote access call:
    p, q = free_access( foo_module.foo, [100, 200], { 'beta': 222, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    # another remote access call (with kwargs):
    p, q = free_access( bar_module.bar, [], { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'delta' : 400, 'lambda' : 7777, 'mu' : 8888 } )
    print("P_bar = {}, Q_bar = {}\n".format(p,q))

    # a local access call:
    p, q, r = free_access( baz, [], { 'alpha' : 100, 'gamma' : 300, 'lambda' : 7777, 'mu' : 8888 } )
    print("P_baz = {}, Q_baz = {}, R_baz = {}\n".format(p,q,r))


    # an incomplete/underdetermined access call throws an exception:
    try:
        s = free_access( foo_module.foo, [], { 'beta' : 200, 'lambda' : 7777 } )
        print("S_foo = {}\n".format(s))
    except TypeError as e:
        print(str(e) + "\n")

    # an incomplete/underdetermined access call throws an exception:
    try:
        s = free_access( bar_module.bar, [], { 'beta' : 200, 'delta' : 400 } )
        print("S_bar = {}\n".format(s))
    except TypeError as e:
        print(str(e) + "\n")

    # an incomplete/underdetermined access call throws an exception:
    try:
        s = free_access( baz, [], { 'beta' : 200 } )
        print("S_bar = {}\n".format(s))
    except TypeError as e:
        print(str(e) + "\n")

    if sys.version_info[0] >=3:     # built-in functions in Python 2 are not first-class functions and cannot be introspected
        h1 = free_access( hex, [], { 'number' : 31 })
        print("hex = {}\n".format(h1))
        h2 = free_access( hex, [30], {})
        print("hex = {}\n".format(h2))
