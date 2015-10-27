'''
Takes a csv as an input and works through the compounds to extract the number of C, H, and O 
present. Then calculates the ratios of H:C and O:C and plots them. 
'''
import sys
import os
from extractNeededElementalData import extractNeededElementalData
from processElementalData import processElementalData
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import six
import dateutil
import itertools

usage_mesg = 'VanKrevelen.py <csv file(s)>'

# Checks if files are available.
filename_csv = sys.argv[1]
if( not os.access(filename_csv,os.R_OK) ):
    print "%s is not accessible."%filename_csv
    print usage_mesg
    sys.exit(1)

# Checks to see if you want to test pos and neg or just one or the other
#***** see if this is needed ****
if(len(sys.argv) == 2 ):
    filename_csv = sys.argv[1]
    elementalList = extractNeededElementalData(filename_csv)
    ratiosList = processElementalData(elementalList)
    #Note, at this point the elementalList and ratiosList will not be aligned
    #because the processing of the ratios removes lines where not all 3 elements
    #were present (rare occurance but may happen)

# Creates the actual graph itself.	

print "Displaying plot"
	
# Graphs the data provided and labels axes

area = 10.0

fig = plt.figure()
fig.suptitle('Van Krevelen Diagram - Nitrogen Check', fontsize=14, fontweight='bold')
ax = fig.add_subplot(111)
fig.subplots_adjust(top=0.85)

ax.set_xlabel('O:C Ratio')
ax.set_ylabel('H:C Ratio')

# Creates a list for plotting purposes where two elements are lists of compounds with N and without respectively
listByN = [[],[]]
withN = None
withoutN = None
for i in range(len(ratiosList[2])):
    if ratiosList[2][i]:
        listByN[0].append([ratiosList[1][i],ratiosList[0][i], 'r', '^'])
    else:
        listByN[1].append([ratiosList[1][i],ratiosList[0][i], 'b', 'o'])

counter = 0
for i in listByN:
    for j in i:
        if counter == 0:
           withN = plt.scatter(j[0], j[1], 15.0, j[2], j[3], alpha = .25)
        else:
            withoutN = plt.scatter(j[0], j[1], 15.0, j[2], j[3], alpha = .25)
    counter += 1


plt.legend((withN, withoutN), ('Does have N', 'Does not have N'), scatterpoints = 1, loc='lower left', ncol=1,fontsize = 9)
plt.show()

print("done")
