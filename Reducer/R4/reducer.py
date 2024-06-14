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

class Reducer():
    # Mapper's port number  => 8500 + id
    # Reducer's port number => 9500 + id
    def savetodump(self, line):
        with open("dump.txt", '+a') as f:
            f.write(line+"\n")
        return

    def Entries(self, lst):
        temp = []
        for cord in lst.lists: temp.append(list(cord.values))
        return temp
    
    def updatedcentroid(self, Dict):
        res = {}
        for key in Dict:
            l = max(1, len(Dict[key]))
            x, y = 0, 0
            for cords in Dict[key]:
                x += cords[0]
                y += cords[1]
            res[key] = [x / l, y / l]
        return res

    def saveresult(self, newcentroids):
        print("Saving results...")
        self.savetodump("Saving results...")
        with open(f"Output/R{self.id}.txt", 'w') as f:
            for key in newcentroids:
                f.write(str(key) + "," + str(newcentroids[key][0]) + "," + str(newcentroids[key][1]))
        flag = random.uniform(0, 1)
        return 1 if (flag >= 0.5) else 0 # Returns failure in case of flag value >= 0.5
    
    def ProcessEntries(self):
        for mapper in range(1, self.M + 1):
            channel = grpc.insecure_channel("localhost" + ":" + str(8500 + mapper))
            stub = message_pb2_grpc.MessageStub(channel)
            try:
                response = stub.ServeReducer(message_pb2.RequestReducer(mappers=self.id))
                if(response.response == 0):
                    self.entries.extend(self.Entries(response.entries)) 
                else: # Failure
                    print(f"Received failure from {mapper} Retrying...")
                    self.savetodump(f"Received failure from {mapper} Retrying...")
                    time.sleep(1) # Wait to prevent stack overflow
                    return self.ProcessEntries() # Ask agian from Mapper
            except:
                    print(f"Could not reach mapper {mapper}")
                    print("Retrying...")
                    self.savetodump(f"Could not reach mapper {mapper}")
                    time.sleep(1) # Wait to prevent stack overflow
                    return self.ProcessEntries() # Ask agian from Mapper
        # Have all the entries
        for entry in self.entries: entry[0] = int(entry[0])
        # Sorting on the basis of key value
        sorted_list = sorted(self.entries, key=lambda x: x[0])
        Dict = {}
        for entry in sorted_list:
            key = entry[0]
            if key not in Dict: Dict[key] = [[entry[1], entry[2]]]
            else: Dict[key].append([entry[1], entry[2]])
        newcentroids = self.updatedcentroid(Dict)
        return self.saveresult(newcentroids)
    
    def readfiles(self):
        lst = []
        with open(f"Output/R{self.id}.txt", 'r') as f:
            lst = [line[:-1].split(',') for line in f if (line != "") and (line != "\n")]

        for i in range(len(lst)): lst[i] = [float(x) for x in lst[i]]
        return lst


    def getEntries(self):
        float_list_list = message_pb2.FloatListList()
        lst = self.readfiles()
        for cord in lst:
            float_list = message_pb2.FloatList()
            float_list.values.extend(cord)
            float_list_list.lists.append(float_list)
        return float_list_list

    def ServeReducer(self, request, context):
        # return response based on flag value (failure)
        self.M = request.mappers
        print("Count of Mappers received: ", self.M)
        self.savetodump(f"Count of Mappers received: {self.M}")
        print("Calculating new centroids")
        return message_pb2.ResponseReducer(response=self.ProcessEntries(), entries=self.getEntries())
    
    def ServeMapper(self, request, context):
        return message_pb2.ResponseMapper(response=0)

    def __init__(self, id, ipaddr, port):
        self.id = id
        self.ip = ipaddr
        self.port = port
        self.entries = []
        print("Listening for Master")

def serve(reducer, ip_addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServicer_to_server(reducer, server)
    server.add_insecure_port(ip_addr + ":" + str(port))
    server.start()
    server.wait_for_termination()
    return

def main():
    if(len(sys.argv) != 4):
        print("Invalid arguments (reducer.py [id] [ipaddr] [port])")
        return 1
    id, ipaddr, port = sys.argv[1:4]
    reducer = Reducer(int(id), ipaddr, int(port))
    
    # [::]: port
    serve(reducer, ipaddr, port)
    return 0

if __name__ == '__main__': main()