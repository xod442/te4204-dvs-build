from pyVmomi import vim
from pyVim.task import WaitForTask
from pyVim.connect import SmartConnect, Disconnect
import time
import ssl
import logging
import atexit
#
def delete_dvs(content):
    dvs_list = content.viewManager.CreateContainerView(content.rootFolder,
                                                     [vim.DistributedVirtualSwitch],
                                                     True)

    for dvs in dvs_list.view:

        message = 'Deleting distributed virtual switch %s' % (dvs.name)
        logging.warning(message)
        task = dvs.Destroy_Task()
        response = WaitForTask(task)

    dvs_list.Destroy()

def list_host_systems(content):
    """List all HostSystem objects in vCenter."""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    host_systems = container.view
    container.Destroy()

    if not host_systems:
        print("No Host Systems found.")
        return

    return host_systems

def connect_to_vcenter(host, user, password, port=443):
    """
    Connect to vCenter server
    """
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=host,
                                                user=user,
                                                pwd=password,
                                                port=port,
                                                sslContext=context)
        atexit.register(connect.Disconnect, service_instance)
        return service_instance.RetrieveContent()
    except Exception as e:
        print("Unable to connect to vCenter server:", str(e))
        return None

def find_snapshots(vm, snapshot_name):
    """
    Find all snapshots with a specific name for a VM
    """
    snapshots = []
    if vm.snapshot:
        snapshot_stack = [(snapshot, []) for snapshot in vm.snapshot.rootSnapshotList]
        while snapshot_stack:
            current_snapshot, snapshot_path = snapshot_stack.pop()
            snapshot_path.append(current_snapshot)
            if current_snapshot.name == snapshot_name:
                snapshots.append(current_snapshot)
            snapshot_stack.extend([(child, snapshot_path[:]) for child in current_snapshot.childSnapshotList])
    return snapshots

def delete_snapshots(snapshots):
    """
    Delete snapshots
    """
    for snapshot in snapshots:
        task = snapshot.snapshot.RemoveSnapshot_Task(removeChildren=False)
        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(1)

def create_snapshot(vm, snapshot_name):
    """
    Create a new snapshot for a VM
    """
    task = vm.CreateSnapshot(snapshot_name, memory=False, quiesce=False)
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(1)

def list_dvs_switches(content):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    dvs_list = dvs_view.view
    dvs_view.Destroy()
    return dvs_list

def wait_for_task(task, hideResult=False):
    """
    Waits and provides updates on a vSphere task
    """
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(5)
    return task.info.result

def get_dvswitches_and_portgroups(content):
    """
    Retrieve all distributed virtual switches and their associated port groups in the vCenter Server.
    """
    dvswitches = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in container.view:
        dvswitches[switch.name] = {'uuid': switch.uuid, 'portgroups': []}
        for pg in switch.portgroup:
            dvswitches[switch.name]['portgroups'].append(pg.name)
    container.Destroy()
    return dvswitches


def get_dvswitches_and_uplinks(content):
    """
    Retrieve all distributed virtual switches and their associated uplinks in the vCenter Server.
    """
    dvswitches = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in container.view:
        dvswitches[switch.name] = {'uuid': switch.uuid, 'uplinks': []}
        for uplink in switch.config.uplinkPortgroup:
            dvswitches[switch.name]['uplinks'].append(uplink.name)
    container.Destroy()
    return dvswitches

def get_dvswitches(content):
    """
    Retrieve all distributed virtual switches in the vCenter Server.
    """
    dvswitches = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in container.view:
        dvswitches[switch.name] = switch.uuid
    container.Destroy()
    return dvswitches

def list_networks(content):
    network_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Network], True)
    networks = network_view.view
    network_view.Destroy()
    return networks


# Function to find a virtual machine by its name
def find_vm_by_name(content, vm_name):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm.name == vm_name:
            return vm
    return None

# Function to find a distributed virtual switch by its name
def find_dvs_by_name(content, dvs_name):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in dvs_view.view:
        if switch.name == dvs_name:
            return switch
    return None

def get_dvportgroup_names(service_instance):
    content = service_instance.RetrieveContent()
    dvportgroups = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualPortgroup], True)

    dvportgroup_names = []
    for dvportgroup in dvportgroups.view:
        dvportgroup_names.append(dvportgroup.name)

    return dvportgroup_names


def find_dvs_portgroup_by_name(content, dvs_name, portgroup_name):
    dvs = find_dvs_by_name(content, dvs_name)
    if dvs:
        ##print(dvs_name)
        portgroup = find_portgroup_by_name(content, dvs, portgroup_name)
        return portgroup
    else:
        return None

def find_portgroup_by_name(content, dvs, portgroup_name):
    portgroup_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.dvs.DistributedVirtualPortgroup], True)
    portgroups = [pg for pg in portgroup_view.view if pg.config.distributedVirtualSwitch == dvs and pg.name == portgroup_name]
    portgroup_view.Destroy()
    if portgroups:
        return portgroups[0]
    else:
        return None
def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def wait_for_task(task, actionName='job', hideResult=False):
    """
    Waits and provides updates on a vSphere task
    """

    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(2)

    if task.info.state == vim.TaskInfo.State.success:
        if task.info.result is not None and not hideResult:
            out = '%s completed successfully, result: %s' % (actionName, task.info.result)
            print(out)
        else:
            out = '%s completed successfully.' % actionName
            print(out)
    #else:
        #out = '%s did not complete successfully: %s' % (actionName, task.info.error)
        #raise task.info.error
        #print(out)

    return task.info.result

def add_dvPort_group(si, dv_switch, dv_port_name, vlan_number):

    dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    dv_pg_spec.name = dv_port_name
    dv_pg_spec.numPorts = 2
    dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding
    dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()

    vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    vlan_spec.vlanId = vlan_number
    dv_pg_spec.defaultPortConfig.vlan = vlan_spec

    dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=True)
    dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)

    dv_pg_spec.defaultPortConfig.vlan.inherited = False
    dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
    dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False
    task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])

    wait_for_task(task)

    return task.info.result


def create_dvSwitch(si, content, network_folder, cluster, dvs_name, vnic):
    pnic_specs = []
    dvs_host_configs = []
    uplink_port_names = []
    dvs_create_spec = vim.DistributedVirtualSwitch.CreateSpec()
    dvs_config_spec = vim.DistributedVirtualSwitch.ConfigSpec()
    dvs_config_spec.name = dvs_name
    dvs_config_spec.uplinkPortPolicy = vim.DistributedVirtualSwitch.NameArrayUplinkPortPolicy()
    hosts = cluster.host
    for x in range(len(hosts)):
        uplink_port_names.append("dvUplink%d" % x)

    for host in hosts:
        dvs_config_spec.uplinkPortPolicy.uplinkPortName = uplink_port_names
        dvs_config_spec.maxPorts = 200
        pnic_spec = vim.dvs.HostMember.PnicSpec()
        pnic_spec.pnicDevice = vnic
        pnic_specs.append(pnic_spec)
        dvs_host_config = vim.dvs.HostMember.ConfigSpec()
        dvs_host_config.operation = vim.ConfigSpecOperation.add
        dvs_host_config.host = host
        dvs_host_configs.append(dvs_host_config)
        dvs_host_config.backing = vim.dvs.HostMember.PnicBacking()
        dvs_host_config.backing.pnicSpec = pnic_specs
        dvs_config_spec.host = dvs_host_configs

    dvs_create_spec.configSpec = dvs_config_spec
    dvs_create_spec.productInfo = vim.dvs.ProductSpec(version='6.6.0')

    task = network_folder.CreateDVS_Task(dvs_create_spec)

    wait_for_task(task, si)

    return


def _2uplinkdvs(si, dvs_name, datacenter_name, uplinks):
    content = si.RetrieveContent()
    print(dvs_name)
    datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)

    if not datacenter:
        raise Exception(f"Datacenter '{datacenter_name}' not found")

    # Get the network folder in the datacenter
    network_folder = datacenter.networkFolder

    # Create a DistributedVirtualSwitchCreateSpec
    dvs_create_spec = vim.dvs.VmwareDistributedVirtualSwitch.CreateSpec()
    dvs_config_spec = vim.dvs.VmwareDistributedVirtualSwitch.ConfigSpec()
    dvs_config_spec.name = dvs_name
    dvs_config_spec.uplinkPortPolicy = vim.dvs.VmwareDistributedVirtualSwitch.NameArrayUplinkPortPolicy()
    dvs_config_spec.uplinkPortPolicy.uplinkPortName = uplinks

    dvs_create_spec.configSpec = dvs_config_spec
    dvs_create_spec.productInfo = vim.dvs.ProductSpec(version="7.0.0")

    # Create the DVS
    print(f"Creating Distributed Virtual Switch '{dvs_name}' with uplinks: {uplinks}")
    task = network_folder.CreateDVS_Task(dvs_create_spec)
    task_result = task.info.state

    while task.info.state == vim.TaskInfo.State.running:
        pass  # Wait for the task to complete

    if task.info.state == vim.TaskInfo.State.success:
        print(f"Distributed Virtual Switch '{dvs_name}' created successfully")
    else:
        print(f"Failed to create DVS: {task.info.error.msg}")
    return


def connect_vnic_to_portgroup(dvs_name,dvs_pg,vm_name,vmnic_mac,portKey,vsp_ip,vsp_user,vsp_pass):
    """
    Connect vmnic to DVswitch.

    :variables:
        dvs_name            -type:string    'LG01-dvs-1'
        dvs_pg              -type:string    'LG01-DP-01'
        vm_name             -type:string    'LG01-WL01-V10-101'
        vmnic_mac           -type:string    '00:50:56:b6:5c:a6'
        portKey             -type:string    '1'
        vsp_ip              -type:string    '10.250.0.50'
        vsp_user            -type:string    'adminsitrator@vsphere.local'
        vsp_pass            -type:string    'my_pass'

    :return: None.
    """
    sslContext = ssl._create_unverified_context()
    port="443"

    # Create a connector to vsphere
    service_instance = SmartConnect(
                        host=vsp_ip,
                        user=vsp_user,
                        pwd=vsp_pass,
                        port=port,
                        sslContext=sslContext
    )
    if service_instance:

        content = service_instance.RetrieveContent()
        switch = find_dvs_by_name(content, dvs_name)
        # Get switch UUID
        switch_uuid = switch.uuid

        portgroup = find_dvs_portgroup_by_name(content, dvs_name, dvs_pg)
        if portgroup:
            vm = find_vm_by_name(content, vm_name)
            if vm:
                trash, portgroup_key = str(portgroup).split(':')
                portgroup_key = portgroup_key[:-1]

                devices = vm.config.hardware.device
                for device in devices:
                    if isinstance(device, vim.vm.device.VirtualVmxnet3):
                        if str(device.macAddress) == vmnic_mac:
                            nic_spec = vim.vm.device.VirtualDeviceSpec()
                            nic_spec.device = device
                            nic_spec.device.connectable.connected = True
                            nic_spec.device.deviceInfo.summary = dvs_pg
                            nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                            nic_spec.device.backing.port.switchUuid = switch_uuid
                            nic_spec.device.backing.port.portgroupKey = portgroup_key
                            nic_spec.device.backing.port.portKey = portKey

                            config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
                            # Connect the port
                            task_number = vm.ReconfigVM_Task(config_spec)
                            response = wait_for_task(task_number)
                            print("Successfully connected vNIC with MAC {} to DVS port group.".format(vmnic_mac))
                            return


        #print("No vNIC found with MAC {} on the VM.".format(vmnic_mac))
    Disconnect(service_instance)
    return None
