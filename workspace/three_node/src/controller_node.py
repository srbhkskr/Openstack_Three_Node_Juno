'''
Created on Nov 14, 2015

@author: saurabh
'''
#! /usr/bin/python
import sys
import os
import time
import subprocess

# These are module names which are not installed by default.
# These modules will be loaded later after downloading
iniparse = None
psutil = None


mysql_password = "openstack"
service_tenant = None
controller = "10.10.10.10"
def kill_process(process_name):
    for proc in psutil.process_iter():
        if proc.name == process_name:
            proc.kill()

#def get_10.10.10.10(ifname):
#        try:
#            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#            return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
#                0x8915,  # SIOCGIFADDR
#                struct.pack('256s', ifname[:15])
#            )[20:24])
#        except Exception:
#            print "Cannot get IP Address for Interface %s" % ifname
#            sys.exit(1)

def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        print("Error: %s file not found" % file_path)

def write_to_file(file_path, content):
    open(file_path, "a").write(content)

def add_to_conf(conf_file, section, param, val):
    config = iniparse.ConfigParser()
    config.readfp(open(conf_file))
    if not config.has_section(section):
        config.add_section(section)
        val += '\n'
    config.set(section, param, val)
    with open(conf_file, 'w') as f:
        config.write(f)


def delete_from_conf(conf_file, section, param):
    config = iniparse.ConfigParser()
    config.readfp(open(conf_file))
    if param is None:
        config.remove_section(section)
    else:
        config.remove_option(section, param)
    with open(conf_file, 'w') as f:
        config.write(f)


def get_from_conf(conf_file, section, param):
    config = iniparse.ConfigParser()
    config.readfp(open(conf_file))
    if param is None:
        raise Exception("parameter missing")
    else:
        return config.get(section, param)

def print_format(string):
    print "+%s+" %("-" * len(string))
    print "|%s|" % string
    print "+%s+" %("-" * len(string))

def execute(command, display=False):
    print_format("Executing  :  %s " % command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if display:
        while True:
            nextline = process.stdout.readline()
            if nextline == '' and process.poll() != None:
                break
            sys.stdout.write(nextline)
            sys.stdout.flush()

        output, stderr = process.communicate()
        exitCode = process.returncode
    else:
        output, stderr = process.communicate()
        exitCode = process.returncode

    if (exitCode == 0):
        return output.strip()
    else:
        print "Error", stderr
        print "Failed to execute command %s" % command
        print exitCode, output
        raise Exception(output)


def execute_db_commnads(command):
    cmd = """mysql -uroot -p%s -e "%s" """ % (mysql_password, command)
    output = execute(cmd)
    return output


def initialize_system():
    
    #if not os.geteuid() == 0:
    #    sys.exit('Please re-run the script with root user')

    execute("apt-get clean" , True)
    execute("apt-get autoclean -y" , True)
<<<<<<< HEAD
    execute("apt-get -f update -y" , True)
    execute("apt-get -f install ubuntu-cloud-keyring python-setuptools python-iniparse python-psutil -y", True)
    delete_file("/etc/apt/sources.list.d/juno.list")
    execute("echo deb http://ubuntu-cloud.archive.canonical.com/ubuntu trusty-updates/juno main >> /etc/apt/sources.list.d/juno.list")
    execute("apt-get -f update -y && apt-get -f upgrade -y", True)
=======
    execute("apt-get update -y" , True)
    execute("apt-get install -f ubuntu-cloud-keyring python-setuptools python-iniparse python-psutil -y", True)
    delete_file("/etc/apt/sources.list.d/juno.list")
    execute('echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu" "trusty-updates/juno main" > /etc/apt/sources.list.d/cloudarchive-juno.list')
    execute("apt-get update -y && apt-get -f upgrade -y", True)
>>>>>>> origin/master

    global iniparse
    if iniparse is None:
        iniparse = __import__('iniparse')

    global psutil
    if psutil is None:
        psutil = __import__('psutil')
#=================================================================================
#==================   Components Installation Starts Here ========================
#=================================================================================


def install_rabbitmq():
<<<<<<< HEAD
    execute("apt-get -f install rabbitmq-server -y", True)
=======
    execute("apt-get install -f rabbitmq-server -y", True)
>>>>>>> origin/master
    execute("service rabbitmq-server restart", True)
    execute("rabbitmqctl change_password guest openstack", True)
    time.sleep(2)


def install_database():

    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
    
<<<<<<< HEAD
    execute("apt-get -f install mariadb-server python-mysqldb -y", True)
    add_to_conf("/etc/mysql/my.cnf", "mysqld", "bind-address" , "10.10.10.10")
=======
    execute("apt-get install mariadb-server python-mysqldb -y", True)

    #Please Comment all without = lines before you do add to conf otherwise it will couse parse error

>>>>>>> origin/master
    add_to_conf("/etc/mysql/my.cnf", "mysqld", "default-storage-engine" , "innodb")
    add_to_conf("/etc/mysql/my.cnf", "mysqld", "collation-server" , "utf8_general_ci")
    add_to_conf("/etc/mysql/my.cnf", "mysqld", "init-connect" , "'SET NAMES utf8'")
    add_to_conf("/etc/mysql/my.cnf", "mysqld", "character-set-server" , "utf8")
    add_to_conf("/etc/mysql/my.cnf", "mysqld", "bind-address" , "10.10.10.10")
    
    execute("service mysql restart", True)
    time.sleep(2)

    try:
        execute("mysqladmin -u root password %s" % mysql_password)
    except Exception:
        print " Mysql Password already set as : %s " % mysql_password



def _create_keystone_users():
    os.environ['SERVICE_TOKEN'] = 'ADMINTOKEN'
    os.environ['SERVICE_ENDPOINT'] = 'http://10.10.10.10:35357/v2.0'
     
#    os.environ['no_proxy'] = "controller,127.0.0.1,%s" % 10.10.10.10
    global service_tenant 
    
    #TODO(ish) : This is crude way of doing. Install keystone client and use that to create tenants, role etc
    admin_tenant = execute("keystone tenant-create --name admin --description 'Admin Tenant' --enabled true |grep ' id '|awk '{print $4}'")
    admin_user = execute("keystone user-create --tenant_id %s --name admin --pass openstack --enabled true|grep ' id '|awk '{print $4}'" % admin_tenant)
    admin_role = execute("keystone role-create --name admin|grep ' id '|awk '{print $4}'")
    execute("keystone user-role-add --user_id %s --tenant_id %s --role_id %s" % (admin_user, admin_tenant, admin_role))
    
    demo_tenant = execute("keystone tenant-create --name demo --description 'Demo Tenant' --enabled true |grep ' id '|awk '{print $4}'")
    demo_user = execute("keystone user-create --tenant_id %s --name demo --pass openstack --enabled true|grep ' id '|awk '{print $4}'" % demo_tenant)
    demo_role = execute("keystone role-create --name demo|grep ' id '|awk '{print $4}'")
    execute("keystone user-role-add --user_id %s --tenant_id %s --role_id %s" % (demo_user, demo_tenant, demo_role))


    service_tenant = execute("keystone tenant-create --name service --description 'Service Tenant' --enabled true |grep ' id '|awk '{print $4}'")


    #keystone
    keystone_service = execute("keystone service-create --name=keystone --type=identity --description='Keystone Identity Service'|grep ' id '|awk '{print $4}'")
    execute( "keystone endpoint-create --service-id %s --publicurl http://controller:5000/v2.0 --internalurl http://controller:5000/v2.0 --adminurl http://controller:35357/v2.0 --region regionOne" % keystone_service)


    #write a rc file
    adminrc = "/root/admin_rc.sh"
    delete_file(adminrc)
    write_to_file(adminrc, "export OS_USERNAME=admin\n")
    write_to_file(adminrc, "export OS_PASSWORD=openstack\n")
    write_to_file(adminrc, "export OS_TENANT_NAME=admin\n")
    write_to_file(adminrc, "export OS_AUTH_URL=http://controller:5000/v2.0\n")

    demorc = "/root/demo_rc.sh"
    delete_file(demorc)
    write_to_file(demorc, "export OS_USERNAME=demo\n")
    write_to_file(demorc, "export OS_PASSWORD=openstack\n")
    write_to_file(demorc, "export OS_TENANT_NAME=demo\n")
    write_to_file(demorc, "export OS_AUTH_URL=http://controller:5000/v2.0\n")

    execute("source /root/admin_rc.sh")

    #Glance
    glance_user = execute("keystone user-create --tenant_id %s --name glance --pass openstack --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)
    execute("keystone user-role-add --user_id %s --tenant_id %s --role_id %s" % (glance_user, service_tenant, admin_role))

    glance_service = execute("keystone service-create --name=glance --type=image --description='Glance Image Service'|grep ' id '|awk '{print $4}'")
    execute("keystone endpoint-create --service-id %s --publicurl http://controller:9292 --internalurl http://controller:9292 --adminurl http://controller:9292 --region regionOne"% glance_service)


    #nova
    nova_user = execute("keystone user-create --tenant_id %s --name nova --pass openstack --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)
    execute("keystone user-role-add --user_id %s --tenant_id %s --role_id %s" % (nova_user, service_tenant, admin_role))

    nova_service = execute("keystone service-create --name=nova --type=compute --description='Nova Compute Service'|grep ' id '|awk '{print $4}'")
    execute("keystone endpoint-create --service-id %s --publicurl http://controller:8774/v2/\$\(tenant_id\)s --internalurl http://controller:8774/v2/\$\(tenant_id\)s --adminurl http://controller:8774/v2/\$\(tenant_id\)s --region regionOne"%nova_service)


    #neutron
    neutron_user = execute("keystone user-create --tenant_id %s --name neutron --pass openstack --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)
    execute("keystone user-role-add --user_id %s --tenant_id %s --role_id %s" % (neutron_user, service_tenant, admin_role))

    neutron_service = execute("keystone service-create --name=neutron --type=network  --description='OpenStack Networking service'|grep ' id '|awk '{print $4}'")
    execute("keystone endpoint-create --service-id %s --publicurl http://controller:9696 --internalurl http://controller:9696 --adminurl http://controller:9696 --region regionOne"%neutron_service)





def install_and_configure_keystone():
    keystone_conf = "/etc/keystone/keystone.conf"

    execute_db_commnads("DROP DATABASE IF EXISTS keystone;")
    execute_db_commnads("CREATE DATABASE keystone;")
    execute_db_commnads("GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'openstack';")
    execute_db_commnads("GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'controller' IDENTIFIED BY 'openstack';")

    execute("apt-get -f install keystone -y", True)


    add_to_conf(keystone_conf, "DEFAULT", "admin_token", "ADMINTOKEN")
    add_to_conf(keystone_conf, "DEFAULT", "admin_port", 35357)
    add_to_conf(keystone_conf, "database", "connection", "mysql://keystone:openstack@controller/keystone")
    add_to_conf(keystone_conf, "revoke", "token_format", "keystone.contrib.revoke.backends.sql.Revoke")
    add_to_conf(keystone_conf, "token", "provider", "keystone.token.providers.uuid.Provider")
    add_to_conf(keystone_conf, "token", "driver", "keystone.token.persistence.backends.sql.Token")


    execute("keystone-manage db_sync")

    execute("service keystone restart", True)

    time.sleep(3)
    _create_keystone_users()



def install_and_configure_glance():
    glance_api_conf = "/etc/glance/glance-api.conf"
    glance_registry_conf = "/etc/glance/glance-registry.conf"
    

    execute_db_commnads("DROP DATABASE IF EXISTS glance;")
    execute_db_commnads("CREATE DATABASE glance;")
    execute_db_commnads("GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY 'openstack';")
    execute_db_commnads("GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'controller' IDENTIFIED BY 'openstack';")

    execute("apt-get -f install glance -y", True)


    

    add_to_conf(glance_api_conf, "DEFAULT", "sql_connection", "mysql://glance:openstack@controller/glance")
    add_to_conf(glance_api_conf, "paste_deploy", "flavor", "keystone")
    add_to_conf(glance_api_conf, "DEFAULT", "verbose", "true")
    add_to_conf(glance_api_conf, "DEFAULT", "debug", "true")
    add_to_conf(glance_api_conf, "DEFAULT", "notification_driver", "noop")
    add_to_conf(glance_api_conf, "keystone_authtoken", "auth_uri", "http://controller:5000/v2.0")
    add_to_conf(glance_api_conf, "keystone_authtoken", "identity_uri", "http://controller:35357")
    add_to_conf(glance_api_conf, "keystone_authtoken", "admin_tenant_name", "service")
    add_to_conf(glance_api_conf, "keystone_authtoken", "admin_user", "glance")
    add_to_conf(glance_api_conf, "keystone_authtoken", "admin_password", "openstack")
    add_to_conf(glance_api_conf, "glance_store", "default_store", "file")
    add_to_conf(glance_api_conf, "glance_store", "filesystem_store_datadir", "/var/lib/glance/images/")
    delete_from_conf(glance_api_conf, "keystone_authtoken", "auth_host")
    delete_from_conf(glance_api_conf, "keystone_authtoken", "auth_port")
    delete_from_conf(glance_api_conf, "keystone_authtoken", "auth_protocol")
    #add_to_conf(glance_api_conf, "DEFAULT", "db_enforce_mysql_charset", "false")

    add_to_conf(glance_registry_conf, "DEFAULT", "sql_connection", "mysql://glance:openstack@controller/glance")
    add_to_conf(glance_registry_conf, "paste_deploy", "flavor", "keystone")
    add_to_conf(glance_registry_conf, "DEFAULT", "verbose", "true")
    add_to_conf(glance_registry_conf, "DEFAULT", "debug", "true")
    add_to_conf(glance_registry_conf, "DEFAULT", "notification_driver", "noop")
    add_to_conf(glance_registry_conf, "keystone_authtoken", "auth_uri", "http://controller:5000/v2.0")
    add_to_conf(glance_registry_conf, "keystone_authtoken", "identity_uri", "http://controller:35357")
    add_to_conf(glance_registry_conf, "keystone_authtoken", "admin_tenant_name", "service")
    add_to_conf(glance_registry_conf, "keystone_authtoken", "admin_user", "glance")
    add_to_conf(glance_registry_conf, "keystone_authtoken", "admin_password", "openstack")
    add_to_conf(glance_registry_conf, "glance_store", "default_store", "file")
    add_to_conf(glance_registry_conf, "glance_store", "filesystem_store_datadir", "/var/lib/glance/images/")
    delete_from_conf(glance_registry_conf, "keystone_authtoken", "auth_host")
    delete_from_conf(glance_registry_conf, "keystone_authtoken", "auth_port")
    delete_from_conf(glance_registry_conf, "keystone_authtoken", "auth_protocol")

    execute("glance-manage db_sync")

    execute("service glance-api restart", True)
    execute("service glance-registry restart", True)
    




def install_and_configure_nova():
    nova_conf = "/etc/nova/nova.conf"
    
    
    execute_db_commnads("DROP DATABASE IF EXISTS nova;")
    execute_db_commnads("CREATE DATABASE nova;")
    execute_db_commnads("GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'openstack';")
    execute_db_commnads("GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'controller' IDENTIFIED BY 'openstack';")

<<<<<<< HEAD
    execute("apt-get -f install nova-api nova-cert nova-conductor nova-consoleauth  nova-novncproxy nova-scheduler python-novaclient-y", True)
=======
    execute("apt-get install nova-api nova-cert nova-conductor nova-consoleauth  nova-novncproxy nova-scheduler python-novaclient -y", True)
>>>>>>> origin/master


    add_to_conf(nova_conf, "database", "connection", "mysql://nova:openstack@controller/nova")
    add_to_conf(nova_conf, "DEFAULT", "rabbit_host", "controller" )
    add_to_conf(nova_conf, "DEFAULT", "rabbit_password", "openstack" )
    add_to_conf(nova_conf, "DEFAULT", "rpc_backend", "rabbit" )
    add_to_conf(nova_conf, "keystone_authtoken", "auth_uri", "http://controller:5000/v2.0")
    add_to_conf(nova_conf, "keystone_authtoken", "identity_uri", "http://controller:35357")
    add_to_conf(nova_conf, "keystone_authtoken", "admin_tenant_name", "service")
    add_to_conf(nova_conf, "keystone_authtoken", "admin_user", "nova")
    add_to_conf(nova_conf, "keystone_authtoken", "admin_password", "openstack")
    delete_from_conf(nova_conf, "keystone_authtoken", "auth_host")
    delete_from_conf(nova_conf, "keystone_authtoken", "auth_port")
    delete_from_conf(nova_conf, "keystone_authtoken", "auth_protocol")
    add_to_conf(nova_conf, "DEFAULT", "my_ip", "10.10.10.10")
    add_to_conf(nova_conf, "DEFAULT", "vncserver_proxyclient_address", "10.10.10.10")
    add_to_conf(nova_conf, "DEFAULT", "vncserver_listen", "10.10.10.10")
    add_to_conf(nova_conf, "glance", "host", "controller")
    add_to_conf(nova_conf, "DEFAULT", "verbose", "True")
    add_to_conf(nova_conf, "DEFAULT", "debug", "True")
    add_to_conf(nova_conf, "DEFAULT", "auth_strategy", "keystone")
    
    #===================== FOR NEUTRON =============================================================
    
    add_to_conf(nova_conf, "DEFAULT", "network_api_class", "nova.network.neutronv2.api.API")
    add_to_conf(nova_conf, "DEFAULT", "security_group_api", "neutron")
    add_to_conf(nova_conf, "DEFAULT", "linuxnet_interface_driver", "nova.network.linux_net.LinuxOVSInterfaceDriver")
    add_to_conf(nova_conf, "DEFAULT", "firewall_driver", "nova.virt.firewall.NoopFirewallDriver")
    
    add_to_conf(nova_conf, "neutron", "admin_username", "neutron")
    add_to_conf(nova_conf, "neutron", "admin_password", "openstack")
    add_to_conf(nova_conf, "neutron", "admin_tenant_name", "service")
    add_to_conf(nova_conf, "neutron", "admin_auth_url", "http://controller:5000/v2.0/")
    add_to_conf(nova_conf, "neutron", "url", "http://controller:9696/")
 
    
  
  
  
    execute("nova-manage db sync")
    execute("service nova-api restart", True)
    execute("service nova-cert restart", True)
    execute("service nova-scheduler restart", True)
    execute("service nova-conductor restart", True)
    execute("service nova-consoleauth restart", True)
    execute("service nova-novncproxy restart", True)


def install_and_configure_neutron():
    neutron_conf = "/etc/neutron/neutron.conf"
    neutron_plugin_conf = "/etc/neutron/plugins/ml2/ml2_conf.ini"
       

    execute_db_commnads("DROP DATABASE IF EXISTS neutron;")
    execute_db_commnads("CREATE DATABASE neutron;")
    execute_db_commnads("GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'openstack';")
    execute_db_commnads("GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'controller' IDENTIFIED BY 'openstack';")

    execute("apt-get -f install neutron-server -y", True)
    execute("apt-get -f install neutron-plugin-ml2 python-neutronclient -y",True)
    
    #add_to_conf(neutron_conf, "database", "connection", "mysql://neutron:openstack@controller/neutron")
    add_to_conf(neutron_conf, "database", "connection", "mysql://neutron:openstack@controller/neutron")
    add_to_conf(neutron_conf, "DEFAULT", "verbose", "True")
    add_to_conf(neutron_conf, "DEFAULT", "rabbit_host", "controller" )
    add_to_conf(neutron_conf, "DEFAULT", "rabbit_password", "openstack" )
    add_to_conf(neutron_conf, "DEFAULT", "rpc_backend", "rabbit" )
    add_to_conf(neutron_conf, "keystone_authtoken", "auth_uri", "http://controller:5000/v2.0")
    add_to_conf(neutron_conf, "keystone_authtoken", "identity_uri", "http://controller:35357")
    add_to_conf(neutron_conf, "keystone_authtoken", "admin_tenant_name", "service")
    add_to_conf(neutron_conf, "keystone_authtoken", "admin_user", "neutron")
    add_to_conf(neutron_conf, "keystone_authtoken", "admin_password", "openstack")
    delete_from_conf(neutron_conf, "keystone_authtoken", "auth_host")
    delete_from_conf(neutron_conf, "keystone_authtoken", "auth_port")
    delete_from_conf(neutron_conf, "keystone_authtoken", "auth_protocol")
    
    add_to_conf(neutron_conf, "DEFAULT", "core_plugin", "ml2")
    add_to_conf(neutron_conf, "DEFAULT", "service_plugins", "router")
    add_to_conf(neutron_conf, "DEFAULT", "allow_overlapping_ips", "True")
    
    
    add_to_conf(neutron_conf, "DEFAULT", "debug", "True")

    
    add_to_conf(neutron_conf, "DEFAULT", "notify_nova_on_port_status_changes", "True")
    add_to_conf(neutron_conf, "DEFAULT", "notify_nova_on_port_data_changes", "True")
    add_to_conf(neutron_conf, "DEFAULT", "nova_url", "http://controller:8774/v2")
    add_to_conf(neutron_conf, "DEFAULT", "nova_admin_username", "nova")
    add_to_conf(neutron_conf, "DEFAULT", "nova_admin_password", "openstack")
    add_to_conf(neutron_conf, "DEFAULT", "nova_admin_tenant_id", service_tenant)
    add_to_conf(neutron_conf, "DEFAULT", "nova_admin_auth_url", "http://controller:5000/v2.0/")

    
    add_to_conf(neutron_plugin_conf, "ml2", "type_drivers", "flat,gre")
    add_to_conf(neutron_plugin_conf, "ml2", "tenant_network_types", "gre")
    add_to_conf(neutron_plugin_conf, "ml2", "mechanism_drivers", "openvswitch")
    add_to_conf(neutron_plugin_conf, "ml2_type_gre", "network_vlan_ranges", "1:1000")
    
    add_to_conf(neutron_plugin_conf, "securitygroup", "enable_security_group", "true")
    add_to_conf(neutron_plugin_conf, "securitygroup", "enable_ipset", "true")
    add_to_conf(neutron_plugin_conf, "securitygroup", "firewall_driver", "neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver")
    
    execute("neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade juno")
    
    execute("service nova-api restart", True)
    execute("service nova-scheduler restart", True)
    execute("service nova-conductor restart", True)
    execute("service neutron-server restart", True)


def install_and_configure_dashboard():
    execute("apt-get -f install openstack-dashboard apache2 libapache2-mod-wsgi memcached python-memcache -y", True)
    execute("service apache2 restart", True)

initialize_system()
install_rabbitmq()
install_database()
install_and_configure_keystone()
install_and_configure_glance()
install_and_configure_nova()
install_and_configure_neutron()
install_and_configure_dashboard()
print_format(" Installation successfull! Login into horizon http://controller/horizon  Username:admin  Password:openstack ")
