#!/bin/bash
M=$1
R=$2
K=$3
I=$4
directory_m="Mapper"
directory_r="Reducer"
refm=8500
refr=9500
for((i=1; i<=$M; i++))
do
	folder_name_m="$directory_m/M$i"
	rm -rf "$folder_name_m" 
	mkdir "$folder_name_m"
	echo "M$i created"
	cp "$directory_m/mapper.py" "$directory_m/M$i/"
	cp "$directory_m/message.proto" "$directory_m/M$i/"
	cp "$directory_m/message_pb2.py" "$directory_m/M$i/"
	cp "$directory_m/message_pb2_grpc.py" "$directory_m/M$i/"
	rm -rf "$folder_name_m/Partition" 
	mkdir "$folder_name_m/Partition"
	port=$((refm+i))
	gnome-terminal --working-directory=$(pwd)/Mapper/M$i --wait --title="Mapper $i" -- python mapper.py $i localhost $port &
done

for((i=1; i<=$R; i++))
do
	folder_name_r="$directory_r/R$i"
	rm -rf "$folder_name_r"
	mkdir "$folder_name_r"
	echo "R$i created"

	cp "$directory_r/reducer.py" "$directory_r/R$i/"
	cp "$directory_r/message.proto" "$directory_r/R$i/"
	cp "$directory_r/message_pb2.py" "$directory_r/R$i/"
	cp "$directory_r/message_pb2_grpc.py" "$directory_r/R$i/"

	mkdir "$folder_name_r/Output"
	port=$((refr+i))
	gnome-terminal --working-directory=$(pwd)/Reducer/R$i --wait --title="Reducer $i" -- python reducer.py $i localhost $port &
done
gnome-terminal --working-directory=$(pwd)/Master/ --wait --title= "Master" -- python master.py $M $R $K $I localhost 8500 &

