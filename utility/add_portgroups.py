'''
add_portgroups

,   ,, ,,  , _   ,_   _,    ___,_,  _, ,  _,
\  /|\/|| ,|'|\  |_) /_,   ' | / \,/ \,| (_,
 \/`| `||/\| |-\'| \'\_      |'\_/'\_/'|___)
 '  '  `'  ` '  `'  `  `     ' '   '     '

builds all the distributed virtual switches in for the telemery lab

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0.

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


__author__ = "@netwookie"
__credits__ = ["Rick Kauffman"]
__license__ = "Apache2"
__version__ = "0.1.1"
__maintainer__ = "Rick Kauffman"
__status__ = "Alpha"

Usage: This python file builds 1 distributed port groups on a dvs in vcenter.
'''
import sys
import time
import ssl
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import nic2dvs as nic
from pyVmomi import vmodl



def main(vsphere_ip,vsphere_user,vsphere_pass,dvs_name):
    sslContext = ssl._create_unverified_context()
    port="443"

    # Create a connector to vsphere
    si = nic.connect_to_vcenter(vsphere_ip,vsphere_user,vsphere_pass,port)

    # Disconnect on exit
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    vlans=[{"dv_port_name":"vlan10", "vlan_number": 10},{"dv_port_name":"vlan20", "vlan_number": 20},{"dv_port_name":"ELK-99", "vlan_number": 99}]

    # Get dvs by name
    dvs = nic.find_dvs_by_name(content, dvs_name)
    # Add three portgroups to the dvs
    for v in vlans:
        vlan_number = v['vlan_number']
        dv_port_name = v['dv_port_name']
        response = nic.add_dvPort_group(si, dvs, dv_port_name, vlan_number)
    return
# Start program
if __name__ == "__main__":

    # Get user variables
    vsphere_ip= sys.argv[1]         #STRING: IP address of vcenter
    vsphere_user = sys.argv[2]      #STRING: administrator@vsphere.local
    vsphere_pass = sys.argv[3]      #STRING: password for userid
    dvs_name= sys.argv[6]           #STRING: Nameof the dvs switch
    main()
