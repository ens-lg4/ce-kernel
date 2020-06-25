#!/usr/bin/env python3


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


def execute(pipeline=None, result_cache=None, __kernel__=None):

    if result_cache == None:
        result_cache = {}

    if pipeline == None:
        return __kernel__.working_collection()

    elif type(pipeline) == list:
        for sub_pipeline in pipeline:
            result = execute(sub_pipeline, result_cache, __kernel__)                # recursion #1
        return result   # only the last result gets returned

    elif type(pipeline) == dict:
        
        start_from  = execute(pipeline.get('start_from'), result_cache, __kernel__) # recursion #2
        label       = pipeline.get('label')
        method      = pipeline['method']            # the only mandatory part
        param_layers= pipeline.get('params', [])

        if type(param_layers)==dict:
            param_layers = [ param_layers ]

        merged_params = {}
        for param_layer in param_layers:
            for k_str in param_layer.keys():
                if k_str[-1] == ':':
                    m_keypath   = k_str[:-1].split('.')
                    m_value     = traverse(result_cache, param_layer[k_str].split('.'))
                else:
                    m_keypath   = k_str.split('.')
                    m_value     = param_layer[k_str]

                m_ptr, m_last_syll = traverse(merged_params, m_keypath, False)
                if m_last_syll == '':
                    m_ptr.update(m_value)
                else:
                    m_ptr[m_last_syll] = m_value

        result = start_from.call(method, merged_params)

        if label != None:
            result_cache[label] = result

        return result


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    import sys, os
    from os.path import dirname as dn
    sys.path.append( dn(dn(dn(os.path.realpath(__file__)))) )

    from class_entry import default_kernel_instance as kernel

    execute({ 'method': 'show_map' }, __kernel__=kernel)
    print('='*60)
    execute({ 'start_from': {'method': 'byname', 'params': {'entry_name': 'params_entry'} }, 'method': 'show' }, __kernel__=kernel)
    print('='*60)
    execute([{'method': 'byname', 'params': {'entry_name': 'words_collection'}, 'label': 'wdz' },
             { 'start_from':{'method': 'byname', 'params': {'entry_name': 'params_entry'} }, 'method': 'show', 'params': { 'dicts.n2p:': 'wdz.name_2_path', 'dicts.pen:': 'wdz.parent_entry_name'} },
            ], __kernel__=kernel)
    print('='*60)
    execute([{'method': 'byname', 'params': {'entry_name': 'words_collection'}, 'label': 'wdz' },
             { 'start_from':{'method': 'byname', 'params': {'entry_name': 'params_entry'} }, 'method': 'show', 'params': { ':': 'wdz.name_2_path'} },
            ], __kernel__=kernel)
