#!/usr/bin/env python3

""" Pipeline interpreter

    Gets a pipeline in internal format produced by cli_parser, executes it and returns the result.
"""


def traverse(dictionary, key_path, complete=True):
    last_syllable = key_path.pop()          # in the edge case of one element, the list becomes empty after popping

    dict_ptr = dictionary
    for key_syllable in key_path:
        if key_syllable not in dict_ptr:    # explicit path vivification
            dict_ptr[key_syllable] = {}
        dict_ptr = dict_ptr[key_syllable]   # iterative descent

    if complete:
        return dict_ptr[last_syllable]
    else:
        return dict_ptr, last_syllable


def execute(pipeline, __kernel__=None):

    #import sys
    #sys.path.append( __kernel__.get_kernel_path() )
    #import utils

    wc                  = __kernel__.working_collection()
    entry_type          = type(wc)
    result_cache        = {}

    if pipeline==[]:
        pipeline = [{ 'method': 'help' }]
    elif type(pipeline)!=list:  # ensuring the pipeline format is a LoLoD
        pipeline = [pipeline]

    if type(pipeline[0])!=list:
        pipeline = [pipeline]

    for curr_chain in pipeline:
        curr_entry_object   = None

        for curr_link in curr_chain:
            start_from  = curr_link.get('start_from')
            label       = curr_link.get('label')
            method      = curr_link['method']       # the mandatory part
            pos_params  = curr_link.get('pos_params', [])
            param_layers= curr_link.get('params', [])

            ## Re-start if explicitly required:
            #
            if start_from:
                if (type(start_from) == str) and start_from.startswith(':'):                # fetch the cached value
                    curr_entry_object = traverse(result_cache, start_from[1:].split('.'))
                else:                                                                       # or use the given value
                    curr_entry_object = start_from
                #
                # we'll deal with possible type/class mismatches later ...
            elif curr_entry_object==None:
                curr_entry_object = wc
            #
            # otherwise just stay with curr_entry_object ...

            if type(param_layers)==dict:
                param_layers = [ param_layers ]

            merged_params = {}
            for param_layer in param_layers:
                for k_str in param_layer.keys():
                    if k_str[-1] == ':':                    # reference to a previously cached result or its subcomponent
                        m_keypath   = k_str[:-1].split('.')
                        m_value     = traverse(result_cache, param_layer[k_str].split('.'))
                    else:                                   # just a verbatim value, possibly structural
                        m_keypath   = k_str.split('.')
                        m_value     = param_layer[k_str]

                    m_ptr, m_last_syll = traverse(merged_params, m_keypath, False)
                    if m_last_syll == '':
                        m_ptr.update(m_value)
                    else:
                        m_ptr[m_last_syll] = m_value

            result = curr_entry_object.call(method, merged_params, pos_params)

            if label != None:
                result_cache[label] = result

            if isinstance(result, entry_type):
                curr_entry_object = result

    return result


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #

    import sys
    from os.path import dirname as dn
    sys.path.append( dn(dn(dn(__file__))) )
    from class_entry import default_kernel_instance as kernel

    execute({ 'method': 'show_map' }, __kernel__=kernel)
    print('='*60)
    execute([{'method': 'byname', 'params': {'entry_name': 'params_entry'} }, {'method': 'show' }], __kernel__=kernel)
    print('='*60)
    execute([[{'method': 'byname', 'pos_params': ['words_collection'], 'label': 'wdz' }],
             [{ 'method': 'byname', 'pos_params': ['params_entry'] }, { 'method': 'show', 'params': { 'extras.n2p:': 'wdz.name_2_path', 'extras.pen:': 'wdz.parent_entry_name'} }],
            ], __kernel__=kernel)
    print('='*60)
    execute([[{'method': 'byname', 'params': {'entry_name': 'words_collection'}, 'label': 'wdz' }],
             [{'method': 'byname', 'params': {'entry_name': 'params_entry'} }, {'method': 'show', 'params': { ':': 'wdz.name_2_path'} }],
            ], __kernel__=kernel)
