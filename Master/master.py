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


class Master():
    # Mapper's port number => 8500 + id
    # Reducer's port number => 9500 + id
    def savetodump(self, line):
        with open("dump.txt", '+a') as f:
            f.write(line+"\n")
        return

    def Entries(self):
        num = 0
        with open("../Input/input.txt", 'r') as f:
            for entry in f: num += 1
        return num
    
    def Chunks(self):
        div = self.entries // self.M
        chunks = {}
        for i in range(self.M):
            if i == (self.M-1):
                chunks[i + 1] = [i * div, self.entries - 1]
            else:
                chunks[i + 1] = [i * div, ((i + 1) * div) - 1]
        return chunks
    
    def MessageMappers(self, mapper, chunk, cords):
        float_list_list = message_pb2.FloatListList()
        for cord in cords:
            float_list = message_pb2.FloatList()
            float_list.values.extend(cord)
            float_list_list.lists.append(float_list)
        
        channel = grpc.insecure_channel("localhost" + ":" + str(8500 + mapper))
        stub = message_pb2_grpc.MessageStub(channel)
        self.ack[mapper] = False
        try:
            response = stub.ServeMapper(message_pb2.RequestMapper(indexes=chunk, cords=float_list_list, reducers=self.R))
            if(response.response == 0): 
                self.ack[mapper] = True
                return
            else: # Failure
                print(f"Received failure from {mapper} Retrying...")
                self.savetodump(f"Received failure from {mapper} Retrying...")
                time.sleep(1) # Wait to prevent stack overflow
                return self.MessageMappers(mapper, chunk, cords) # Assign the task again to Mapper
        
        except:
                print(f"Could not reach mapper {mapper}")
                self.savetodump(f"Could not reach mapper {mapper}")
                print("Retrying...")
                time.sleep(1) # Wait to prevent stack overflow
                return self.MessageMappers(mapper, chunk, cords) # Assign the task again to Mapper

    def setdiff(self, vec1, vec2):
        for i in range(len(vec1)):
            points1 = vec1[i]
            points2 = vec2[i]
            if (abs(points1[0] - points2[0]) > 0.001) and (abs(points1[1] - points2[1]) > 0.001): return 1
        return 0

    def MessageReducers(self, reducer, M):
        channel = grpc.insecure_channel("localhost" + ":" + str(9500 + reducer))
        stub = message_pb2_grpc.MessageStub(channel)
        self.ack[reducer] = False
        try:
            response = stub.ServeReducer(message_pb2.RequestReducer(mappers=M))
            if(response.response == 0):
                self.ack[reducer] = True
                temp = response.entries.lists 
                cords = []
                for cord in temp: cords.append(list(cord.values))
                for cord in range(len(cords)): self.cords[int(cords[cord][0])] = [float(cords[cord][1]), float(cords[cord][2])]  
                return
            else: # Failure
                print(f"Received failure from {reducer} Retrying...")
                self.savetodump(f"Received failure from {reducer} Retrying...")
                time.sleep(1) # Wait to prevent stack overflow
                return self.MessageReducers(reducer, M) # Assign the task again to Mapper
        except:
                print(f"Could not reach mapper {reducer}")
                self.savetodump(f"Could not reach mapper {reducer}")
                print("Retrying...")
                time.sleep(1) # Wait to prevent stack overflow
                return self.MessageReducers(reducer, M) # Assign the task again to Mapper
    
    def ServeMapper(self, request, context):
        return message_pb2.ResponseMapper(response=self.M)

    def Mappers(self, start, end):
        for mapper in range(start, end + 1):
            thread = threading.Thread(target=self.MessageMappers, args=(mapper, self.chunks[mapper], self.cords))
            thread.start()
        return 0
    
    def allacks(self, count):
        for key in range(1, count + 1):
            if (self.ack[key] == False): return False
        return True
    
    def Reducer(self, start, end):
        for reducer in range(start, end + 1):
            thread = threading.Thread(target=self.MessageReducers, args=(reducer, self.M))
            thread.start()
        return 0
    
    def pickK(self):
        with open("../Input/input.txt", 'r') as f:
            lst = [entry[:-1].split(',') for entry in f if (entry != "") and (entry != "\n")]
        for i in range(len(lst)): lst[i] = [float(x) for x in lst[i]]
        random_numbers = random.sample(range(0, len(lst)), self.K)
        res = []
        for num in random_numbers: res.append(lst[num])
        return res

    def __init__(self, mappers, reducers, centroids, iterations, ipaddr, port):
        self.port = port
        self.ip = ipaddr
        self.M = mappers
        self.R = reducers
        self.K = centroids
        self.I = iterations
        self.ack = {}
        for i in range(1, max(self.M, self.R) + 1): self.ack[i] = False
        # Pick any K points
        self.cords = self.pickK()
        self.prev = [x for x in self.cords]
        self.entries = self.Entries()
        self.chunks = self.Chunks()
        self.diff = 1

        print("Initail cords of centroid")
        print(self.cords)
        inp = input("Press enter to start")
        for iter in range(1, self.I + 1):
            print(f"Starting iteration {iter}")
            self.savetodump(f"Starting iteration {iter}")
            print("Mapping...")
            self.savetodump("Mapping...")
            self.Mappers(1, self.M)
            while(not self.allacks(self.M)): continue
            for key in self.ack: self.ack[key] = False
            print("Reducing...")
            self.savetodump("Reducing...")
            self.Reducer(1, self.R) # Inform Reducers about no. of Mappers
            while(not self.allacks(self.R)): continue
            self.diff = self.setdiff(self.prev, self.cords) # Set 0 to break
            if (self.diff == 0):
                print(f"Converged on iteration {iter}")
                self.savetodump(f"Converged on iteration {iter}")
                break
            for key in self.ack: self.ack[key] = False
            self.prev = [x for x in self.cords]

        # for iter in range(1, self.I + 1):
        #     print(f"1) Start iteration {iter}")
        #     print(f"2) Exit")
        #     inp = int(input())
        #     if(inp == 1): self.Mappers(1, self.M)
        #     elif(inp == 2): exit(0)
            
        #     while(not self.allacks(self.M)): continue
        #     for key in self.ack: self.ack[key] = False
        #     print("SUCCESS received from all Mappers!")
        #     print(f"1) Reduce")
        #     print(f"2) Exit")
        #     inp = int(input())
        #     if(inp == 1): self.Reducer(1, self.R) # Inform Reducers about no. of Mappers
        #     elif(inp == 2): exit(0)

        #     while(not self.allacks(self.R)): continue
        #     if (self.diff == 0):
        #         print(f"Converged on iteration {iter}")
        #         break
        #     for key in self.ack: self.ack[key] = False

        print("New Cords of centroids:")
        print(self.cords)
        with open("../centroids.txt", 'w') as f: json.dump(self.cords, f)
        print("Press Enter to exit")
        inp = input()

def serve(master, ip_addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServicer_to_server(master, server)
    server.add_insecure_port(ip_addr + ":" + str(port))
    server.start()
    server.wait_for_termination()
    return

def main():
    if(len(sys.argv) != 7):
        print("Invalid arguments (master.py [mappers] [reducers] [centroids] [iterations] [ipaddr] [port])")
        return 1
    mappers, reducers, centroids, iterations, ipaddr, port = sys.argv[1:7]
    master = None
    if(os.path.exists(f"../Input/input.txt")):
        master = Master(int(mappers), int(reducers), int(centroids), int(iterations), ipaddr, int(port))
    else:
        print("Input file doesnot exist!")
        return
    
    # [::]: port
    serve(master, ipaddr, port)
    return 0


if __name__ == '__main__': main()
