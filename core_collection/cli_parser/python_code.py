#!/usr/bin/env python3


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


def cli_parse(arglist):
    "Parse the command line"

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


    cmd_name    = arglist[0]
    uber_params = {}
    method_name = None
    entry_name  = None
    call_params = {}

    ## Optional uber_params may follow the cmd_name:
    #
    i = 1
    while i<len(arglist) and is_param_like(arglist[i]):   # uber-parameters of the call precede both method_name and entry_name
        uber_param_key, uber_param_value = undash_unpair(arglist[i])
        uber_params[uber_param_key] = uber_param_value
        i += 1

    ## No arguments means the same as --help
    #
    if len(arglist)==1:
        uber_params['help'] = 'yes'

    ## Expecting two consecutive non-params, <method_name> and <entry_name>
    #
    if len(arglist)-i>=2 and ('=' not in arglist[i]+arglist[i+1]) and not arglist[i+1].startswith('-'):
        method_name, entry_name = arglist[i], arglist[i+1]

    ## Optional call_params may follow <method_name> and <entry_name>
    #
    for syll in arglist[i+2:]:
        param_name, param_value = undash_unpair(syll)
        call_params[param_name] = param_value

    return cmd_name, uber_params, method_name, entry_name, call_params


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    cmd_line = 'ce --u1= --u2=v2 --u3=33 -u4 method_A entry_B --p5 --p6=v6 --p7= --p8=800'
    cmd_name, uber_params, method_name, entry_name, call_params = cli_parse( cmd_line.split(' ') )
    print("{} command line parser:\n\tuber_params={}, method_name={}, entry_name={}, call_params={}\n".format(cmd_name, uber_params, method_name, entry_name, call_params))

