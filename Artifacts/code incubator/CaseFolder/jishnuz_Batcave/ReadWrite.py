import sys
import fileinput
import re


# Buggy code to edit the blockMeshDict with the updated coord

for i, line in enumerate(fileinput.input('BlockNesh', inplace=1)):
    
    old = 'jishnu'
    new = 'superman'
    sys.stdout.write(line.replace(old, new))  # replace 'old' with 'new'
    
    # if i == 7: sys.stdout.write('\n')  # write a blank line after the 5th line 
    # if i == 3: print(line) 
    
    # bug 
    if i == 20:
        newPoint = (0,0,0)
        newLine = re.sub(r'\(.*?\)', newPoint, line)
        sys.stdout.write(line.replace(line, newLine))

    


