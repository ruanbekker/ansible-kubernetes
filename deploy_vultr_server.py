import requests
import argparse
import json
import time

parser = argparse.ArgumentParser(description='vultr')
parser.add_argument('-a', '--action', help='create (required)', required=False)
parser.add_argument('-r', '--region', help='region to deploy vm (required)', required=False)
parser.add_argument('-p', '--plan', help='vm size (required)', required=False)
parser.add_argument('-o', '--os', help='os (required)', required=False)
parser.add_argument('-s', '--sshkey', help='sshkey (required)', required=False)
parser.add_argument('-n', '--hostname', help='hostname (required)', required=False)
parser.add_argument('-i', '--serverid', help='serverid (required)', required=False)
args = parser.parse_args()


VULTR_API_TOKEN = "${VULTR_API_TOKEN}"
VULTR_API_URL_SERVER_CREATE = "https://api.vultr.com/v1/server/create"
VULTR_API_URL_SERVER_LIST = "https://api.vultr.com/v1/server/list"
VULTR_API_URL_SERVER_DELETE = "https://api.vultr.com/v1/server/destroy"

vultr_inventory_map = {
    "regions": {
        "eu-nl": "7",
        "eu-gb": "8",
        "us-wa": "4",
        "us-ca": "12"
    },
    "plans": {
        "cpu1_ram1gb": "201",
        "cpu1_ram2gb": "202",
        "cpu2_ram4gb": "203",
        "cpu4_ram8gb": "204"
    },
    "os": {
        "centos7": "167",
        "centos8": "362",
        "ubuntu18": "270",
        "debian10": "352",
        "coreos": "179"
    },
    "sshkey": {
        "work-laptop": "xx",
        "personal-laptop": "yy"
    }
}

def list():
    response = requests.get(VULTR_API_URL_SERVER_LIST, headers={"API-Key": VULTR_API_TOKEN})
    return response.json()

def lookup(server_id):
    response = requests.get(VULTR_API_URL_SERVER_LIST, headers={"API-Key": VULTR_API_TOKEN}).json()
    serverip = response[server_id]['main_ip']
    return serverip

def create(region, plan, os, sshkey, hostname):
    response = requests.post(
        VULTR_API_URL_SERVER_CREATE,
        headers={"API-Key": VULTR_API_TOKEN},
        data={
            "DCID": vultr_inventory_map['regions'][region],
            "VPSPLANID": vultr_inventory_map['plans'][plan],
            "OSID": vultr_inventory_map['os'][os],
            "hostname": hostname,
            "tag": "api",
            "label": hostname,
            "SSHKEYID": vultr_inventory_map['sshkey'][sshkey]
        }
    ).json()
    server_id = response['SUBID']
    time.sleep(10)
    return lookup(server_id)

def delete(server_id):
    response = requests.post(VULTR_API_URL_SERVER_DELETE, headers={"API-Key": VULTR_API_TOKEN}, data={"SUBID": server_id})
    return response.status_code

if args.action == "create":
    response = create(args.region, args.plan, args.os, args.sshkey, args.hostname)
    print(response)

if args.action == "lookup":
    response = lookup(args.serverid)
    print(response)

if args.action == "delete":
    response = delete(args.serverid)
    print(response)

if args.action == "list":
    response = list()
    print(response)
