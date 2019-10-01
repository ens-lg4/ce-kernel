#!/usr/bin/env python3

""" This entry accesses and prints available information about entries and methods
"""

def entry(entry_name, __kernel__=None):
    """ Print the available DocString of the given entry
    """

    print( "Entry: {}".format( entry_name ) )

    try:
        entry           = __kernel__.byname(entry_name)         # the entry may not be findable...
        module_object   = entry.get_module_object()             # the entry may not contain any code...
        doc_string      = module_object.__doc__                 # the module may not contain any DocString...
        print("DocString: {}".format(doc_string))
    #except NameError as e:
    except Exception as e:
        print( str(e) )


def method(entry_name, method_name, __kernel__=None):
    """ Print the available information about the given method
    """

    print( "Entry: {}".format( entry_name ) )
    print( "Method: {}".format( method_name ) )
    try:
        entry           = __kernel__.byname(entry_name)                                     # the entry may not be findable...
        ancestry_path   = []
        function_object = entry.reach_method(method_name, _ancestry_path=ancestry_path)     # the method may not be reachable
        print( "Path: {}".format( function_object.__module__ ))
        print( "Ancestry path: {}".format( ' --> '.join(ancestry_path) ))
        print( "DocString: {}".format( function_object.__doc__ ))
    #except NameError as e:
    except Exception as e:
        print( str(e) )


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    print("Cannot test this entry in standalone mode yet")
