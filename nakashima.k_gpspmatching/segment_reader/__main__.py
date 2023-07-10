import sys

trajectoryfile_name = '2019-10-05_114328.csv'
segmentsfile_name = 'segments_data/2023-05-06_221836_segment.csv'
edgefile_name = 'road_data/RoadNetwork_Fukuoka_Edge.csv'
nodefile_name = 'road_data/RoadNetwork_Node_Fukuoka.csv'

# with open(trajectoryfile_name, 'r') as file:
#     for a_line in file:
#         items = a_line.strip().split(',')
#         print(items)

table = list()    
with open(segmentsfile_name, 'r') as file:
    isheadline = True
    for a_line in file:
        items = a_line.strip().split(',')
        if isheadline :
            headline = items
            isheadline = False
        else:
            table.append(list())
            for each in items:
                try:
                    val = eval(each)
                    if isinstance(val,list):
                        val = each.strip()[1:-2].split(' ')
                except:
                    val = each
                table[-1].append(val)

print(headline)
for e in table:
    print(e)
    
# with open(nodefile_name, 'r') as file:
#     for a_line in file:
#         print(a_line)
#
# with open(edgefile_name, mode='r', encoding='utf-8') as file:
#     for a_line in file:
#         print(a_line)
