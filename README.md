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
I used the steps below to download and preprocess the files. This step came before I wrote the client-server thing.

### Step 1 - Downloading and some preprocessing 
There is a `zip_downloader.py` script in the download_and_preprocess folder that I used to download, unzip and pre-process the files. This script was run on gpfs1, gpfs2 and gpfs3 with different parameters for Google ngram file ranges. That way each gpfs node got its own set of ~33 local files. This script does the following:
* Downloads the zip files as a stream (in memory). Since Google stored their data as a .zip and not a tar.gz file, I could not unzip line by line. 
* Extarcts each line from the in memory file and splits it into 'bigram', 'year', 'count' ... The bigram is convered to 'ascii' and any non-ascii encodable bigrams are discarded.
* Builds an in memory dictionary of bigram, value pairs
* Once all lines have been read from the file, dumps it to disk in a binary format using python's pickle. This results in a file size of ~46MB for each file.
This download and pre-process step took nearly 3 hours on each node. I of course ran the thing in parallel.

The 100 files thus downloaded and pre-processed resulted in a total on disk size of ~4.5GB - a tad better from the original ~150GB or so uncompressed. Please note I never needed to store that 150GB on disk in this process.

### Step 2 - Creating databases
Once everything was downloaded I ran the `create_db.py` script from the download_and_preprocess folder on each gpfs node. I used the file numbers that were local to each node to create a local sqlite database on each node. This script does the following:
* **Drops** the database if it exists. Please do not run this script as it will take a couple of hours to create each database.
* Reads in and unpickles each downloaded, pickled file. (0-32 for gpfs1, 33-66 for gpfs2 and so forth).
* Breake the bigrams into a first word and a second word.
* Inserts or updates the row into the named table as appropriate.
I ran this script individually on each gpfs node with the correct parameters for file indexes and the database name. I then ran the script `index_db.py` to create indexes. 

Note: I wasn't initially sure whether I wanted an auto-increment id in my table so `create_db.py` did not create a table that had the auto-increment id. Later, I figured it would be good to have this for future optimization so I manually created a new table named `bigrams_counts_id` in each of the three databases and dumped the data from the original table. I also created indexes on first words and second words.
The SQL statements used for copying the database tables are in the `gpfs_add_autoincrement_id.txt` file.

After all this pre-processing, each database table occupied ~1.7GB of space on disk. The databases are about twice that size because I'm keeping the tables my script created earlier. I don't want to drop it yet out of fear of things falling apart - you know how software development goes ;)

## Future Optimizations
Since RedHat fought me every step of the way in this project I ran out of time to work on some optimizations I had thought of.
* Currently, each server sends back the results to the client for each word. These results include ID, FirstWord, SecondWord and Count. Since I have a unique ID for each tuple in there, I can only send the ID and Count back to the Client. The client can then query the right server based on this unique ID to get the SecondWord. And then repeat the process of selection.
* The process of weighted selection can be distributed to each gpfs node as well. Essentially, each node will send back the sum of its counts to the client. The client will build a range summing together the sums and pick a random number in that range. The client will send the random number to each node, along with an index that each node can use to calculate the range that belongs to it. Each node would then either return a second-word or nothing. Since there is one random number and a unique subset of total range mapped to each node, I would get back only one word. The process would then be repeated until a chain was built.

## Broken Dreams
Initially I tried working directly with the unadulterated, unzipped .txt files. This proved to be a slow approach because of the reasons below:
* It's not easily possible to access a random line in a text file
* Pre-processing each file to get offsets of where each line begins takes time and results in a bunch of data. 
* While these offsets can be used for binary search over the files, loading the offsets files into memory needed ~4-5 seconds. 
* A modified binary search that decrements the range by the number of bytes read in the last line (from a random byte position) is slow for large files. Essentially, in this approach, I tried finding a line starting at a random **byte** offset and then looking for a line there. 
* I tried Roulette Selection with Stochastic Acceptance to pick the next word but that approach was slow to the iterative approach I ended up using. 
You can see how this went in the `broken_mumbler.py` file under the `broken_dreams` folder. I didn't really scale this approach to all files.

