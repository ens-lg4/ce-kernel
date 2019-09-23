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

        return s.startswith('-') or '=' in s


    def undash_unpair(s):
        "Remove 1 or 2 leading dashes from an argument"

        undashed = s[1:] if s.startswith('-') else s                        # remove one dash
        undashed = undashed[1:] if undashed.startswith('-') else undashed   # remove another dash

        eq_position = undashed.find('=')
        if eq_position>0:
            param_name, param_value = undashed[0:eq_position], to_num_or_not_to_num(undashed[eq_position+1:])
        else:
            param_name, param_value = undashed, 'yes'
        return (param_name, param_value)


    i = 0
    pipe_calls = []

    while i<len(arglist):
        ## Since the previous iteration stopped, we are looking at a method name
        #
        call_method = arglist[i]
        call_params = {}
        pipe_calls.append( [ call_method, call_params ] )
        i += 1
        while i<len(arglist) and is_param_like(arglist[i]):
            call_param_key, call_param_value = undash_unpair(arglist[i])
            call_params[call_param_key] = call_param_value
            i += 1

    caller_name, kernel_params = pipe_calls.pop(0)

    return {
        'caller_name':      caller_name,
        'kernel_params':    kernel_params,
        'pipe_calls':       pipe_calls,
    }


def execute(pipe_calls, start_entry=None, __entry__=None, __kernel__=None):
    "Execute the previously parsed command line"

    import utils

    current_entry = start_entry or __kernel__.entry_cache['working_collection']
    call_output = None
    passed_params = {}

    for pipe_call_vector in pipe_calls:
        call_method = pipe_call_vector[0]
        call_params = pipe_call_vector[1] if len(pipe_call_vector)>1 else {}
        print("Call method: {}, Passed params: {}, Overriding params: {}".format(call_method, passed_params, call_params))
        mixed_params = utils.merged_dictionaries(passed_params, call_params)
        call_output = current_entry.call(call_method, mixed_params )
        print("Call output: {}".format(call_output))
        if isinstance(call_output, type(__entry__)):
            current_entry = call_output
            passed_params = {}
            print("Output is an Entry, switching to it")
        elif isinstance(call_output, dict):
            passed_params = call_output
            print("Output is a dictionary, passing it for a merge")
        else:
            print("Output is neither an Entry nor a dictionary, staying with the current one")

    return call_output


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    cmd_line = 'ce --u1= --u2=v2 -u3=33 u2=override2 -u4 method_A --p5 --p6=60 p7= p6=600 --p8=v8 method_B method_C --p9=999 -p10'
    parsed_cmd = parse( cmd_line.split(' ') )

    from pprint import pprint
    print("Caller name: {}".format(parsed_cmd['caller_name']))
    print("Kernel parameters: {}".format(parsed_cmd['kernel_params']))
    print("\nPipeline calls:")
    pprint(parsed_cmd['pipe_calls'])