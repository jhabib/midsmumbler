# MIDS W251 - Mumbler

## Overview
I took a client-server approach this mumbler project. The server environment consists of three GPFS nodes cleverly named gpfs1, gpfs2 and gpfs3. I submitted the IP addresses and login info for these VSes on ISVC.

This picture probably does a better job of explaining my mumbler implementation than I ever could in my ESL.

![mumbler overview](https://github.com/jhabib/midsmumbler/blob/master/midsmumbler.png?raw=true "mumbler overview")

A few words nonetheless:
* Each gpfs node has it's own un-replicated sqlite database 
* gpfs1_bigrams.db resides locally on gpfs1 and stores all bigram counts from files 0 through 32; gpfs2_bigrams.db and gpfs3_bigrams.db reside on their own nodes and store bigram counts from files 33-66 and 67-99 respectively
* Each gpfs node gets it's own instance of a REST server. Each server serves up results from it's own db.
* The client takes a starting word and queries all servers for results. It then combines the results, picks the next "start" word based on weighted probability and repeats the process.
* The client keeps repeating the process until the desired chain length is achieved or until a start word is not found.

## Running the mumbler

### Step 1 - Start the Servers
* ssh into gpfs1 using it's IP address and password provided in ISVC e.g. ssh root@ip\_address. Then run the commands below.
Change to the right directory:
* `cd /gpfs/gpfsfpo/bigrams/db`
Start the server using **python2.7** and the **public** ip address and database of this specific server. Do not enter a port.
* `python2.7 mumbler_server.py <108.*.*.*> <gpfs1_bigrams.db>`

ssh into gpfs2 and gpfs3 servers and start those as well. Replace the ip address and database name with appropriate ones for the specific servers. Do not enter the < and > characters.

Once the servers are started you are ready to run the client.

### Step 2 - Running the Client
* ssh into any one of the three gpfs nodes
Change to the right directory:
* `cd /gpfs/gpfsfpo/bigrams/db`
Run the client using **python2.7**:
* `python2.7 mumbler_client.py terminator 5`

NOTE: 
The client (mumbler_client.py) has a hard-coded server IP and port list that points to the public (eth1) IP addresses of the servers. Since these are public IPs you can run the client on your local machine as long as you have Python 2.7.9 and a few dependencies: requests, flask, flask-restful, sqlalchemy. You can pip install the dependencies. Essentially, anything that's an import in the mumbler_client.py should be available on your machine.

If you start the servers with their eth0 IP addresses you will only be able to access the mumbler from the SoftLayer network. If you do that you will also need to edit the server IP addresses in the mumbler_client.py on lines [36, 37, 38]. Essentially the statement that declares `servers = ['', '', '']`. With this, the mumbler will run a little faster but won't be accessible over the public network. You will need to ssh into one of the gpfs nodes and then run the client. The three servers must be started manually before you can run the client.

## Preprocessing and building the database
I used the steps below to download and preprocess the files.
### Downloading and some preprocessing 

