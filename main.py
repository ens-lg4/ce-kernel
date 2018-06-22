#!/usr/bin/env python3

#   Accessing an (almost) random python function in CK way (passing in a dictionary) :
#
#   Thanks for this SO entry for inspiration:
#       https://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-python-function-receives

import os           # to manipulate file paths
import sys          # to refer to THIS module
import imp          # to import modules dynamically
import inspect      # to obtain a random function's signature


def get_entrys_python_module(module_path, module_name):
    """ Find and load a python module given the path and filename.

    """
    (open_file_descriptor, path_to_module, module_description) = imp.find_module(module_name, [module_path])

    module_object = imp.load_module(path_to_module, open_file_descriptor, path_to_module, module_description)

    return module_object


_module_cache = {}

def get_cached_module(entry_name=None, path_to_entries='entries', module_name='python_code'):

    if entry_name == None:
        return sys.modules[__name__]

    module_path     = os.path.join(path_to_entries, entry_name)
    cache_key       = os.path.join(module_path, module_name)
    cached_module   = _module_cache.get(cache_key)

    if not cached_module:
        cached_module = _module_cache[cache_key] = get_entrys_python_module(module_path, module_name)

    return cached_module


def access(entry_name, function_name, arg_dict):
    """ Call a given function of a given entry and feed it with arguments from a given dictionary.

        The function can be declared as having named args, defaults and possibly also **kwargs.
    """

    module_object   = get_cached_module(entry_name)
    function_object = getattr(module_object, function_name)

    args, varargs, varkw, defaults = inspect.getargspec(function_object)

    num_args        = len(args)
    num_required    = num_args-len(defaults or tuple())
    required_args   = args[:num_required]
    missing_args    = set(required_args) - set(arg_dict)

    if missing_args:
        print('The "{}" function IS NOT callable with {}'.format(function_name, arg_dict))
        print('Missing required positional args: {}'.format(missing_args))
    else:
        if varkw:
            # unmentioned args ( set(arg_dict) - set(args) ) will end up in **kwargs:
            #
            relevant_arg_dict   = arg_dict
        else:
            # leave out irrelevant args by creating a slice and mixing in the defaults:
            #
            relevant_arg_dict   = {args[i] : arg_dict.get(args[i], defaults[i-num_required]) for i in range(num_args)}

        print('The "{}" function IS callable with {}'.format(function_name, relevant_arg_dict))
        ret_values = function_object(**relevant_arg_dict)
        return ret_values


def baz(alpha, beta=22, gamma=333):
    print('alpha = "{}", beta = "{}", gamma = "{}"'.format(alpha,beta,gamma))
    return 987, 654, 321


if __name__ == '__main__':

    this_module = get_cached_module(None)
    foo_module  = get_cached_module('foo_entry')
    bar_module  = get_cached_module('bar_entry')

    # a direct call of a remote function:
    r = foo_module.foo(10, 20, 30, epsilon=70)
    print("R_foo = {}\n".format(r))

    # a direct call of another remote function:
    r = bar_module.bar(10, 20, 30, 40)
    print("R_bar = {}\n".format(r))

    # a direct call of a local function:
    r = baz(10, 20)
    print("R_baz = {}\n".format(r))


    # a remote access call:
    p, q = access('foo_entry', 'foo', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'epsilon' : 500, 'lambda' : 7777 } )
    print("P_foo = {}, Q_foo = {}\n".format(p,q))

    # another remote access call (with kwargs):
    p, q = access('bar_entry', 'bar', { 'alpha' : 100, 'beta' : 200, 'gamma' : 300, 'delta' : 400, 'lambda' : 7777, 'mu' : 8888 } )
    print("P_bar = {}, Q_bar = {}\n".format(p,q))

    # a local access call:
    p, q, r = access(None, 'baz', { 'alpha' : 100, 'gamma' : 300, 'lambda' : 7777, 'mu' : 8888 } )
    print("P_baz = {}, Q_baz = {}, R_baz = {}\n".format(p,q,r))


    # an incomplete/underdetermined access call:
    s = access('foo_entry', 'foo', { 'beta' : 200, 'lambda' : 7777 } )
    print("S_foo = {}\n".format(s))

    # an incomplete/underdetermined access call:
    s = access('bar_entry', 'bar', { 'beta' : 200, 'delta' : 400 } )
    print("S_bar = {}\n".format(s))

    # an incomplete/underdetermined access call:
    s = access(None, 'baz', { 'beta' : 200 } )
    print("S_bar = {}\n".format(s))

