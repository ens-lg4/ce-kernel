#!/usr/bin/env python3


def cli_parse(arglist):
    """Parse the command line given as a list of string arguments.

    The expected format is:
        <executable_path> [--<job_param_key>[=<job_param_value>]]* <method_name> <entry_name> [--<param_key>[=<param_value>]]*

    Both job_params and call_params may:
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

    job_params  = { 'caller_name'   : arglist[0] }
    call_params = {}

    ## Optional job_params may follow the caller_name:
    #
    i = 1
    while i<len(arglist) and is_param_like(arglist[i]):   # auxiliary job parameters precede both <method_name> and <entry_name>
        job_param_key, job_param_value = undash_unpair(arglist[i])
        job_params[job_param_key] = job_param_value
        i += 1

    ## No arguments means the same as --help
    #
    if len(arglist)==1:
        job_params['help'] = 'yes'

    ## Expecting two consecutive non-params, <method_name> and <entry_name>
    #
    if len(arglist)-i>=2 and ('=' not in arglist[i]+arglist[i+1]) and not arglist[i+1].startswith('-'):
        job_params['method_name']   = arglist[i]
        job_params['entry_name']    = arglist[i+1]

    ## Optional call_params may follow <method_name> and <entry_name>
    #
    for syll in arglist[i+2:]:
        param_name, param_value = undash_unpair(syll)
        call_params[param_name] = param_value

    return job_params, call_params


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #
    cmd_line = 'ce --u1= --u2=v2 -u3=33 u2=override2 -u4 method_A entry_B --p5 --p6=60 p7= p6=600 --p8=v8'
    job_params, call_params = cli_parse( cmd_line.split(' ') )
    print("Command line parser:\n\tjob_params={}, call_params={}\n".format(job_params, call_params))
