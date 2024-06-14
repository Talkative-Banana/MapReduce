<!-- PROJECT LOGO --> <br /> <p align="center"> <a href="https://github.com/Talkative-Banana/MapReduce"> <img src="logo/Hadoop_logo.svg" alt="Logo"> </a>

# MapReduce
<!-- ABOUT THE PROJECT -->
This Project focuses on Implementing MapReduce framework from scratch to perform K-means clustering on a given dataset in a distributed manner like Hadoop does.

MapReduce is a programming model and an associated implementation for processing and generating large data sets. Users specify a map function that processes a key/value pair to generate a set of intermediate key/value pairs, and a reduce function that merges all intermediate values associated with the same intermediate key. Many real world tasks are expressible in this model, as shown in the paper.

### Built With
<!-- BUILT WITH -->
* [Python](https://www.python.org/)
* [gRPC](https://grpc.io/)
* [Google Cloud](https://cloud.google.com/)

### Table of Contents
<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="implementation">Implementation</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

## Documentation
<!-- DOCUMENTATION -->
### Storage and Database Options

The K-means algorithm is an iterative algorithm that partitions a dataset into K clusters.

* The nodes (mappers or reducers) are persistent, i.e., even after stopping the node, the data (logs) are stored locally (in human-readable format, .txt) and retrieved when the node starts again.

* #### Top level directory layout:
        .MapReduce/
        ├── Input
        |   ├── points.txt (initial points)
        ├── Master/
            ├── dump.txt
            ├── master.py
            ├── message.proto 
        ├── Mappers/
        |   ├── M1
        |       Partition
        |       ├── partition_1.txt
        |       ├── partition_2.txt
        ...
        |       ├── partition_R.txt (R based on the number of reducers)
        |   ├── dump.txt
        |   ├── M2/ ...
        |   ├── M3/ ...
        ...
        ├── Reducer
        |   ├── R1
        |       ├── Output
        |           ├── R1.txt
        |       ├── dump.txt
        |       ├── reducer.py
        |       ├── message.proto
        |   ├── R2/ ...
        |   ├── R3/ ...
        ├── centroid.txt (final list of centroids)
        ├── script.sh

Mappers, Reducers, and Master form a cluster.

## Implementation:
<!-- IMPLEMENTATION -->
* The master stores the IP addresses and ports of all the nodes (mappers and reducers).

### Master: 
* The master program/process is responsible for running and communicating with the other components in the system. When running the master program, the following parameters should be provided as input:
  * number of mappers (M)
  * number of reducers (R)
  * number of centroids (K)
  * number of iterations for K-Means (Note: program stops early if the algorithm converges before)
  * Other necessary information

### Map and Partition (invoked by mapper):
1. **Map**: Mapper read the input split by itself (based on the information provided by the master).
    * Inputs to the Map function: 
        Input split assigned by the master:
        List of Centroids from the previous iteration

    * Output from the Map function: For each data point processed by the map function, the function outputs:
        Key: index of the nearest centroid to which the data point belongs
        Value: value of the data point itself.

    The output of each Map function is written to a file in the mapper’s directory on the local file system and then passed to the partition function which will then write the output in a partition file inside the mapper’s directory on the local file system.
   
2. **Partition**: The output of the Map function (as mentioned in the mapper above) needs to be partitioned into a set of smaller partitions.
     * The partitioning function ensures that:
         All key-value pairs belonging to the same key are sent to the same partition file.
         Distribute the different keys equally (or almost equally) among each of the partitions. This can be done using very simple and reasonable partition functions ( such as key % num_reducers)

      * Each partition file is picked up by a specific reducer during shuffling and sorting.
      * If there are M mappers and R reducers, each mapper should have R file partitions. This means that there will be M*R partitions in total.
    
### Shuffle sort and Reduce (invlked by reducer):
1. Sort the intermediate key-value pairs by key and group the values that belong to the same key base on the key value.

2. The reducer will receive the intermediate key-value pairs from the mapper, perform the shuffle & sort function as mentioned, and produce a set of final key-value pairs as output.
  * Input to the reduce function:
      Key: Centroid id
      Value: List of all the data points which belong to this centroid id (this information is available after shuffle and sorting)
      Other necessary information

  * Output of the reduce function:
      Key: Centroid Id
      Value: Updated Centroid
    
  The output of each Reduce function is written to a file in the reducer’s directory on the local file system (centroid. txt).

### Centroid Compilation (invoked by master):
* The master needs to parse the output generated by all the reducers to compile the final list of (K) centroids and store them in a single file. This list of centroids is considered as input for the next iteration.

### gRPC Communication
  The gRPC communication between the three processes for each iteration looks something like this:
  
    Master ⇔ Mapper (master sends necessary parameters to mapper, mapper performs map & partition)
    Master ⇔ Reducer (after all mappers have returned to master successfully, master invokes reducers with the necessary parameters)
    Reducer ⇔ Mapper (after invocation, reducers communicates with the mapper to get the input before the shuffle, sort, and reduce step)
    Master ⇔ Reducer (after all reducers have returned to master successfully, master contacts the reducers to read the output datafiles)
  
For any other requirements refer [Documentation](https://github.com/Talkative-Banana/MapReduce/logo/Document.html)

## Getting Started
<!-- GETTING-STARTED -->
To get a local copy up and running follow these simple steps.

### Prerequisites
<!-- PREREQUISITES -->
* Basic understanding of Python (Tutorials: [English](https://youtu.be/_uQrJ0TkZlc) | [Hindi](https://youtu.be/gfDE2a7MKjA))
* Python installed on your computer ([Download from Here](https://www.python.org/downloads/))
* GitHub Account ([Sign Up](https://github.com/))
* gRPC ([Download from here](https://grpc.io/))

### Installation
<!-- INSTALLATION -->
* Clone the repo

        git clone https://github.com/Talkative-Banana/MapReduce.git
        chmmod +x script.sh # (For linux users)
        run the sh file with asked parameters denoting # mappers, # reducers.

For MacOS or Windows you need to either run each mapper and reducer manually or change the build file to run all of them locally.
## Deployment
<!-- DEPLOYMENT -->
### Remote Deployment

* Set up google cloud or docker containers and update the firewall settings to accept and send remote request.

* **mapper.py**, **master.py** and **reducer.py** have a static dictionary storing IP-address and IP port which needs to be manually updated for gRPC communication. In case of local deployment all of the ip address are set to localhost.

* Grant permission to sh file and run it with required parameters.

### Local Deployment

* Simply grant permission to sh file and run it with required parameters.
## Roadmap
<!-- ROADMAP -->
- Clone the repo and open it in suitable IDE for complete project source code. You can also fix the issues and hence contribute.


## Contributing
<!-- CONTRIBUTING -->
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request
## Contact
<!-- CONTACT -->
Email ID - lakshay21059@iiitd.ac.in
## Acknowledgements
<!-- ACKNOWLEDGEMENTS -->
Lakshay Bansal lakshay21059@iiitd.ac.in


