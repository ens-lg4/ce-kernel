#!/usr/bin/env python3


def get_arglist():
    "Returns command line arguments as a list, wrapped in a dictionary"

    import sys

    return { 'arglist': sys.argv }


def parse(arglist):
    """Parse the command line given as a list of string arguments.

    The expected format is:
        <executable_path> [--<kernel_param_key>[=<kernel_param_value>]]* [ <method_name> [--<param_key>[=<param_value>]]* ]+

    Both kernel_params and call_params may:
        (1) have a value (numeric or string)
        (2) have no value, but terminate with an equal sign (assuming the value to be '')
        (3) have no value and no trailing equal sign (assuming the value to be 'yes')
        (4) override a previously mentioned value from left to right
    """

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


    def is_param_like(s):
        "Check that an argument looks like a param"

        return s.startswith('-')


    def undash_unpair(s):
        "Remove 1 or 2 leading dashes from an argument"

        undashed = s[1:] if s.startswith('-') else s                        # remove one dash
        undashed = undashed[1:] if undashed.startswith('-') else undashed   # remove another dash

        eq_position = undashed.find('=')
        value_given = eq_position>0
        if value_given:
            param_name, param_value = undashed[0:eq_position], undashed[eq_position+1:]
        else:
            param_name, param_value = undashed, 'yes'
        return (param_name, param_value, value_given)


    import re

    i = 0
    pipe_calls = []

    while i<len(arglist):
        ## There may be a preceding label, check for it:
        #
        found_label = re.match('^(\w+):$', arglist[i])
        if found_label:
            call_label = found_label.group(1)
            i += 1
        else:
            call_label = None   # make sure to clean it up

        ## The mandatory method name:
        #
        call_method = arglist[i]
        i += 1

        call_params = {}
        chain_link = { 'method': call_method, 'params': call_params }
        if call_label:
            chain_link['label'] = call_label
        pipe_calls.append( chain_link )

        while i<len(arglist) and is_param_like(arglist[i]):
            call_param_key, call_param_value, value_given = undash_unpair(arglist[i])

            key_syllables = call_param_key.split('.')   # should contain at least one element
            last_syllable = key_syllables.pop()         # in the edge case of one element, the list becomes empty after popping

            dict_ptr = call_params
            for key_syllable in key_syllables:
                if key_syllable not in dict_ptr:        # explicit path vivification
                    dict_ptr[key_syllable] = {}
                dict_ptr = dict_ptr[key_syllable]       # iterative descent

            delimiter = last_syllable[-1]
            if delimiter in ";, ":
                if value_given:             # split the list
                    dict_ptr[last_syllable[:-1]] = [to_num_or_not_to_num(el) for el in call_param_value.split(delimiter)]
                else:                       # special syntax to denote an empty list
                    dict_ptr[last_syllable[:-1]] = []
            else:                           # treat it as a single scalar
                dict_ptr[last_syllable] = to_num_or_not_to_num(call_param_value)

            i += 1

    caller_name, kernel_params = pipe_calls.pop(0)

    return {
        'caller_name':      caller_name,
        'kernel_params':    kernel_params,
        'chain':            pipe_calls,
    }


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    cmd_line = 'ce --u1= --u2=v2 -u3=33 u2=override2 -u4 method_A --p5 --p6=60 p7= p6=600 --p8.key1=v81 --p8.key2=82 method_B method_C --p9.alpha.beta=999 -p9.alpha.gamma=boo -p10 --data.empty1 --data.empty2= --data.empty3,= --data.empty4,'
    parsed_cmd = parse( cmd_line.split(' ') )

    from pprint import pprint
    print("Caller name: {}".format(parsed_cmd['caller_name']))
    print("Kernel parameters: {}".format(parsed_cmd['kernel_params']))
    print("\nPipeline calls:")
    pprint(parsed_cmd['chain'])
