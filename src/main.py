#!/usr/bin/env python3

import docker
import logging
import json
import argparse
import os

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

    cpu_count = os.cpu_count()
    logging.info(f"Host has {cpu_count} CPUs available")
    
    host_gpus = read_gpu_uids()
    logging.info('Host gpus: ' + ','.join(host_gpus))

    # Number of cores per each GPUs
    if args.pinning_mode == "auto":
        n_cores = cpu_count // len(host_gpus)
        logging.info(f"Pinning mode set to auto: reserving {n_cores} cores per GPU")
        
        logging.info("Building GPU-CPU affinity map..")
        affinity_map = {}
        for i, uuid in enumerate(host_gpus):
            start_cpu = i * n_cores
            end_cpu = start_cpu + n_cores - 1
            affinity_map.update({uuid: [start_cpu, end_cpu]})
        
        logging.info("Done.")
        logging.debug(affinity_map)

    logging.info("Connecting to docker daemon..")
    client = docker.from_env()

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
                