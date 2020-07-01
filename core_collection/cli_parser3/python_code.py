#!/usr/bin/env python3

""" CLIP stands for Command LIne Pipeline.

    An Entry is defined as a directory that may contain:
        - DATA (in the form of parameters.json)
        - CODE (in the form of python_code.py)
        - FILES (just arbitrary files within that directory)

    CLIP allows you to access all of these in a convenient way from the command line.

    The simplest pipeline is accessing a directory that contains python_code.py
    and then running a parameterized function from it:
        clip bypath /path/to/your/entry , \\
             fun_name pos_param1 pos_param2 --opt_scalar4=val4 --opt_list6,=list_el1,list_el2 --opt_dict8.foo=bar

    Yes, it's that simple: CLIP automatically understands positional & optional parameters,
    and can do quite a bit of structural data parsing on the fly, so you don't have to.
    In the example above we pass in two positional parameters, an optional scalar,
    an optional space-separated list, and a key-value pair of an optional dictionary.

    Note the comma - it is CLIP's "internal pipe" symbol that links steps of a pipeline together,
    passing the object that is a result of the previous step, to the next step of the pipeline.
"""


def get_arglist():
    "Returns command line arguments as a list, wrapped in a dictionary"

    import sys

    return { 'arglist': sys.argv }


def parse(arglist):
    """Parse the command line given as a list of string arguments.

    The expected format is:
        clip [[[<label>:] <method_name> [<pos_param>]* [<opt_param>]* ] [<separator> [label:] <method_name> [<pos_param>]* [<opt_param>]*]* ]

        You can use as many positional params as possible while their values are scalars.
        However as soon as you need to define a structure, a switch to optional param syntax will be necessary.

        Optional params can represent a lot of things:
            --alpha                         # boolean True
            --beta-                         # boolean False
            --gamma=                        # scalar empty string
            --delta=1234                    # scalar number
            --epsilon=hello                 # scalar string
            --zeta,=tag1,tag2,tag3          # list (can be split on a comma, a colon: or a space )
            --eta.theta                     # dictionary boolean True value
            --iota.kappa-                   # dictionary boolean False value
            --lambda.mu=                    # dictionary empty string value
            --nu.xi=omicron                 # dictionary scalar value (number or string)
            --pi.rho,=tag1,tag2,tag3        # dictionary that contains a list
            --sigma:tau.upsilon             # value taken from execution cache, produced by a pipeline step labelled "tau:"
            --phi.chi:psi.omega             # value taken from execution cache, produced by "psi:", assigned to a dictionary key

        Separator can be:
            ,               # pass the object that is the expected result of the previous step to the next step
            ,:cache_label   # do not pass the previous result, rather start from a cached object
            ,,              # do not pass the previous result, rather start from working_collection
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

    pipeline = []

    while i<len(arglist):

        curr_link = {}
        pipeline.append( curr_link )

        ## Leaf through various forms of link separators:
        #
        if arglist[i].startswith(','):
            if arglist[i]==',,':
                curr_link['begin_with'] = ',,'
            else:
                matched_separator = re.match('^,(:[\w\.]+)?(\{?)$', arglist[i])
                if matched_separator:
                    if matched_separator.group(1):
                        curr_link['begin_with'] = matched_separator.group(1)
                    if matched_separator.group(2):
                        curr_link['iterate']    = matched_separator.group(2) == '{'
            i += 1

        ## There may be a label, check for it:
        #
        matched_label = re.match('^(\w+):$', arglist[i])
        if matched_label:
            curr_link['label'] = matched_label.group(1)
            i += 1

        ## The mandatory method name:
        #
        curr_link['method'] = arglist[i]
        i += 1

        call_params = {}
        call_pos_params = []
        curr_link['pos_params'] = call_pos_params
        curr_link['params'] = call_params

        ## Going through the parameters
        while i<len(arglist) and not arglist[i].startswith(','):
            if not arglist[i].startswith('--'):
                call_pos_params.append( to_num_or_not_to_num(arglist[i]) )
            else:
                call_param_key = None
                matched_paramref = re.match('^--([\w\.]*:)([\w\.]+)$', arglist[i])
                if matched_paramref:
                    call_param_key      = matched_paramref.group(1)
                    call_param_value    = matched_paramref.group(2)
                else:
                    matched_parampair = re.match('^--([\w\.]+)([\ ,;:]?)=(.*)$', arglist[i])
                    if matched_parampair:
                        call_param_key      = matched_parampair.group(1)
                        delimiter           = matched_parampair.group(2)
                        call_param_value    = matched_parampair.group(3)
                        if delimiter:
                            call_param_value    = [to_num_or_not_to_num(el) for el in call_param_value.split(delimiter)]
                        else:
                            call_param_value    = to_num_or_not_to_num(call_param_value)
                    else:
                        matched_paramsingle = re.match('^--([\w\.]+)([,-]?)$', arglist[i])
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
        'pipeline':     pipeline,
    }


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    cmd_line = 'clip labA: method_A posA1 --p5- -p6=60 --p7= -p6=600 --p8.key1=v81 --p8.key2=82 , labB: method_B ,, method_C --p9.alpha.beta=999 -p9.alpha.gamma=boo -p10 --data.empty1 --data.empty2= --data.empty3,= --data.empty4, ,, methodD paramD1 --paramD2 ,{ methodE paramE1 , methodF --paramF1=valF1'
    parsed_cmd = parse( cmd_line.split(' ') )

    from pprint import pprint
    print("Caller name: {}".format(parsed_cmd['caller_name']))
    print("\nPipeline structure:")
    pprint(parsed_cmd['pipeline'])
