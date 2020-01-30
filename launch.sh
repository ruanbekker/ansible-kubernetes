#!/usr/bin/env bash

SERVER1_IP=$(python deploy_vultr_server.py --action create --region eu-nl --plan cpu2_ram4gb --os ubuntu18 --sshkey personal-laptop --hostname master)
SERVER2_IP=$(python deploy_vultr_server.py --action create --region eu-nl --plan cpu1_ram2gb --os ubuntu18 --sshkey personal-laptop --hostname worker1)
SERVER3_IP=$(python deploy_vultr_server.py --action create --region eu-nl --plan cpu1_ram2gb --os ubuntu18 --sshkey personal-laptop --hostname worker2)

while [ $(timeout 2 bash -c "</dev/tcp/${SERVER1_IP}/22" > /dev/null 2>&1 ; echo $?) != 0 ]
do
  sleep 10
done

while [ $(timeout 2 bash -c "</dev/tcp/${SERVER2_IP}/22" > /dev/null 2>&1 ; echo $?) != 0 ]
do
  sleep 10
done

while [ $(timeout 2 bash -c "</dev/tcp/${SERVER3_IP}/22" > /dev/null 2>&1 ; echo $?) != 0 ]
do
  sleep 10
done

cat > k8s_hosts << EOF
[masters]
master ansible_host=${SERVER1_IP} ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa

[workers]
worker1 ansible_host=${SERVER2_IP} ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa
worker2 ansible_host=${SERVER3_IP} ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa

[all:vars]
ansible_python_interpreter=/usr/bin/python3
EOF

sleep 2

ansible-playbook -i k8s_hosts initial.yml
ansible-playbook -i k8s_hosts kube-dependencies.yml
ansible-playbook -i k8s_hosts master.yml
ansible-playbook -i k8s_hosts workers.yml
ansible-playbook -i k8s_hosts setup-kubeconfig.yml

sleep 10

ssh ubuntu@${SERVER1_IP} kubectl get nodes

export KUBECONFIG="kubeconfig"
kubectl get nodes

# delete servers
#python deploy_vultr_server.py --action delete --serverid $(python deploy_vultr_server.py --action list | cut -d ':' -f1 | cut -d "'" -f2)
#python deploy_vultr_server.py --action delete --serverid $(python deploy_vultr_server.py --action list | cut -d ':' -f1 | cut -d "'" -f2)
#python deploy_vultr_server.py --action delete --serverid $(python deploy_vultr_server.py --action list | cut -d ':' -f1 | cut -d "'" -f2)
