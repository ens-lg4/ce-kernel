#!/usr/bin/env python3

""" This entry knows how to download a file given a URL and can create a holding entry for it.

Parameterizations of this entry can be recipes for downloading specific things.

Create a new parameterized recipe:
    clip add_entry --entry_name=examplepage_recipe --data.parent_entry_name=download_entry --data.url='http://example.com/' --data.entry_name=examplepage_downloaded --data.file_name=example.html --data.remark='A specific parameterized downloader'

Activate the recipe, i.e. download the file into a new entry:
    clip byname --entry_name=examplepage_recipe , download

Clean up:
    clip delete_entry --entry_name=examplepage_downloaded
    clip delete_entry --entry_name=examplepage_recipe
"""

import os

def download(url, entry_name, file_name, __kernel__):
    """
        Usage example:
            clip byname --entry_name=download_entry , download --url='https://example.com' --entry_name=examplepage_downloaded --file_name=example.html

        Clean up:
            clip delete_entry --entry_name=examplepage_downloaded
    """
    data = {
        'url':          url,
        'file_name':    file_name,
        'remark':       'downloaded via URL'
    }

    new_entry = __kernel__.working_collection().call('add_entry', { 'entry_name' : entry_name, 'data': data})
    target_path = new_entry.get_path(file_name)

    if download_to_path(url, target_path) == 0:
        return target_path
    else:
        return None


def download_to_path(url, target_path):
    """
        Usage example: (assuming the entry has been added to the collection) :
            clip byname --entry_name=download_entry , download_to_path --url='http://example.com' --target_path=exmpl.html
    """
    print('url = "{}", target_path = "{}"'.format(url, target_path))
    return wget(url, target_path)


def wget(url, target_path):
    """
        Usage example (not assuming the entry has been added to the collection) :
            clip bypath --path=working_collection/download_entry , wget --url='http://example.com' --target_path=exmpl.html
    """
    return os.system('wget -O {} {}'.format(target_path, url))


def curl(url, target_path):
    """
        Usage example (not assuming the entry has been added to the collection) :
            clip bypath --path=working_collection/download_entry , curl --url='http://example.com' --target_path=exmpl.html
    """
    return os.system('curl -o {} {}'.format(target_path, url))


if __name__ == '__main__':

    # When the entry's code is run as a script, perform local tests:
    #
    r1 = wget('https://www.1112.net/lastpage.html', target_path='lastpage.html')
    print("R_wget = {}\n".format(r1))

    r2 = curl('http://example.com/', target_path='example.html')
    print("R_curl = {}\n".format(r2))
