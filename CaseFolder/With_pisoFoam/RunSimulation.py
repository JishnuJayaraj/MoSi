import fileinput
import os, re, sys
import numpy as np
from pathlib import Path

#Path Definitions
Modpath     = '/home/aju/Seminar/With_pisoFoam'
Refpath     = '/home/aju/Seminar/With_pisoFoam/Reference'
Itpath      = '/home/aju/Seminar/With_pisoFoam/Iteration_'
NSpath      = '/home/aju/Seminar/With_pisoFoam/Reference/NS'
OSpath      = '/home/aju/Seminar/With_pisoFoam/Reference/OS'

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
       
    # Calculation of new boundary Coordinates 
    # viscosity
    nu = .01
    # weight = 1/w
    weight = 0.00001

    word = []
    with open (Itpath+str(i+1)+'/OS/BoundaryResults.txt') as file:
    #lines = file.readlines()
    	for line in file:
        #line = line.split(' ')
        	word.append(re.findall(r'[^(())\t\n ]+',line))
        
    #print(word)
    del word[0]


    flat_value = []
    for sublist in word:
    	for item in sublist:
        	flat_value.append(item)
        
    values = list(map(float,flat_value))

    pos = []
    for count, item in enumerate(values):
    	if count == 0 and count == 1:
        	pos.append(item)
        
    allitems = np.array(values)

    indicespos = [0,1,2]
    indicesU = [3,4,5]
    indicesPadj = [6]
    indicesUadj = [7,8,9]
    indicesGradu = [10,11,12,13,14,15,16,17,18]
    indicesGraduAdj = [19,20,21,22,23,24,25,26,27]
    indicesNormal = [28,29,30]

    lineSize = 31
    nFaces = 40
#print(list(allitems[indexes]))

#indexes = list(np.asarray(indexes) + 31)
#print(indexes)
#print(list(allitems[indexes]))

    global_Corrector = np.array([])
    global_pos = np.array([])

    for i in range(0,nFaces):
    #print(list(allitems[indicespos = [0,1,2]]))
    #indexes = list(np.asarray(indexes) + 31)
    	pos = np.array(list(allitems[indicespos]))
    	indicespos = list(np.asarray(indicespos) + lineSize)
    
    	U = np.array(list(allitems[indicesU]))
    	indicesU = list(np.asarray(indicesU) + lineSize)
    
    	pAdj = np.array(list(allitems[indicesPadj]))
    	indicesPadj = list(np.asarray(indicesPadj) + lineSize)
    
    	uAdj = np.array(list(allitems[indicesUadj]))
    	indicesUadj = list(np.asarray(indicesUadj) + lineSize)
    
    	gradU = np.array(list(allitems[indicesGradu]))
    	indicesGradu = list(np.asarray(indicesGradu) + lineSize)
    
    	gradUadj = np.array(list(allitems[indicesGraduAdj]))
    	indicesGraduAdj = list(np.asarray(indicesGraduAdj) + lineSize)
    
    	normal = np.array(list(allitems[indicesNormal]))
    	indicesNormal = list(np.asarray(indicesNormal) + lineSize)
    
    	u_Inner_uAdj = np.inner(U.reshape(1,-1).T, uAdj.reshape(1,-1).T)
    	pAdj_Matrix = np.identity(3)*pAdj
    	sym_GraduAdj = (gradUadj.reshape(3,3) + gradUadj.reshape(3,3).T)*nu
    
    	s = (u_Inner_uAdj + pAdj_Matrix + sym_GraduAdj).dot(normal.reshape(1,-1).T)
    	corrector = weight*(gradU.reshape(3,3).T).dot(s)
    
    
    	global_Corrector=np.append(global_Corrector,corrector)
    	global_pos = np.append(global_pos,pos)
    #print(np.inner(U,uAdj.T))
    #print(U)
    
    updated_global_pos = global_pos - global_Corrector
    print(updated_global_pos)



  
        
        
        
        
        
        
        
        
        
