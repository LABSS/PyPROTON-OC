# dockerize proton-oc

# setup

## requirements

1. Install and start (`sudo service docker start` on centos) Docker
2. put ssh keys on the machine so that it can fetch the release from the git.
3. create the working directory: `~/commondisk`
4. create (or use) a working release with its tag (ex. v0.3)
5. start from the git base directory
6. prepare an experiment in the form of an xml file
7. the git base should be linked as ~/OC

## create the netlogo base:
from the netlogo-docker directory 
```
cd docker/netlogo-docker/
docker build --tag=labss/netlogo-base .
```

## create the OC docker from a release
from the docker directory
```
cd ..
 docker build --tag=labss/oc --build-arg SSH_KEY="$(cat ~/.ssh/id_rsa)" --build-arg OC_VERSION='v0.3' .
```

# interactive run - testing the docker

docker run --entrypoint "/bin/bash" -v ~/commondisk:/extdisk -it  oc 

# run!
Copy the content of the skeleton on the common disk, then substitute the file `exp.xml` with your own. Then call the docker run command.

```
cp ~/OC/docker/extdisk-skeleton/* ~/commondisk
docker run -v ~/commondisk:/extdisk  -d labss/oc
```

It will run in the container, dumping the results in the commondisk.

# useful docker instructions

# run a terminal in the latest container
``` 
docker exec -it `docker ps -l -q`  /bin/bash
``` 

## run a terminal in a running container
`docker ps` to retrieve the `_ID_`, then `docker exec -it _ID_ /bin/bash`

## clean up
```docker ps -a
docker ps --filter "status=exited" | grep 'weeks ago' | awk '{print $1}' | xargs --no-run-if-empty docker rm
```

# push the container on the online repository
```
docker push labss/oc
```
# share results (in the directory to share; turn off other servers on 80, like R)
```
sudo rstudio-server stop
python -m SimpleHTTPServer
```
