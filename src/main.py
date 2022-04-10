#!/usr/bin/env python3

import docker
import logging

def read_gpu_uids():
    """Read host GPU uuids from /etc/docker/daemon.json
       Must be mounted with -v /etc/docker/deaemon.json:/etc/docker/daemon.json
    """
    pass

def get_gpu_uids(container):
    config = client.api.inspect_container(actor['ID'])['Config']
    env = config['Env']
    gpus = list(filter(lambda venv: "DOCKER_RESOURCE_GPU" in venv, env))
    return gpus

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = docker.from_env()
    
    filters = {'Type': 'container', 'Action': 'start'}
    for event in client.events(decode=True):
        if not (event['Type'] == 'container' and event['Action'] == 'start'):
            continue

        actor = event['Actor']
        logging.info(f"New container started: {actor['Attributes']['name']}, {actor['ID']}")

        container = client.containers.get(actor['ID'])
        print('container:', container)
        
        gpus = get_gpu_uids(container)
        logging.info(f"GPUs assigned to {actor['Attributes']['name']}: {gpus}")
                