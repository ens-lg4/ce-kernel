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


    import re

    i = 0
    caller_name = arglist[0]
    i += 1

    top_links = []

    while i<len(arglist):

        if arglist[i] == ',':   # backward nesting on demand
            prev_link = top_links.pop()
            chain_link = { 'start_from': prev_link }
            i += 1
        else:
            if arglist[i] == ',,':
                i += 1
            chain_link = {}
        ## There may be a preceding label, check for it:
        #
        matched_label = re.match('^(\w+):$', arglist[i])
        if matched_label:
            chain_link['label'] = matched_label.group(1)
            i += 1

        ## The mandatory method name:
        #
        chain_link['method'] = arglist[i]
        i += 1

        call_params = {}
        chain_link['params'] = call_params

        top_links.append( chain_link )

        while i<len(arglist) and arglist[i] not in (',', ',,'):
            call_param_key = None
            matched_paramref = re.match('^-?-?([\w\.]*:)([\w\.]+)$', arglist[i])
            if matched_paramref:
                call_param_key      = matched_paramref.group(1)
                call_param_value    = matched_paramref.group(2)
            else:
                matched_parampair = re.match('^-?-?([\w\.]+)([\ ,;]?)=(.*)$', arglist[i])
                if matched_parampair:
                    call_param_key      = matched_parampair.group(1)
                    delimiter           = matched_parampair.group(2)
                    call_param_value    = matched_parampair.group(3)
                    if delimiter:
                        call_param_value    = [to_num_or_not_to_num(el) for el in call_param_value.split(delimiter)]
                    else:
                        call_param_value    = to_num_or_not_to_num(call_param_value)
                else:
                    matched_paramsingle = re.match('^-?-?([\w\.]+)([,-]?)$', arglist[i])
                    if matched_paramsingle:
                        call_param_key      = matched_paramsingle.group(1)
                        if matched_paramsingle.group(2) == ',':
                            call_param_value    = []                                    # the way to express an empty list
                        else:
                            call_param_value    = matched_paramsingle.group(2) != '-'     # either boolean True or False

            if call_param_key:
                call_params[call_param_key] = call_param_value
            else:
                raise(Exception("Parsing error - cannot understand '{}'".format(arglist[i])))
            i += 1


    return {
        'caller_name':  caller_name,
        'pipeline':     top_links,
    }


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    cmd_line = 'clip labA: method_A --p5- --p6=60 p7= p6=600 --p8.key1=v81 --p8.key2=82 , labB: method_B ,, method_C --p9.alpha.beta=999 -p9.alpha.gamma=boo -p10 --data.empty1 --data.empty2= --data.empty3,= --data.empty4,'
    cmd_line = 'clip'
    parsed_cmd = parse( cmd_line.split(' ') )

    from pprint import pprint
    print("Caller name: {}".format(parsed_cmd['caller_name']))
    print("\nPipeline structure:")
    pprint(parsed_cmd['pipeline'])
