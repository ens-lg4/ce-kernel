#!/usr/bin/env python3

# Test via CLIP:
#   clip bypath --path=working_collection/download_entry wget --url='http://example.com' --target_path=exmpl.html
#
# or after it has been added to the working_collection:
#   clip byname --entry_name=download_entry wget --url='http://example.com' --target_path=exmpl.html

import os

def download(url, target_path):
    print('url = "{}", target_path = "{}"'.format(url, target_path))
    return wget(url, target_path)


def wget(url, target_path):
    return os.system('wget -O {} {}'.format(target_path, url))


def curl(url, target_path):
    return os.system('curl -o {} {}'.format(target_path, url))


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    r1 = wget('https://www.1112.net/lastpage.html', target_path='lastpage.html')
    print("R_wget = {}\n".format(r1))

    r2 = curl('http://example.com/', target_path='example.html')
    print("R_curl = {}\n".format(r2))
