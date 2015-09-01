#!/usr/bin/env python

DOCUMENTATION='''
module: retention
author: "Greg Hellings (@greghellings)"
version_added: 2.0
description:
    - Define a retention policy for files or directories matching a particular shell pattern. This module will only
      indicate that something has changed if it deletes files or folders.
short_description: Remove files/folders outside of retention policy
options:
  src: 
    description:
      - The folder where files/folders live that should be culled. If this folder does not exist, then this module
        will fail to execute.
    required: true
    aliases: [ "directory" ]
  count:
    description:
      - The number of files matching the pattern to retain. If you set this to 0, then all files matching the
        pattern will be deleted.
    required: true
    type: "int"
    aliases: [ "retain" ]
  pattern:
    description:
      - The filesystem pattern of files or folders within the specified directory to consider for retention and deletion.
        See Python's glob.glob documentation for specific details, but in general the expansions available are ? to match
        a single character, * to match mulitple characters, and [0-7] to match ranges of characters. Other types of expansion
        patterns do not appear to work (e.g. {gz,bz2,xz} will not work, though it will work on some shells in Unix).
    required: true
  ordering:
    description:
      - The method to use while ordering the entries within the directory. Only the latter elements in the ordering will be
        retained. So if you specify 'alphabetical' (the default) for ordering and '*' for your pattern, in a directory
        containing a, b, c, d, e, f, g, h, i then the latter alphabetical values will be retained while earlier entries in
        the alphabet will be removed
    required: false
    default: "alphabetical"
    choices: [ "alphabetical", "time" ]
  recursive:
    description:
      - If a folder is considered for deletion and this is set to "true", then the entire folder with its contents will be
        recursively removed. If this is false (the default) then the directory must already be empty in order to be removed.
        Attempting to remove a non-empty directory without setting this value to "true" will result in the module failing.
    required: false
    default: "False"
    type: "bool"
'''

EXAMPLES='''
- name: keep only the last 3 apache log files
  retention: src=/var/log/httpd pattern=access_log* count=3

- name: keep only the 5 most-recently updated copies of the application
  retention: src=/home/application/copies pattern=* count=5 ordering="time"
'''
import glob
import os
import shutil
from ansible.module_utils.basic import *


def time_key(item):
    stat = os.stat(item)
    return stat.st_mtime


def sort_entries(entries, ordering, module):
    key_methods = {
            'time': time_key,
            'alphabetical': lambda i: i
    }
    try:
        return sorted(entries, key=key_methods[ordering])
    except Exception, ex:
        module.fail_json(msg="Failed to sort directory listings. %s" % (str(ex)))


def delete_files(entry, recursive, module):
    try:
        if os.path.isdir(entry):
            if recursive:
                shutil.rmtree(entry)
            else:
                os.rmdir(entry)
        else:
            os.remove(entry)
    except Exception, ex:
        module.fail_json(msg="Failed to delete item %s. Error %s" % (entry, str(ex)))


def main():
    module = AnsibleModule(
            argument_spec={
                'src': { 'required' : True, 'aliases': ['directory'] },
                'count': { 'required' : True, 'aliases': ['retain'], 'type': 'int' },
                'pattern': { 'default' : '*' },
                'ordering': { 'default' : 'alphabetical', 'choices': ['time', 'alphabetical'] },
                'recursive': { 'default': False, 'type': 'bool'}
            }
    )
    params = type('Params', (), module.params)
    try:
        os.chdir(params.src)
    except Exception, ex:
        module.fail_json(msg=str(ex))
    entries = glob.glob(params.pattern)
    entries = sort_entries(entries, params.ordering, module)
    to_remove = []
    if params.count == 0:
        to_remove = entries
    else:
        for entry in entries[:-1*params.count]:
            to_remove.append(entry)
    if len(to_remove) == 0:
        module.exit_json(changed=False, files=entries)
    else:
        for entry in to_remove:
            delete_files(entry, params.recursive, module)
        module.exit_json(changed=True, files=entries, remove=to_remove)
    module.exit_json(files=entries, remove=to_remove)


main()
