import random
import logging
import string
import os
import inspect
from shutit_module import ShutItModule

class shutit_hands_on_ansible(ShutItModule):


	def build(self, shutit):
		shutit.run_script('''#!/bin/bash
MODULE_NAME=shutit_hands_on_ansible
rm -rf $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/vagrant_run/*
if [[ $(command -v VBoxManage) != '' ]]
then
	while true
	do
		VBoxManage list runningvms | grep ${MODULE_NAME} | awk '{print $1}' | xargs -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | grep shutit_hands_on_ansible | awk '{print $1}'  | xargs -IXXX VBoxManage unregistervm 'XXX' --delete
		# The xargs removes whitespace
		if [[ $(VBoxManage list vms | grep ${MODULE_NAME} | wc -l | xargs) -eq '0' ]]
		then
			break
		else
			ps -ef | grep virtualbox | grep ${MODULE_NAME} | awk '{print $2}' | xargs kill
			sleep 10
		fi
	done
fi
if [[ $(command -v virsh) ]] && [[ $(kvm-ok 2>&1 | command grep 'can be used') != '' ]]
then
	virsh list | grep ${MODULE_NAME} | awk '{print $1}' | xargs -n1 virsh destroy
fi
''')
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		shutit.build['vagrant_run_dir'] = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + '/vagrant_run'
		shutit.build['module_name'] = 'shutit_hands_on_ansible_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.build['this_vagrant_run_dir'] = shutit.build['vagrant_run_dir'] + '/' + shutit.build['module_name']
		shutit.send(' command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		shutit.send('command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		if shutit.send_and_get_output('vagrant plugin list | grep landrush') == '':
			shutit.send('vagrant plugin install landrush')
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file(shutit.build['this_vagrant_run_dir'] + '/Vagrantfile','''Vagrant.configure("2") do |config|
  config.landrush.enabled = true
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
  end

  config.vm.define "ansibleacs" do |ansibleacs|
    ansibleacs.vm.box = "ubuntu/trusty64"
    ansibleacs.vm.hostname = "ansibleacs.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_hands_on_ansible_acs"
    end
  end
  config.vm.define "ansibleweb" do |ansibleweb|
    ansibleweb.vm.box = "centos/7"
    ansibleweb.vm.hostname = "ansibleweb.vagrant.test"
    ansibleweb.vm.network "forwarded_port", guest: 80, host: 8080
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_hands_on_ansible_web"
    end
  end
  config.vm.define "ansibledb" do |ansibledb|
    ansibledb.vm.box = "centos/7"
    ansibledb.vm.hostname = "ansibledb.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_hands_on_ansible_db"
    end
  end
end''')
		pw = shutit.get_env_pass()
		try:
			shutit.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + " ansibleacs",{'assword for':pw,'assword:':pw},timeout=99999)
		except NameError:
			shutit.multisend('vagrant up ansibleacs',{'assword for':pw,'assword:':pw},timeout=99999)
		if shutit.send_and_get_output("""vagrant status | grep -w ^ansibleacs | awk '{print $2}'""") != 'running':
			shutit.pause_point("machine: ansibleacs appears not to have come up cleanly")
		try:
			shutit.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + " ansibleweb",{'assword for':pw,'assword:':pw},timeout=99999)
		except NameError:
			shutit.multisend('vagrant up ansibleweb',{'assword for':pw,'assword:':pw},timeout=99999)
		if shutit.send_and_get_output("""vagrant status | grep -w ^ansibleweb | awk '{print $2}'""") != 'running':
			shutit.pause_point("machine: ansibleweb appears not to have come up cleanly")
		try:
			shutit.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + " ansibledb",{'assword for':pw,'assword:':pw},timeout=99999)
		except NameError:
			shutit.multisend('vagrant up ansibledb',{'assword for':pw,'assword:':pw},timeout=99999)
		if shutit.send_and_get_output("""vagrant status | grep -w ^ansibledb | awk '{print $2}'""") != 'running':
			shutit.pause_point("machine: ansibledb appears not to have come up cleanly")


		# machines is a dict of dicts containing information about each machine for you to use.
		machines = {}
		machines.update({'ansibleacs':{'fqdn':'ansibleacs.vagrant.test'}})
		ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines['ansibleacs']['fqdn'] + ''' | awk '{print $2}' ''')
		machines.get('ansibleacs').update({'ip':ip})
		machines.update({'ansibleweb':{'fqdn':'ansibleweb.vagrant.test'}})
		ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines['ansibleweb']['fqdn'] + ''' | awk '{print $2}' ''')
		machines.get('ansibleweb').update({'ip':ip})
		machines.update({'ansibledb':{'fqdn':'ansibledb.vagrant.test'}})
		ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines['ansibledb']['fqdn'] + ''' | awk '{print $2}' ''')
		machines.get('ansibledb').update({'ip':ip})

		for i in (0,1,2):
			shutit.login(command='vagrant ssh ' + sorted(machines.keys())[i],check_sudo=False)
			shutit.send('ssh-keygen',{'Enter':''})
			shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
			shutit.install('ansible')
			shutit.install('sshpass')
			shutit.send('''sed -i 's/ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/g' /etc/ssh/sshd_config''')
			shutit.send('service ssh restart || service sshd restart')
			shutit.logout()
			shutit.logout()

		for i in (0,1,2):
			shutit.login(command='vagrant ssh ' + sorted(machines.keys())[i],check_sudo=False)
			for j in (0,1,2):
				shutit.send('ssh-copy-id vagrant@' + machines[machines.keys()[j]]['ip'],{'ontinue':'yes','assword':'vagrant'})
				shutit.send('ssh-copy-id vagrant@' + machines[machines.keys()[j]]['fqdn'],{'ontinue':'yes','assword':'vagrant'})
				shutit.send('ssh-copy-id vagrant@' + machines.keys()[j],{'ontinue':'yes','assword':'vagrant'})
			shutit.logout()

		i = 2
		shutit.login(command='vagrant ssh ' + sorted(machines.keys())[i],check_sudo=False)
		shutit.login(command='sudo su -',password='vagrant',check_sudo=False)
		shutit.install('gcc')
		shutit.install('python-setuptools')
		shutit.install('python-devel')
		shutit.send('easy_install pip')
		shutit.send('pip install ansible')
		shutit.logout()
		shutit.logout()

		shutit.login(command='vagrant ssh ' + sorted(machines.keys())[0],check_sudo=False)
		shutit.send('mkdir exercise1')
		shutit.send('cd exercise1')
		shutit.send('touch inventory')
		shutit.send('echo ' + str(machines['ansibleweb']['ip']) + ' >> inventory')
		shutit.send('echo ' + str(machines['ansibledb']['ip']) + ' >> inventory')
		shutit.send('ansible ' + str(machines['ansibleweb']['ip']) + ' -i inventory -u vagrant -m ping -k',{'SSH password:':'vagrant'})
		shutit.send('ansible ' + str(machines['ansibleweb']['ip']) + ' -i inventory -u vagrant -m ping -k -vv',{'SSH password:':'vagrant'})
		shutit.send('ansible ' + str(machines['ansibleweb']['ip']) + ' -i inventory -u vagrant -m ping -k -vvv',{'SSH password:':'vagrant'})

		# not working yet?
		#shutit.send('ansible all -i inventory -u vagrant -m command -a "/sbin/ifconfig"',{'SSH':'vagrant'})
		# the same
		#shutit.send('ansible all -i inventory -u vagrant -a "/sbin/ifconfig"',{'SSH':'vagrant'})
		#shutit.send('ansible all -i inventory -u vagrant -m shell -a "/sbin/ifconfig"',{'SSH':'vagrant'})

		shutit.send('cd ..')
		shutit.send('mkdir exercise4.1')
		shutit.send('cd exercise4.1')
		shutit.send('touch inventory')
		shutit.send('echo ' + str(machines['ansibleweb']['fqdn']) + ' ansible_ssh_user=vagrant ansible_ssh_pass=vagrant >> inventory')
		shutit.send('ansible ' + str(machines['ansibleweb']['fqdn']) + ' -i inventory -m ping')
		shutit.send('echo "[webservers]" >> inventory')
		shutit.send('echo ' + str(machines['ansibleweb']['fqdn']) + ' >> inventory')
		shutit.send('echo "[dbservers]" >> inventory')
		shutit.send('echo ' + str(machines['ansibledb']['fqdn']) + ' >> inventory')
		shutit.send('echo "[datacenter:children]" >> inventory')
		shutit.send('echo "webservers" >> inventory')
		shutit.send('echo "dbservers" >> inventory')
		shutit.send('ansible datacenter -i inventory -m ping')
		shutit.send('echo "[datacenter:vars]" >> inventory')
		shutit.send('echo "ansible_ssh_user=vagrant" >> inventory')
		shutit.send('echo "ansible_ssh_pass=vagrant" >> inventory')
		shutit.send('ansible datacenter -i inventory -m ping')

		shutit.send('cd ..')
		shutit.send('mkdir exercise4.2')
		shutit.send('cd exercise4.2')
		shutit.send('mkdir -p {test,production}/{group_vars,host_vars}')
		shutit.send('mkdir -p {test,production}/group_vars')
		shutit.send('mkdir -p {test,production}/host_vars')
		shutit.send('cp ../exercise4.1/inventory production/inventory_prod')
		# all_username is just the username we are creating
		shutit.send('''cat > production/group_vars/all << END
---
# This is our user
username: all_username
END''')
		shutit.send('cd production')
		# variable: {{username}}
		shutit.send('ansible webservers -i inventory_prod -m user -a "name={{username}} password=12345" --sudo')
		# group takes precedence over all
		shutit.send('''cat > production/group_vars/webserver << END
---
# This is our group user
username: group_user
END''')
		shutit.send('ansible webservers -i inventory_prod -m user -a "name={{username}} password=12345" --sudo')
		# web1 takes precedence because we're running it on there. 
		shutit.send('''cat > production/host_vars/web1 << END
---
# This is a comment
username: web1_user
END''')
		shutit.send('ansible webservers -i inventory_prod -m user -a "name={{username}} password=12345" --sudo')
		shutit.pause_point()
		shutit.logout()

		shutit.log('''Vagrantfile created in: ''' + shutit.build['this_vagrant_run_dir'],add_final_message=True,level=logging.DEBUG)
		shutit.log('''Run:

	cd ''' + shutit.build['this_vagrant_run_dir'] + ''' && vagrant status && vagrant landrush ls

To get a picture of what has been set up.''',add_final_message=True,level=logging.DEBUG)
		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/xenial64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')
		return True

	def test(self, shutit):
		return True

	def finalize(self, shutit):

		shutit.log('''Vagrantfile created in: ''' + shutit.build['this_vagrant_run_dir'],add_final_message=True,level=logging.DEBUG)
		shutit.log('''Run:

	cd ''' + shutit.build['this_vagrant_run_dir'] + ''' && vagrant status && vagrant landrush ls

To get a picture of what has been set up.''',add_final_message=True,level=logging.DEBUG)
		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/xenial64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')
		return True

	def test(self, shutit):
		return True

	def finalize(self, shutit):
		return True

	def is_installed(self, shutit):
		return False

	def start(self, shutit):
		return True

	def stop(self, shutit):
		return True

def module():
	return shutit_hands_on_ansible(
		'git.shutit_hands_on_ansible.shutit_hands_on_ansible', 1358775422.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)
