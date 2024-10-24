'''
build_dvs

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

Usage: This python file builds 1 distributed virtual switch in vcenter.
'''
import sys
import ssl
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import nic2dvs as nic
from pyVmomi import vmodl

def main(vsphere_ip,vsphere_user,vsphere_pass,datacenter,cluster,dvs_name):

    sslContext = ssl._create_unverified_context()
    port="443"

    # Create a connector to vsphere
    si = SmartConnect(
        host=vsphere_ip,
        user=vsphere_user,
        pwd=vsphere_pass,
        port=port,
        sslContext=sslContext
    )

    # Number of ports
    num_ports = 200
    vnic ="vmnic7"
    # Disconnect on exit
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    datacenter = nic.get_obj(content, [vim.Datacenter], datacenter)
    cluster = nic.get_obj(content, [vim.ClusterComputeResource], cluster)

    network_folder = datacenter.networkFolder

    #Create DV Switch
    dv_switch = nic.create_dvSwitch(si, content, network_folder, cluster, dvs_name, vnic)

    return dv_switch
# Start program
if __name__ == "__main__":

    # Get user variables
    vsphere_ip= sys.argv[1]         #STRING: IP address of vcenter
    vsphere_user = sys.argv[2]      #STRING: administrator@vsphere.local
    vsphere_pass = sys.argv[3]      #STRING: password for userid
    datacenter = sys.argv[4]        #STRING: name of the data datacenter
    cluster = sys.argv[5]           #STRING: Cluster name ex: "LG06"
    dvs_name= sys.argv[6]           #STRING: Nameof the dvs switch

    main()
