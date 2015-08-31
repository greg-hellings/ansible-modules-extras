#!/usr/bin/env python


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
    except Exception as ex:
        module.fail_json(msg="Failed to sort directory listings. %s" % (str(ex)))


def delete_files(entry, recursive, module):
    try:
        if recursive:
            shutil.rmtree(entry)
        else:
            if os.path.isdir(entry):
                os.rmdir(entry)
            else:
                os.remove(entry)
    except Exception as ex:
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
    except Exception as ex:
        module.fail_json(msg=str(ex))
    entries = glob.glob(params.pattern)
    entries = sort_entries(entries, params.ordering, module)
    to_remove = []
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
