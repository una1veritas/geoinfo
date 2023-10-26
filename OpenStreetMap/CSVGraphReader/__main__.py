import sys





### main 
if len(sys.argv) < 2 :
    print("Supply graph .csv file name.")
    exit(1)

filename = sys.argv[1]
print("open file " + filename + ".")

geograph = list()
with open(filename) as csvf:
    for line in csvf:
        line = line.strip()
        row = line.split(",")
        gpid = row[0]
        gpposition = (row[1], row[2])
        gpadjacents = row[3:]
        geopt = (gpid, gpposition, gpadjacents)
        geograph.append(geopt)
        print(geopt)

print("geograph has "+str(len(geograph))+ " points.")
print("finished.")