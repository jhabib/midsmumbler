# ssh-keygen -R ip_address
# ssh-copy-id -i /home/root/.ssh/id_rsa/id_rsa.pub root@ip_address

# copy ssh key-pair to gpfs nodes
salt-cp 'gpfs2' /home/root/.ssh/id_rsa/id_rsa /root/.ssh/
salt-cp 'gpfs2' /home/root/.ssh/id_rsa/id_rsa.pub /root/.ssh/

# set permissions on private key
salt 'gpfs2' cmd.run "chmod 600 /root/.ssh/id_rsa"

# Setup hosts file here

# create a nodefile as /root/nodefile and execute command below
salt 'gpfs*' cmd.run "echo $'gpfs1:quorum:\ngpfs2::\ngpfs3::' >> /root/nodefile"

salt 'gpfs*' cmd.run "wget -O /root/GPFS_4.1_STD_LSX_QSG.tar http://b0a3.http.dal05.cdn.softlayer.net/brad-impact-demo-test/SaharaImage/GPFS_4.1_STD_LSX_QSG.tar"

salt 'gpfs*' cmd.run "cd /root/ && tar -xvf GPFS_4.1_STD_LSX_QSG.tar"
salt 'gpfs*' cmd.run "/root/gpfs_install-4.1.0-0_x86_64 --silent"

salt 'gpfs*' cmd.run "cd /usr/lpp/mmfs/4.1 && yum install -y kernel"
salt 'gpfs*' system.reboot && salt 'gpfs*' cmd.run "last reboot | less"


salt 'gpfs*' cmd.run "yum -y install ksh gcc-c++ compat-libstdc++-33 kernel-devel redhat-lsb net-tools libaio"

salt 'gpfs*' cmd.run "uname -r"

# KERN_VER=$(salt 'gpfs*' cmd.run "uname -r" | grep -v $'gpfs*' | head -1)
# 2.6.32-642.3.1.el6.x86_64

salt 'gpfs*' cmd.run "uname -r"
KERN_VER=2.6.32-642.3.1.el6.x86_64

salt 'gpfs*' cmd.run "cd /lib/modules/$KERN_VER && rm -f build && ln -sf /usr/src/kernels/$KERN_VER build"

salt 'gpfs*' cmd.run "cd /lib/modules/$KERN_VER && rpm -ivh /usr/lpp/mmfs/4.1/gpfs*.rpm"

salt 'gpfs*' cmd.run "cd /usr/lpp/mmfs/src && make Autoconfig && make World && make InstallImages"

# salt 'gpfs1' cmd.run "mmcrcluster -C habibi -p gpfs1 -s gpfs2 -R /usr/bin/scp -r /usr/bin/ssh -N /root/nodefile"

# SSH into gpfs1
# salt cmd.run could not find mmcrcluster
# I had added /usr/lpp/mmfs/bin to PATH in both ~/.bashrc and ~/.bash_profile
# Neither worked for salt cmd.run
# Commands below were run after ssh into gpfs1

mmcrcluster -C habibi -p gpfs1 -s gpfs2 -R /usr/bin/scp -r /usr/bin/ssh -N /root/nodefile
mmchlicense server -N all
mmstartup -a
mmgetstate -a

salt 'gpfs*' cmd.run "fdisk -l | grep Disk | grep bytes"
salt 'gpfs*' cmd.run "mount | grep ' \/ '"

touch /root/diskfile.fpo
# edit diskfile.fpo and configure the 25GB disks
mmcrnsd -F /root/diskfile.fpo
mmlsnsd -m
mmcrfs gpfsfpo -F /root/diskfile.fpo -A yes -Q no -r 1 -R 1
mmlsfs all
mmmount all -a
cd /gpfs/gpfsfpo
df -h .
touch aa
ls -l /gpfs/gpfsfpo
# ssh gpfs2 'ls -l /gpfs/gpfsfpo'
# ssh gpfs3 'ls -l /gpfs/gpfsfpo'


