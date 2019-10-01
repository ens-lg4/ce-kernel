#!/usr/bin/env python3


def execute_job(job_params, call_params, __kernel__=None):
    "Execute the previously parsed command line"

    caller_name = job_params.get('caller_name')
    method_name = job_params.get('method_name')
    entry_name  = job_params.get('entry_name')

    if 'version' in job_params:
        print("Kernel version: {}".format(__kernel__.version()))
        return 0

    if method_name==None or entry_name==None:
        print("Usage:\n\t{0} [--<job_param_key>[=<job_param_value>]]* <method_name> <entry_name> [--<param_key>[=<param_value>]]*".format(caller_name))
        return 0 if 'help' in job_params else 3

    if 'dryrun' in job_params:     # just check that the command line was parsed correctly
        print("{} command line parser:\n\tjob_params={}, call_params={}\n".format(caller_name, job_params, call_params))
        return 0

    entry   = __kernel__.byname(entry_name)
    if not entry:
        print("{}: Could not find the entry '{}'".format(caller_name, entry_name))
        return 2

    if 'help' in job_params:   # now that the format is ok, reaching for method's documentation
        __kernel__.byname('help').call('method', { 'entry_name': entry_name, 'method_name': method_name})

    else:
        try:
            ret_tuple   = entry.call(method_name, call_params)

            print("{}: method '{}' on entry '{}' with parameters {} returned ({})".format(caller_name, method_name, entry_name, call_params, ret_tuple))
        except Exception as e:
            print("{}: When trying to execute method '{}' on entry '{}' with parameters {}, got the exception: {}".format(caller_name, method_name, entry_name, call_params, e))
            return 1

    return 0    # assuming overall success


if __name__ == '__main__':

    ## When the entry's code is run as a script, perform local tests:
    #

    job_params = {
        'entry_name'    : 'recursive_functions',
        'method_name'   : 'factorial',
        'caller_name'   : 'job_test',
        'dryrun'        : 'yes',
    }
    call_params = {
        'n'             : 6,
    }

    ret_value = execute_job(job_params, call_params)
    exit(ret_value)

