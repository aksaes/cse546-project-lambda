import os

mapFile = open("mapping.txt","r")
lines = mapFile.readlines()

mapping  = {}
for line in lines:
    key = line.split(':')[0].split('.')[0]
    value = line.split(':')[1].strip()
    mapping[key] = value

directory = "output/"
all_files = os.listdir(directory)

count = 0

for file in all_files:
    key = file.split('.')[0]
    dataFile = open(directory + file)
    line = dataFile.readline()
    data = ",".join(line.replace(" ","").split(',')[1:])
    if mapping[key] != data:
        print("this file has an error: " + file)
    else:
        count += 1

print("final count of verified files " + str(count))



