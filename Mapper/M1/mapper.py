import os
import sys
import grpc
import time
import json
import random
import logging
import threading
import message_pb2
import message_pb2_grpc
from concurrent import futures


class Mapper():
    # Mapper's port number => 8500 + id
    # Reducer's port number => 9500 + id
    def savetodump(self, line):
        with open("dump.txt", '+a') as f:
            f.write(line+"\n")
        return

    def Entries(self):
        lst = []
        with open("../../Input/input.txt", 'r') as f:
            lst = [line[:-1].split(',') for line in f]

        for i in range(len(lst)): lst[i] = [float(x) for x in lst[i]]
        return lst[self.inputsplit[0]: self.inputsplit[1] + 1]
    
    def ServeMapper(self, request, context):
        # return response based on flag value (failure) to master
        self.R = request.reducers
        self.inputsplit = request.indexes
        temp = request.cords.lists
        print("Split received: ", self.inputsplit)
        self.savetodump(f"Split received: {self.inputsplit}")
        self.centroid_cords = []
        for cord in temp: self.centroid_cords.append(list(cord.values))
        return message_pb2.ResponseMapper(response=self.ProcessEntries())

    def readfiles(self, id):
        lst = []
        with open(f"Partition/partition_{id}.txt", 'r') as f:
            lst = [line[:-1].split(',') for line in f if (line != "") and (line != "\n")]
        for i in range(len(lst)): lst[i] = [float(x) for x in lst[i]]
        return lst

    def ServeReducer(self, request, context):
        # returns response to reducer
        float_list_list = message_pb2.FloatListList()
        id = request.mappers
        lst = self.readfiles(id)
        for cord in lst:
            float_list = message_pb2.FloatList()
            float_list.values.extend(cord)
            float_list_list.lists.append(float_list)
        return message_pb2.ResponseReducer(response=0, entries=float_list_list) # Assign the task again to Mapper

    def Partition(self, lst):
        # lst is list containing key value pairs
        bucket = {}
        for keyval in lst:
            hash = (int(keyval[0]) % self.R) + 1
            if hash not in bucket: bucket[hash] = [keyval]
            else: bucket[hash].append(keyval)

        for partition in range(1, self.R + 1):
            fname = f"Partition/partition_{partition}.txt"
            with open(fname, 'w') as f:
                if partition not in bucket: continue
                for entry in bucket[partition]: f.write(str(entry[0]) + "," + str(entry[1][0]) + "," + str(entry[1][1]) + "\n")
        flag = random.uniform(0, 1)
        return 1 if (flag >= 0.5) else 0 # Returns failure in case of flag value >= 0.5

    def minmdist(self, point):
        mdist = 1e9
        idx = -1
        centroidcords = self.centroid_cords
        for i in range(len(centroidcords)):
            cord = centroidcords[i]
            dist = ((cord[0] - point[0]) ** 2) + ((cord[1] - point[1]) ** 2)
            if dist < mdist:
                mdist = dist
                idx = i
        return idx

    def Map(self):
        # Takes prevcord and entries as input
        points = self.entries
        result = []
        for point in points:
            key = self.minmdist(point)
            value = point
            result.append([key, value])
        return self.Partition(result)

    def ProcessEntries(self):
        self.entries = self.Entries()
        print("Entries read completed")
        self.savetodump("Entries read completed")
        return self.Map()

    def __init__(self, id, ipaddr, port):
        self.id = id
        self.ip = ipaddr
        self.port = port
        self.inputsplit = [-1, -1]
        self.entries = []
        print("Listening for Master")

def serve(mapper, ip_addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServicer_to_server(mapper, server)
    server.add_insecure_port(ip_addr + ":" + str(port))
    server.start()
    server.wait_for_termination()
    return

def main():
    if(len(sys.argv) != 4):
        print("Invalid arguments (mapper.py [id] [ipaddr] [port])")
        return 1
    id, ipaddr, port = sys.argv[1:4]
    mapper = None
    if(os.path.exists(f"../../Input/input.txt")):
        mapper = Mapper(int(id), ipaddr, int(port))
    else:
        print("Input file doesnot exist!")
        return
    
    # [::]: port
    serve(mapper, ipaddr, port)
    return 0

if __name__ == '__main__': main()
