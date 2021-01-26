#!/usr/bin/env python3


import subprocess


def run(shell_cmd='env', env=None):

    env = env or {}

    env_setting_prefix = 'env ' + ' '.join([ '{}={}'.format(k,env.get(k,'')) for k in env])
    if env_setting_prefix:
        shell_cmd = env_setting_prefix + ' ' + shell_cmd

    return_code = subprocess.call(shell_cmd, shell = True)

    return return_code


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    return_code = run( "echo Hello, world!" )
    print("ReturnCode = {}\n".format(return_code))

    return_code = run( env={'FOO':12345, 'BAR':23456, 'BAZ':34567} )
    print("ReturnCode = {}\n".format(return_code))
