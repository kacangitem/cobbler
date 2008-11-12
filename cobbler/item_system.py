"""
A Cobbler System.

Copyright 2006-2008, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301  USA
"""

import utils
import item
import time
from cexceptions import *
from utils import _

class System(item.Item):

    TYPE_NAME = _("system")
    COLLECTION_TYPE = "system"

    def make_clone(self):
        ds = self.to_datastruct()
        cloned = System(self.config)
        cloned.from_datastruct(ds)
        return cloned

    def clear(self,is_subobject=False):
        self.name                 = None
        self.owners               = self.settings.default_ownership
        self.profile              = None
        self.image                = None
        self.kernel_options       = {}
        self.kernel_options_post  = {}
        self.ks_meta              = {}    
        self.interfaces           = {}
        self.default_interface    = self.settings.default_interface
        self.netboot_enabled      = True
        self.depth                = 2
        self.mgmt_classes         = []              
        self.template_files       = {}
        self.kickstart            = "<<inherit>>"   # use value in profile
        self.server               = "<<inherit>>"   # "" (or settings)
        self.virt_path            = "<<inherit>>"   # ""
        self.virt_type            = "<<inherit>>"   # "" 
        self.virt_cpus            = "<<inherit>>"   # ""
        self.virt_file_size       = "<<inherit>>"   # ""
        self.virt_ram             = "<<inherit>>"   # ""
        self.virt_type            = "<<inherit>>"   # ""
        self.virt_path            = "<<inherit>>"   # ""
        self.virt_bridge          = "<<inherit>>"   # ""
        self.comment              = ""
        self.ctime                = 0
        self.mtime                = 0

    def delete_interface(self,name):
        """
        Used to remove an interface.  Not valid for the default interface.
        """
        if self.interfaces.has_key(name) and name != "eth0":
            del self.interfaces[name]
        else:
            if name == "eth0"
                raise CX(_("Interface %s can never be deleted") % name
            else:
                raise CX(_("Cannot delete interface that is not present: %s") % name)
        return True
        

    def __get_interface(self,name):
        if name is None:
            return self.__get_default_interface()

        if not self.interfaces.has_key(name):
            self.interfaces[name] = {
                "mac_address" : "",
                "ip_address"  : "",
                "dhcp_tag"    : "",
                "subnet"      : "",
                "gateway"     : "",
                "hostname"    : "",
                "virt_bridge" : "",
                "static"      : False,
                "bonding"     : "",
                "bonding_master" : "",
                "bonding_opts" : ""
            }

        return self.interfaces[name]

    def __get_default_interface(self):
        return self.__get_interface("eth0")

    def from_datastruct(self,seed_data):

        # this is to upgrade older cobbler installs.
        # previously we had interfaces in a hash from intf0 ... intf8
        # now we support arbitrary names but want to make sure any interfaces named intfN
        # are named after the actual interface name -- before we couldn't assure order so
        # we didn't want apply intf0 == eth0, now we can.

        intf = self.load_item(seed_data, "interfaces", {})
        for x in range(0,8):
           key1 = "intf%d" % x
           key2 = "intf%d" % y
           if intf.has_key(key1):
               # copy intfN to ethN
               seed_data["interfaces"][key2] = seed_data["interfaces"][key1].copy()
               del seed_data["interfaces"][key1]

        # load datastructures from previous and current versions of cobbler
        # and store (in-memory) in the new format.
        # (the main complexity here is the migration to NIC data structures)

        self.parent               = self.load_item(seed_data, 'parent')
        self.name                 = self.load_item(seed_data, 'name')
        self.owners               = self.load_item(seed_data, 'owners', self.settings.default_ownership)
        self.profile              = self.load_item(seed_data, 'profile')
        self.image                = self.load_item(seed_data, 'image')

        self.kernel_options       = self.load_item(seed_data, 'kernel_options', {})
        self.kernel_options_post  = self.load_item(seed_data, 'kernel_options_post', {})
        self.ks_meta              = self.load_item(seed_data, 'ks_meta', {})
        self.depth                = self.load_item(seed_data, 'depth', 2)        
        self.kickstart            = self.load_item(seed_data, 'kickstart', '<<inherit>>')
        self.netboot_enabled      = self.load_item(seed_data, 'netboot_enabled', True)
        self.server               = self.load_item(seed_data, 'server', '<<inherit>>')
        self.mgmt_classes         = self.load_item(seed_data, 'mgmt_classes', [])
        self.template_files       = self.load_item(seed_data, 'template_files', {})
        self.comment              = self.load_item(seed_data, 'comment', '')

        # virt specific 
        self.virt_path   = self.load_item(seed_data, 'virt_path', '<<inherit>>') 
        self.virt_type   = self.load_item(seed_data, 'virt_type', '<<inherit>>')
        self.virt_ram    = self.load_item(seed_data,'virt_ram','<<inherit>>')
        self.virt_file_size  = self.load_item(seed_data,'virt_file_size','<<inherit>>')
        self.virt_path   = self.load_item(seed_data,'virt_path','<<inherit>>')
        self.virt_type   = self.load_item(seed_data,'virt_type','<<inherit>>')
        self.virt_bridge = self.load_item(seed_data,'virt_bridge','<<inherit>>')
        self.virt_cpus   = self.load_item(seed_data,'virt_cpus','<<inherit>>')

        self.ctime       = self.load_item(seed_data,'ctime',0)
        self.mtime       = self.load_item(seed_data,'mtime',0)

        # backwards compat, these settings are now part of the interfaces data structure
        # and will contain data only in upgrade scenarios.

        __ip_address      = self.load_item(seed_data, 'ip_address',  "")
        __dhcp_tag        = self.load_item(seed_data, 'dhcp_tag',    "")
        __hostname        = self.load_item(seed_data, 'hostname',    "")
        __mac_address     = self.load_item(seed_data, 'mac_address', "")

        # now load the new-style interface definition data structure

        self.interfaces      = self.load_item(seed_data, 'interfaces', {})

        # now backfill the interface structure with any old values from
        # before the upgrade

        if not self.interfaces.has_key("intf0"):
            if __hostname != "":
                self.set_hostname(__hostname, "intf0")
            if __mac_address != "":
                self.set_mac_address(__mac_address, "intf0")
            if __ip_address != "":
                self.set_ip_address(__ip_address, "intf0")
            if __dhcp_tag != "":
                self.set_dhcp_tag(__dhcp_tag, "intf0")

        # backwards compatibility:
        # for interfaces that do not have all the fields filled in, populate the new fields
        # that have been added (applies to any new interface fields Cobbler 1.3 and later)
        # other fields have been created because of upgrade usage        

        for k in self.interfaces.keys():
            if not self.interfaces[k].has_key("static"):
               self.interfaces[k]["static"] = False

        # backwards compatibility -- convert string entries to dicts for storage
        # this allows for better usage from the API.

        if self.kernel_options != "<<inherit>>" and type(self.kernel_options) != dict:
            self.set_kernel_options(self.kernel_options)
        if self.kernel_options_post != "<<inherit>>" and type(self.kernel_options_post) != dict:
            self.set_kernel_options_post(self.kernel_options_post)
        if self.ks_meta != "<<inherit>>" and type(self.ks_meta) != dict:
            self.set_ksmeta(self.ks_meta)

        # explicitly re-call the set_name function to possibily populate MAC/IP.
        self.set_name(self.name)

        # coerce types from input file
        self.set_netboot_enabled(self.netboot_enabled)
        self.set_owners(self.owners) 
        self.set_mgmt_classes(self.mgmt_classes)
        self.set_template_files(self.template_files)


        # enforce that the system extends from a profile or system but not both
        # profile wins as it's the more common usage
        self.set_image(self.image)
        self.set_profile(self.profile)

        return self

    def get_parent(self):
        """
        Return object next highest up the tree.
        """
        if (self.parent is None or self.parent == '') and self.profile:
            return self.config.profiles().find(name=self.profile)
        elif (self.parent is None or self.parent == '') and self.image:
            return self.config.images().find(name=self.image)
        else:
            return self.config.systems().find(name=self.parent)

    def set_name(self,name):
        """
        Set the name.  If the name is a MAC or IP, and the first MAC and/or IP is not defined, go ahead
        and fill that value in.  
        """
        intf = self.__get_default_interface()


        if self.name not in ["",None] and self.parent not in ["",None] and self.name == self.parent:
            raise CX(_("self parentage is weird"))
        if type(name) != type(""):
            raise CX(_("name must be a string"))
        for x in name:
            if not x.isalnum() and not x in [ "_", "-", ".", ":", "+" ] :
                raise CX(_("invalid characters in name: %s") % x)

        if utils.is_mac(name):
           if intf["mac_address"] == "":
               intf["mac_address"] = name
        elif utils.is_ip(name):
           if intf["ip_address"] == "":
               intf["ip_address"] = name
        self.name = name 

        return True

    def set_server(self,server):
        """
        If a system can't reach the boot server at the value configured in settings
        because it doesn't have the same name on it's subnet this is there for an override.
        """
        self.server = server
        return True

    def get_mac_address(self,interface):
        """
        Get the mac address, which may be implicit in the object name or explicit with --mac-address.
        Use the explicit location first.
        """

        intf = self.__get_interface(interface)

        if intf["mac_address"] != "":
            return intf["mac_address"]
        else:
            return None

    def get_ip_address(self,interface):
        """
        Get the IP address, which may be implicit in the object name or explict with --ip-address.
        Use the explicit location first.
        """

        intf = self.__get_interface(interface)

        if intf["ip_address"] != "": 
            return intf["ip_address"]
        else:
            return None

    def is_management_supported(self,cidr_ok=True):
        """
        Can only add system PXE records if a MAC or IP address is available, else it's a koan
        only record.  Actually Itanium goes beyond all this and needs the IP all of the time
        though this is enforced elsewhere (action_sync.py).
        """
        if self.name == "default":
           return True
        for (name,x) in self.interfaces.iteritems():
            mac = x.get("mac_address",None)
            ip  = x.get("ip_address",None)
            if ip is not None and not cidr_ok and ip.find("/") != -1:
                # ip is in CIDR notation
                return False
            if mac is not None or ip is not None:
                # has ip and/or mac
                return True
        return False

    def set_default_interface(self,interface):
        if self.interfaces.has_key(interface):
            self.default_interface = interface
        else:
            raise CX(_("invalid interface (%s)") % interface)

    def set_dhcp_tag(self,dhcp_tag,interface):
        intf = self.__get_interface(interface)
        intf["dhcp_tag"] = dhcp_tag
        return True

    def set_hostname(self,hostname,interface):
        intf = self.__get_interface(interface)
        intf["hostname"] = hostname
        return True

    def set_static(self,truthiness,interface):
        intf = self.__get_interface(interface)
        intf["static"] = utils.input_boolean(truthiness)
        return True

    def set_ip_address(self,address,interface):
        """
        Assign a IP or hostname in DHCP when this MAC boots.
        Only works if manage_dhcp is set in /etc/cobbler/settings
        """
        intf = self.__get_interface(interface)
        if address == "" or utils.is_ip(address):
           intf["ip_address"] = address
           return True
        raise CX(_("invalid format for IP address (%s)") % address)

    def set_mac_address(self,address,interface):
        intf = self.__get_interface(interface)
        if address == "" or utils.is_mac(address):
           intf["mac_address"] = address.strip()
           return True
        raise CX(_("invalid format for MAC address (%s)" % address))

    def set_gateway(self,gateway,interface):
        intf = self.__get_interface(interface)
        intf["gateway"] = gateway
        return True

    def set_subnet(self,subnet,interface):
        intf = self.__get_interface(interface)
        intf["subnet"] = subnet
        return True
    
    def set_virt_bridge(self,bridge,interface):
        intf = self.__get_interface(interface)
        intf["virt_bridge"] = bridge
        return True

    def set_bonding(self,bonding,interface):
        intf = self.__get_interface(interface)
        intf["bonding"] = bonding
        return True

    def set_bonding_master(self,bonding_master,interface):
        intf = self.__get_interface(interface)
        intf["bonding_master"] = bonding_master
        return True

    def set_bonding_opts(self,bonding_opts,interface):
        intf = self.__get_interface(interface)
        intf["bonding_opts"] = bonding_opts
        return True

    def set_profile(self,profile_name):
        """
        Set the system to use a certain named profile.  The profile
        must have already been loaded into the Profiles collection.
        """
        if profile_name in [ "delete", "None", "~", ""] or profile_name is None:
            self.profile = ""
            return True

        self.image = "" # mutual exclusion rule

        p = self.config.profiles().find(name=profile_name)
        if p is not None:
            self.profile = profile_name
            self.depth = p.depth + 1 # subprofiles have varying depths.
            return True
        raise CX(_("invalid profile name"))

    def set_image(self,image_name):
        """
        Set the system to use a certain named image.  Works like set_profile
        but cannot be used at the same time.  It's one or the other.
        """
        if image_name in [ "delete", "None", "~", ""] or image_name is None:
            self.image = ""
            return True

        self.profile = "" # mutual exclusion rule

        img = self.config.images().find(name=image_name)

        if img is not None:
            self.image = image_name
            self.depth = img.depth + 1
            return True
        raise CX(_("invalid image name (%s)") % image_name)

    def set_virt_cpus(self,num):
        return utils.set_virt_cpus(self,num)

    def set_virt_file_size(self,num):
        return utils.set_virt_file_size(self,num)
 
    def set_virt_ram(self,num):
        return utils.set_virt_ram(self,num)

    def set_virt_type(self,vtype):
        return utils.set_virt_type(self,vtype)

    def set_virt_path(self,path):
        return utils.set_virt_path(self,path)

    def set_netboot_enabled(self,netboot_enabled):
        """
        If true, allows per-system PXE files to be generated on sync (or add).  If false,
        these files are not generated, thus eliminating the potential for an infinite install
        loop when systems are set to PXE boot first in the boot order.  In general, users
        who are PXE booting first in the boot order won't create system definitions, so this
        feature primarily comes into play for programmatic users of the API, who want to
        initially create a system with netboot enabled and then disable it after the system installs, 
        as triggered by some action in kickstart %post.   For this reason, this option is not
        surfaced in the CLI, output, or documentation (yet).

        Use of this option does not affect the ability to use PXE menus.  If an admin has machines 
        set up to PXE only after local boot fails, this option isn't even relevant.
        """
        self.netboot_enabled = utils.input_boolean(netboot_enabled)
        return True

    def is_valid(self):
        """
        A system is valid when it contains a valid name and a profile.
        """
        # NOTE: this validation code does not support inheritable distros at this time.
        # this is by design as inheritable systems don't make sense.
        if self.name is None:
            raise CX(_("need to specify a name for this object"))
        if self.profile in [ None, "" ] and self.image in [ None,"" ]:
            raise CX(_("need to specify a profile or image as a parent for this system"))

        return True

    def set_kickstart(self,kickstart):
        """
        Sets the kickstart.  This must be a NFS, HTTP, or FTP URL.
        Or filesystem path. Minor checking of the URL is performed here.

        NOTE -- usage of the --kickstart parameter in the profile
        is STRONGLY encouraged.  This is only for exception cases
        where a user already has kickstarts made for each system
        and can't leverage templating.  Profiles provide an important
        abstraction layer -- assigning systems to defined and repeatable 
        roles.
        """
        if kickstart is None or kickstart == "" or kickstart == "delete":
            self.kickstart = "<<inherit>>"
            return True
        if utils.find_kickstart(kickstart):
            self.kickstart = kickstart
            return True
        raise CX(_("kickstart not found"))


    def to_datastruct(self):
        return {
           'name'                  : self.name,
           'kernel_options'        : self.kernel_options,
           'kernel_options_post'   : self.kernel_options_post,
           'depth'                 : self.depth,
           'interfaces'            : self.interfaces,
           'ks_meta'               : self.ks_meta,
           'kickstart'             : self.kickstart,
           'netboot_enabled'       : self.netboot_enabled,
           'owners'                : self.owners,
           'parent'                : self.parent,
           'profile'               : self.profile,
           'image'                 : self.image,
           'server'                : self.server,
           'virt_cpus'             : self.virt_cpus,
           'virt_bridge'           : self.virt_bridge,
           'virt_file_size'        : self.virt_file_size,
           'virt_path'             : self.virt_path,
           'virt_ram'              : self.virt_ram,
           'virt_type'             : self.virt_type,
           'mgmt_classes'          : self.mgmt_classes,
           'template_files'        : self.template_files,
           'comment'               : self.comment,
           'ctime'                 : self.ctime,
           'mtime'                 : self.mtime
        }

    def printable(self):
        buf =       _("system                : %s\n") % self.name
        buf = buf + _("profile               : %s\n") % self.profile
        buf = buf + _("comment               : %s\n") % self.comment
        buf = buf + _("created               : %s\n") % time.ctime(self.ctime)
        buf = buf + _("image                 : %s\n") % self.image
        buf = buf + _("kernel options        : %s\n") % self.kernel_options
        buf = buf + _("kernel options post   : %s\n") % self.kernel_options_post
        buf = buf + _("kickstart             : %s\n") % self.kickstart
        buf = buf + _("ks metadata           : %s\n") % self.ks_meta
        buf = buf + _("mgmt classes          : %s\n") % self.mgmt_classes
        buf = buf + _("modified              : %s\n") % time.ctime(self.mtime)

        buf = buf + _("netboot enabled?      : %s\n") % self.netboot_enabled 
        buf = buf + _("owners                : %s\n") % self.owners
        buf = buf + _("server                : %s\n") % self.server
        buf = buf + _("template files        : %s\n") % self.template_files

        buf = buf + _("virt cpus             : %s\n") % self.virt_cpus
        buf = buf + _("virt file size        : %s\n") % self.virt_file_size
        buf = buf + _("virt path             : %s\n") % self.virt_path
        buf = buf + _("virt ram              : %s\n") % self.virt_ram
        buf = buf + _("virt type             : %s\n") % self.virt_type

        ikeys = self.interface.keys()
        ikeys.sort()
        for name in ikeys:
            x = self.__get_interface(name)
            buf = buf + _("interface        : %s\n") % (name)
            buf = buf + _("  bonding        : %s\n") % x.get("bonding","")
            buf = buf + _("  bonding_master : %s\n") % x.get("bonding_master","")
            buf = buf + _("  bonding_opts   : %s\n") % x.get("bonding_opts","")
            buf = buf + _("  dhcp tag       : %s\n") % x.get("dhcp_tag","")
            buf = buf + _("  gateway        : %s\n") % x.get("gateway","")
            buf = buf + _("  hostname       : %s\n") % x.get("hostname","")
            buf = buf + _("  ip address     : %s\n") % x.get("ip_address","")
            buf = buf + _("  is static?     : %s\n") % x.get("static",False)
            buf = buf + _("  mac address    : %s\n") % x.get("mac_address","")
            buf = buf + _("  subnet         : %s\n") % x.get("subnet","")
            buf = buf + _("  virt bridge    : %s\n") % x.get("virt_bridge","")

        return buf

    def modify_interface(self, hash):
        """
        Used by the WUI to modify an interface more-efficiently
        """
        for (key,value) in hash.iteritems():
            (field,interface) = key.split("-")
            if field == "macaddress" : self.set_mac_address(value, interface)
            if field == "ipaddress"  : self.set_ip_address(value, interface)
            if field == "hostname"   : self.set_hostname(value, interface)
            if field == "static"     : self.set_static(value, interface)
            if field == "dhcptag"    : self.set_dhcp_tag(value, interface)
            if field == "subnet"     : self.set_subnet(value, interface)
            if field == "gateway"    : self.set_gateway(value, interface)
            if field == "virtbridge" : self.set_virt_bridge(value, interface)
            if field == "bonding"    : self.set_bonding(value, interface)
            if field == "bonding_master" : self.set_bonding_master(value, interface)
            if field == "bonding_opts" : self.set_bonding_opts(value, interface)
        return True
         

    def remote_methods(self):
        return {
           'name'             : self.set_name,
           'profile'          : self.set_profile,
           'image'            : self.set_image,
           'kopts'            : self.set_kernel_options,
           'kopts-post'       : self.set_kernel_options_post,
           'kopts_post'       : self.set_kernel_options_post,           
           'ksmeta'           : self.set_ksmeta,
           'kickstart'        : self.set_kickstart,
           'netboot-enabled'  : self.set_netboot_enabled,
           'netboot_enabled'  : self.set_netboot_enabled,           
           'virt-path'        : self.set_virt_path,
           'virt_path'        : self.set_virt_path,           
           'virt-type'        : self.set_virt_type,
           'virt_type'        : self.set_virt_type,           
           'modify-interface' : self.modify_interface,
           'modify_interface' : self.modify_interface,           
           'delete-interface' : self.delete_interface,
           'delete_interface' : self.delete_interface,           
           'virt-path'        : self.set_virt_path,
           'virt_path'        : self.set_virt_path,           
           'virt-ram'         : self.set_virt_ram,
           'virt_ram'         : self.set_virt_ram,           
           'virt-type'        : self.set_virt_type,
           'virt_type'        : self.set_virt_type,           
           'virt-cpus'        : self.set_virt_cpus,
           'virt_cpus'        : self.set_virt_cpus,           
           'virt-file-size'   : self.set_virt_file_size,
           'virt_file_size'   : self.set_virt_file_size,           
           'server'           : self.set_server,
           'owners'           : self.set_owners,
           'mgmt-classes'     : self.set_mgmt_classes,
           'mgmt_classes'     : self.set_mgmt_classes,           
           'template-files'   : self.set_template_files,
           'template_files'   : self.set_template_files,           
           'comment'          : self.set_comment
        }


