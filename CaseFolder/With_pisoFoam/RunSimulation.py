import fileinput
import os, re, sys
from pathlib import Path

#Path Definitions
Modpath     = '/home/prabhu/MoSi/CaseFolder/With_pisoFoam'
Refpath     = '/home/prabhu/MoSi/CaseFolder/With_pisoFoam/Reference'
Itpath      = '/home/prabhu/MoSi/CaseFolder/With_pisoFoam/Iteration_'
NSpath      = '/home/prabhu/MoSi/CaseFolder/With_pisoFoam/Reference/NS'
OSpath      = '/home/prabhu/MoSi/CaseFolder/With_pisoFoam/Reference/OS'

DragInitialX = 1
for i in range(1):
    if Path(Itpath+str(i+1)).exists() == False:
        os.mkdir('Iteration_'+str(i+1))
    os.system('cp -r '+Refpath+'/* '+Itpath+str(i+1))
    os.chdir(Itpath+str(i+1)+'/NS')

    #ToDo: 'Edit Block mesh dict'
    blockMeshDict = os.path.isfile(NSpath+'/system/blockMeshDict')
    if blockMeshDict:
        os.system('blockMesh')
        os.system('checkMesh')
        #ToDo: if checkmesh last but second line says mesh: ok, then execute next line
        os.system('pisoFoam')
    else:
        print('Block Mesh Dictionary is not available')
        sys.exit(1)
    
    os.system('cp '+Itpath+str(i+1)+'/NS/1.5/p '+Itpath+str(i+1)+'/OS/0')
    os.system('cp '+Itpath+str(i+1)+'/NS/1.5/U '+Itpath+str(i+1)+'/OS/0')
    
    dragForceFile   = open(Itpath+str(i+1)+'/NS/postProcessing/forces/0/forces.dat','r')
    lastline        = dragForceFile.readlines()
    lastline        = lastline[-1]
    term = '[^(())\t\n ]+'
    splitDoubleBraces = re.findall(term, lastline)
    DragForceX      = float(splitDoubleBraces[1])+float(splitDoubleBraces[4])
    
    f = fileinput.FileInput(Itpath+str(i+1)+'/OS/0/UAdj', inplace=True)
    for line in f:
        #findText = 'value           uniform (1 0 0);'
        #replaceText = 'value           uniform (100 0 0);'
        #print(re.sub(findText,replaceText,line))
        findText = 'value           uniform ('+str(DragInitialX)+' 0 0);'
        replaceText = 'value           uniform ('+str(DragForceX)+' 0 0);'
        print(line.replace(findText, replaceText))
    DragInitialX = DragForceX
    f.close()
    
    os.chdir(Itpath+str(i+1)+'/OS')
    os.system('cp '+Itpath+str(i+1)+'/NS/system/blockMeshDict '+Itpath+str(i+1)+'/OS/system/') 
    os.system('blockMesh')
    os.system('checkMesh')
    os.system('pisomosiFoam')
        
        
        
        
        
        
        
        
        
        
        