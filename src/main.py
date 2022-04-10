#!/usr/bin/env python3

import docker
import logging
import json
import argparse

def read_gpu_uids():
    """Read host GPU uuids from /etc/docker/daemon.json
       Must be mounted with -v /etc/docker/deaemon.json:/etc/docker/daemon.json
    """
    with open("/etc/docker/daemon.json", "r") as f:
        data = json.load(f)

    resources = data['node-generic-resources']
    resources = filter(lambda r: 'gpu=' in r, resources)
    resources = map(lambda r: r.replace('gpu=', ''), resources)
    return list(resources)

def get_gpu_uids(container):
    config = client.api.inspect_container(actor['ID'])['Config']
    env = config['Env']
    gpus = list(filter(lambda venv: "DOCKER_RESOURCE_GPU" in venv, env))
    return gpus

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Docker Swarm cpu auto-pinner",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--pinning_mode', type=str, default="auto", 
                        help='if auto, distribute cpu cores evenly among host GPUs')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    client = docker.from_env()
    
    host_gpus = read_gpu_uids()
    logging.info('Host gpus: ' + ','.join(host_gpus))

    logging.info('Starting listener..')
    for event in client.events(decode=True):
        if not (event['Type'] == 'container' and event['Action'] == 'start'):
            continue

        actor = event['Actor']
        logging.info(f"New container started: {actor['Attributes']['name']}, {actor['ID']}")

        container = client.containers.get(actor['ID'])
        print('container:', container)
        
        gpus = get_gpu_uids(container)
        logging.info(f"GPUs assigned to {actor['Attributes']['name']}: {gpus}")
                