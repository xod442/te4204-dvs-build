import sys
import ssl
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import nic2dvs as nic

# vCenter connection details
vcenter_host = "10.250.0.50"
vcenter_user = "administrator@vsphere.local"
vcenter_password = "your_vcenter_password"
dvs_name = "MyDistributedSwitch"
datacenter_name = "YourDatacenterName"
uplinks = ["vmnic6", "vmnic7"]

# Disable SSL certificate verification
context = ssl._create_unverified_context()

# Connect to vCenter
try:
    si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)
    print("Connected to vCenter Server")

    # Create the DVS
    return = nic.create_dvs(si, dvs_name, datacenter_name, uplinks)
except Exception as e:
    print(f"Failed to connect to vCenter: {str(e)}")
finally:
    Disconnect(si)
    print("Disconnected from vCenter Server")
