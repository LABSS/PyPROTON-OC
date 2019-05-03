# dockerize proton-oc

# setup

## requirements

1. Install Docker
2. put ssh keys on the machine so that it can fetch the release from the git.
3. create the working directory: `~/commondisk`
4. a working release with its tag (ex. v0.3)

## create the netlogo base: 
```
docker build --tag=labss/netlogo-base
```

## create the OC docker from a release
```
 docker build --tag=labss/oc --build-arg SSH_KEY="$(cat ~/.ssh/id_rsa)" --build-arg OC_VERSION='v0.3' .
```


# useful docker instructions

## clean up
```docker ps -a
docker ps --filter "status=exited" | grep 'weeks ago' | awk '{print $1}' | xargs --no-run-if-empty docker rm
```

# create the simulation with the exp.xml file from 
 docker build --tag=labss/oc --build-arg SSH_KEY="$(cat ~/.ssh/id_rsa)" .

 docker build --tag=labss/oc --build-arg SSH_KEY="$(cat ~/.ssh/id_rsa)" --build-arg OC_VERSION='v0.3-alpha' .

docker build --tag=labss/protont --build-arg SSH_KEY="$(cat ~/.ssh/id_rsa)" --build-arg T_VERSION='v0.2a' .


docker push labss/protont


# interactive run

docker run --entrypoint "/bin/bash" -v /home/mario/commondisk:/extdisk -it  oc 

# real run

cp ../T/docker/extdisk-skeleton/* .

docker run -v ~/commondisk:/extdisk  -d labss/protont
docker run -v ~/commondisk:/extdisk  -it labss/protont
docker run --entrypoint "/bin/bash" -v ~/commondisk:/extdisk -it labss/protont

docker run -v /home/mario/commondisk:/extdisk  -t oc

 docker exec -it 91aee0d32a92 /bin/bash


# upload 

docker push labss/protont

# share results (in the directory to share; turn off other servers on 80, like R)

sudo rstudio-server stop
python -m SimpleHTTPServer

# AZURE----------------------------------------

# mount the files in the container

STORAGE_KEY=$(az storage account keys list --resource-group OCtest --account-name mario.paolucci@istc365.onmicrosoft.com
 --query "[0].value" --output tsv)

 # Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=OCtest
ACI_PERS_STORAGE_ACCOUNT_NAME=ahem$RANDOM
ACI_PERS_LOCATION=northeu
ACI_PERS_SHARE_NAME=acishare

# Create the storage account with the parameters
az storage account create \
    --resource-group $ACI_PERS_RESOURCE_GROUP \
    --name $ACI_PERS_STORAGE_ACCOUNT_NAME \
    --location $ACI_PERS_LOCATION \
    --sku Standard_LRS

# Create the file share
az storage share create --name $ACI_PERS_SHARE_NAME --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME


az container create \
    --resource-group OCtest \
    --name proton-t-compare-10k-1c-1000s \
    --cpu 1 \
    --image labss/protont:latest \
    --dns-name-label aci-demo$RANDOM \
    --ports 80 \
    --restart-policy Never \
    --azure-file-volume-account-name commondisk \
    --azure-file-volume-account-key DvkQfFeBTGLdgXdGDUmn1y6CU69SCkwUFF/2diHewNadWdEnNZuvvhC3PYJuWC4AIooxqB4QRlWPKtpS1x6qEQ== \
    --azure-file-volume-share-name proton \
    --azure-file-volume-mount-path /extdisk/


# mount the disk from a unix box with crypted samba

    sudo mount -t cifs //commondisk.file.core.windows.net/proton azure-commondisk/  -o vers=3.0,username=commondisk,password=DvkQfFeBTGLdgXdGDUmn1y6CU69SCkwUFF/2diHewNadWdEnNZuvvhC3PYJuWC4AIooxqB4QRlWPKtpS1x6qEQ==,dir_mode=0777,file_mode=0777,sec=ntlmssp

az container exec --resource-group OCtest --name aci-demo9058.northeurope.azurecontainer.io --exec-command /bin/bash/

git config --global user.email "mario.paolucci@gmail.com"
  git config --global user.name "Mario Paolucci"
