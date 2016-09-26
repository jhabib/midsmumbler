# MIDS W251 - Mumbler

## Overview
I took a client-server approach this mumbler project. The server environment consists of three GPFS nodes cleverly named gpfs1, gpfs2 and gpfs3. I submitted the IP addresses and login info for these VSes on ISVC.

This picture probably does a better job of explaining my mumbler implementation than I ever could in my ESL.

![mumbler overview](https://github.com/jhabib/midsmumbler/blob/master/midsmumbler.png?raw=true "mumbler overview")

A few words nonetheless:
* Each gpfs node has it's own un-replicated sqlite database 
* gpfs1_bigrams.db resides locally on gpfs1 and stores all bigram counts from files 0 through 32; gpfs2_bigrams,db and gpfs3_bigrams.db reside on their own nodes and store bigram counts from files 33-66 and 67-99 respectively
* Each gpfs node gets it's own instance of a REST server. Each server serves up results from it's own db.
* The client takes a starting word and queries all servers for results. It then combines the results, picks the next "start" word based on weighted probability and repeats the process.
* The client keeps repeating the process until the desired chain length is achieved or until a start word is not found.

