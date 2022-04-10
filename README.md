# Swarm CPU pinner

## Automatic CPU pinning for docker-swarm-based GPU HPC cluster 

- Docker swarm does not support the ```--cpuset-cpus``` argument.
- This package provides a way to automatically assign a predefined set of cores to a swarm service, based on the GPU(s) it is using.
- It runs as global service on a swarm cluster (replicated on each node), intercepts the creation of new containers, and update their cpu affinity settings at runtime

**PoC use-case:** 3 nodes with each:
- 8 gpus
- 96 cpu cores

Pinning is the best way to obtain maximum performance, and avoid multiple containers contesting the same cores.

In the setup above, 96/8 = 12 cores can be dedicated to each single GPU.

This package works by looking for the DOCKER_RESOURCE_GPU in the container env vars, and matching the gpu uuid with the contents of /etc/docker/daemon.json (for details: https://gist.github.com/tomlankhorst/33da3c4b9edbde5c83fc1244f010815c)

### Example usage

On the swarm manager run (first, build the image with the provided Dockerfile):

```bash
docker service create \
    --restart-condition=on-failure \
    --mode global \
    --mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock \ 
    --mount type=bind,source=/etc/docker/daemon.json,destination=/etc/docker/daemon.json \
    --hostname {{.Service.Name}}-{{.Node.Hostname}} \
    --name ghcr.io/eidoslab/swarm-cpupin:1.0.2
```

Now, when you deploy swarm services with 

```
docker service create ... \
    --generic-resource gpu=1 \
    ...
```
the spawned container(s) will be automatically pinned to the corresponding cpu cores.
