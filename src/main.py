from flask import Flask
from flask import jsonify
from flask import request
app = Flask(__name__)
import random
import boto3
import os
import csv
import time

ec2 = boto3.resource('ec2')


def create_new_region():
    #return new region, maybe needed further down line
    regions_list = []
    with open('regionslist.csv', 'r') as f:
        csv_reader = csv.reader(f)
        regions_list = list(csv_reader)
        for reg in regions_list:
            for r in reg:
                if '.' not in r and 'gov' not in r and r.islower():
                    regions_list.append(r)
                else:
                    continue
    return regions_list

def remove_ec2_instance(instance_id):
    #function to stop and remove an ec2 instance
    instance = ec2.Instance(instance_id)
    instance.terminate()
    return instance_id


def create_new_ec2_instance(instance_count):
    #function to start instance
    ami_id = 'ami-0afbec417ce8b6702'
    if instance_count < 21:
        instance_count += 1
        instance = ec2.create_instances(
            ImageId = ami_id,
            MinCount=1,
            MaxCount=instance_count,
            InstanceType='t2.micro',
            KeyName=os.environ.get('AWSKEYS'),
            SecurityGroupIds=[
                'custom_satellite',
            ]
        )
        return instance
    else:
        return


def proxy_ips():
    #get all the ip addresses into list
    proxy_list = []
    for inst in ec2.instances.all():
        if inst:
            proxy_list.append(inst.public_ip_address)
        else:
            continue
    return proxy_list


@app.route('/', methods=['GET'])
def server_running():
    #aim return randomly selected ip of aws instance
    prox_list = proxy_ips()
    if len(prox_list) > 0:
        prox_string = str(random.choice(prox_list)) + ':8888'
        return jsonify({'new_ip': prox_string})
    else:
        id = create_new_ec2_instance(1)
        time.sleep(30)
        return jsonify({'instance_id': id})


@app.route('/proxy', methods=['GET','POST'])
def new_proxy():
    instance_count = len(proxy_ips())
    if request.method == "POST":
        if instance_count == 0:
            instance_count = 2
            create_new_ec2_instance(instance_count)
        elif instance_count > 0 < 21:
            instance_count += 1
            create_new_ec2_instance(instance_count)
        else:
            instance_ip = request.get_json()
            for inst in ec2.instances.all():
                if inst.public_ip_address == instance_ip['ip']:
                    remove_ec2_instance(inst.id)
                else:
                    continue
        return jsonify({'message':'proxy_list updated'})
    else:
        new_ips_list = proxy_ips()
        return jsonify({'ips list': new_ips_list})

if __name__ == '__main__':
    app.run(port=5000, threaded=True, host=('0.0.0.0'))
