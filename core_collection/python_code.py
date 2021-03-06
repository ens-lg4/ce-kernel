#!/usr/bin/env python3

""" Find a given entry_name in the given or stored index
"""


def show_map(name_2_path):
    """ Show the whole name_2_path index of this collection.
    """

    from pprint import pprint
    pprint(name_2_path)


def byquery(query, name_2_path, collections_searchpath, __entry__=None, __kernel__=None):
    """ Find all objects matching the query

        Usage examples:
            clip byquery dictionary,-english  ,{ get_path       # tag 'dictionary' is present while tag 'english' is absent
            clip byquery key1.key2.key3==1234 ,{ get_name       # the value of key1.key2.key3 equals 1234
            clip byquery key1.key2.key3!=1234 ,{ get_path       #                     does not equal 1234
            clip byquery key1.key2.key3<1234  ,{ get_name       #                       is less than 1234
            clip byquery key1.ind2.key3>1234  ,{ get_path       #                    is greater than 1234
            clip byquery key1.ind2.key3<=1234 ,{ get_name       #           is less than or equal to 1234
            clip byquery key1.ind2.key3>=1234 ,{ get_path       #        is greater than or equal to 1234
            clip byquery solar.planets:Mars   ,{ get_path       #   is a list and contains the value Mars
            clip byquery solar.planets!:Titan ,{ get_path       #   is a list and does not contain the value Titan
            clip byquery key1.key2.key3.      ,{ get_name       # the path key1.key2.key3 exists
            clip byquery key1.ind2.key3?      ,{ get_path       # the path key1.ind2.key3 converts to True (Python rules)
    """

    def traverse_and_apply(key_path, fun, against=None):
        """ Finally, a useful real-life example of closures:
            captures both *fun* and *against* in the internal function.
        """

        def traverse(entry):
            struct_ptr = entry.parameters_loaded()
            for key_syllable in key_path:
                if type(struct_ptr)==dict and (key_syllable in struct_ptr):
                    struct_ptr = struct_ptr[key_syllable]   # iterative descent
                elif type(struct_ptr)==list:
                    idx = None
                    try:
                        idx = int(key_syllable)
                    except:
                        pass

                    if type(idx)==int and 0<=idx<len(struct_ptr):
                        struct_ptr = struct_ptr[idx]
                    else:
                        return None
                else:
                    return None

            return fun(struct_ptr, against)

        return traverse


    def to_num_or_not_to_num(x):
        "Convert the parameter to a number if it looks like it"

        try:
            x_int = int(x)
            if type(x_int)==int:
                return x_int
        except:
            try:
                x_float = float(x)
                if type(x_float)==float:
                    return x_float
            except:
                pass

        return x


    ## Forming the query:
    #
    if type(query)==dict:   # an already parsed query
        parsed_query        = query
        positive_tags_set   = parsed_query.get('positive_tags_set', set())
        negative_tags_set   = parsed_query.get('negative_tags_set', set())
        check_list          = parsed_query.get('check_list', [])
    else:                   # parsing the query for the first time
        positive_tags_set   = set()
        negative_tags_set   = set()
        check_list          = []
        parsed_query = {
            'positive_tags_set':    positive_tags_set,
            'negative_tags_set':    negative_tags_set,
            'check_list':           check_list,
        }

        conditions = query.split(',')

        import re
        for condition in conditions:
            binary_op_match = re.match('([\w\.]*\w)(=|==|!=|<>|<|>|<=|>=|:|!:)(-?[\w\.]+)$', condition)
            if binary_op_match:
                key_path    = binary_op_match.group(1).split('.')
                test_val    = to_num_or_not_to_num(binary_op_match.group(3))
                if binary_op_match.group(2) in ('=', '=='):
                    check_list.append( traverse_and_apply(key_path, lambda x, y : x==y, test_val) )
                elif binary_op_match.group(2) in ('!=', '<>'):
                    check_list.append( traverse_and_apply(key_path, lambda x, y : x!=y, test_val) )
                elif binary_op_match.group(2)=='<':
                    check_list.append( traverse_and_apply(key_path, lambda x, y : x!=None and x<y, test_val) )
                elif binary_op_match.group(2)=='>':
                    check_list.append( traverse_and_apply(key_path, lambda x, y : x!=None and x>y, test_val) )
                elif binary_op_match.group(2)=='<=':
                    check_list.append( traverse_and_apply(key_path, lambda x, y : x!=None and x<=y, test_val) )
                elif binary_op_match.group(2)=='>=':
                    check_list.append( traverse_and_apply(key_path, lambda x, y : x!=None and x>=y, test_val) )
                elif binary_op_match.group(2)==':':
                    check_list.append( traverse_and_apply(key_path, lambda x, y : type(x)==list and y in x, test_val) )
                elif binary_op_match.group(2)=='!:':
                    check_list.append( traverse_and_apply(key_path, lambda x, y : type(x)==list and y not in x, test_val) )
            else:
                unary_op_match = re.match('([\w\.]*\w)(\.|\?)$', condition)
                if unary_op_match:
                    key_path    = unary_op_match.group(1).split('.')
                    if unary_op_match.group(2)=='.':
                        check_list.append( traverse_and_apply(key_path, lambda x, y: x!=None) )
                    elif unary_op_match.group(2)=='?':
                        check_list.append( traverse_and_apply(key_path, lambda x, y: bool(x)) )
                else:
                    tag_match = re.match('([!^-])?(\w+)$', condition)
                    if tag_match:
                        if tag_match.group(1):
                            negative_tags_set.add( tag_match.group(2) )
                        else:
                            positive_tags_set.add( tag_match.group(2) )
                    else:
                        raise(SyntaxError("Could not parse the condition '{}'".format(condition)))

    objects_found = []

    # Applying the query:
    #
    for relative_path in name_2_path.values():
        full_path = __entry__.get_path(relative_path)
        candidate_object    = __kernel__.bypath(full_path)
        candidate_tags_set  = set(candidate_object['tags'] or [])
        if (positive_tags_set <= candidate_tags_set) and negative_tags_set.isdisjoint(candidate_tags_set):
            candidate_still_ok = True
            for check in check_list:
                if not check(candidate_object):
                    candidate_still_ok = False
                    break
            if candidate_still_ok:
                objects_found.append( candidate_object )

    # Recursion into collections:
    #
    if collections_searchpath:
        for subcollection_name in collections_searchpath:
            if subcollection_name.find('/')>=0:
                subcollection_object    = __kernel__.bypath(subcollection_name)
            else:
                subcollection_local     = name_2_path.get(subcollection_name)
                subcollection_object    = __kernel__.byname(subcollection_name, __entry__ if subcollection_local else None)

            objects_found_in_subcollection  = subcollection_object.call('byquery', { 'query': parsed_query })
            objects_found.extend( objects_found_in_subcollection )

    return objects_found


def byname(entry_name, name_2_path, collections_searchpath, __entry__=None, __kernel__=None):
    """ Find a relative path of the named entry in this collection entry's index.
    """

    relative_path   = name_2_path.get(entry_name)
    if relative_path:
        return __kernel__.bypath( __entry__.get_path(relative_path) )

    # Recursion into collections:
    #
    elif collections_searchpath:
        print("COLLECTION.byname({}) recursing ...".format(entry_name))
        for subcollection_name in collections_searchpath:
            print("COLLECTION.byname({}) checking in {}...".format(entry_name, subcollection_name))
            if subcollection_name.find('/')>=0:
                subcollection_object    = __kernel__.bypath(subcollection_name)
            else:
                subcollection_local     = name_2_path.get(subcollection_name)
                subcollection_object    = __kernel__.byname(subcollection_name, __entry__ if subcollection_local else None)

            found_object            = __kernel__.byname(entry_name, subcollection_object)
            if found_object:
                return found_object
    
    return None


def add_entry(entry_name, data=None, __entry__=None, __kernel__=None):
    """
        Usage example:
            clip byname --entry_name=words_collection add_entry --entry_name=xyz --data.foo.bar=1234 --data.baz=alpha
    """
    import os

    # Create the physical directory for the new entry:
    new_entry_full_path = __entry__.get_path(entry_name)
    print("add_entry: new_entry_full_path="+new_entry_full_path)
    os.makedirs(new_entry_full_path)      # FIXME: fail gracefully if directory path existed

    # Add the new entry to collection:
    __entry__.parameters_loaded()['name_2_path'][entry_name] = entry_name
    __entry__.update()

    if data==None:
        data = {}

    # Update parameters of the new entry:
    new_entry = __kernel__.bypath(new_entry_full_path)
    new_entry.update( data )

    return new_entry


def delete_entry(entry_name, __entry__=None, __kernel__=None):
    """
        Usage example:
            clip byname --entry_name=words_collection delete_entry --entry_name=xyz
    """
    import shutil

    name_2_path = __entry__.parameters_loaded()['name_2_path']
    old_entry_full_path = __entry__.get_path(name_2_path[entry_name])
    print("delete_entry: old_entry_full_path="+old_entry_full_path)

    # Remove the old entry from collection:
    del name_2_path[entry_name]
    __entry__.update()

    # Remove the physical directory of the old entry:
    shutil.rmtree(old_entry_full_path)

    return __entry__


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #

    show_map({"alpha" : 10, "beta" : 200})

    returned_path = byname('second', { "first" : "relative/path/to/the/first", "second" : "relative/path/to/the/second" })
    print("returned_path = {}\n".format(returned_path))
