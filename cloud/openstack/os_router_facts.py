#!/usr/bin/python

# Copyright (c) 2016 Red Hat, Inc.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

try:
    import shade
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

DOCUMENTATION = '''
---
module: os_router_facts
short_description: Retrieve facts about one or more OpenStack routers.
version_added: "2.2"
author: "Greg Hellings (@greg-hellings)"
description:
    - Retrieve facts about one or more routers from OpenStack.
requirements:
    - "python >= 2.6"
    - "shade"
options:
   router:
     description:
        - Name or ID of the Router
     required: false
   filters:
     description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
     required: false
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Gather facts about previously created routers
- os_router_facts:
    auth:
      auth_url: https://your_api_url.com:9000/v2.0
      username: user
      password: password
      project_name: someproject
- debug: var=openstack_routers

# Gather facts about a previously created router by name
- os_router_facts:
    auth:
      auth_url: https://your_api_url.com:9000/v2.0
      username: user
      password: password
      project_name: someproject
    name:  router1
- debug: var=openstack_routers

# Gather facts about a previously created router with filter (note: name and
  filters parameters are Not mutually exclusive)
- os_router_facts:
    auth:
      auth_url: https://your_api_url.com:9000/v2.0
      username: user
      password: password
      project_name: someproject
    filters:
      tenant_id: 55e2ce24b2a245b09f181bf025724cbe
      subnets:
        - 057d4bdf-6d4d-4728-bb0f-5ac45a6f7400
        - 443d4dc0-91d4-4998-b21c-357d10433483
- debug: var=openstack_routers
'''

RETURN = '''
openstack_routers:
    description: has all the openstack facts about the routers
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: string
        name:
            description: Name given to the network.
            returned: success
            type: string
        status:
            description: Network status.
            returned: success
            type: string
        subnets:
            description: Subnet(s) included in this network.
            returned: success
            type: list of strings
        tenant_id:
            description: Tenant id associated with this network.
            returned: success
            type: string
        shared:
            description: Network shared flag.
            returned: success
            type: boolean
'''

def main():

    argument_spec = openstack_full_argument_spec(
        name=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default=None)
    )
    module = AnsibleModule(argument_spec)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    try:
        cloud = shade.openstack_cloud(**module.params)
        routers = cloud.search_routers(module.params['name'],
                                         module.params['filters'])
        module.exit_json(changed=False, ansible_facts=dict(
            openstack_routers=routers))

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))

# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
if __name__ == '__main__':
    main()
