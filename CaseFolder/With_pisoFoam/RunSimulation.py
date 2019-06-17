# cd /opt/pycharm-*/bin
# ./pycharm.sh

import numpy as np
from pathlib import Path
import os, re, sys, math, fileinput

#Path Definitions
Modpath     = '/home/prabhu/PycharmProjects/MoSiSeminar'
Refpath     = Modpath+'/Reference'
Itpath      = Modpath+'/Iteration_'
NSpath      = Refpath+'/NS'
OSpath      = Refpath+'/OS'

DragInitialX = 1
for i in range(2):
	if Path(Itpath+str(i+1)).exists() == False:
		os.mkdir('Iteration_'+str(i+1))
		print('Iteration_'+str(i+1)+'Directory Created')
	os.system('cp -r '+Refpath+'/* '+Itpath+str(i+1))
	os.chdir(Itpath+str(i+1)+'/NS')

	blockMeshDict = os.path.isfile(NSpath+'/system/blockMeshDict')
	if blockMeshDict:
		if i != 0:
			index = 0
			flag = False
			for vertex in range(30):
				f = open(Itpath+str(i+1)+"/NS/system/blockMeshDict", "r")
				for line in f:
					findText = '//Vertex_' + str(vertex + 1) + '*'
					if findText in line:
						replaceline = line
						flag = True
				f.close()

				if flag == True:
					s = open(Itpath+str(i+1)+"/NS/system/blockMeshDict").read()
					StripVertex = ' '.join(map(str, Vertices[index]))
					s = s.replace(replaceline, '(' + StripVertex + ') ' + findText + '\n')
					f = open(Itpath+str(i+1)+"/NS/system/blockMeshDict", 'w')
					f.write(s)
					f.close()
					index = index + 1
					flag = False

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
		findText = 'value           uniform ('+str(DragInitialX)+' 0 0);'
		replaceText = 'value           uniform ('+str(DragForceX)+' 0 0);'
		print(line.replace(findText, replaceText), end='')
	DragInitialX = DragForceX
	f.close()

	os.chdir(Itpath+str(i+1)+'/OS')
	os.system('cp '+Itpath+str(i+1)+'/NS/system/blockMeshDict '+Itpath+str(i+1)+'/OS/system/')
	os.system('blockMesh')
	os.system('checkMesh')
	os.system('pisomosiFoam')

	# Calculation of new boundary Coordinates
	nu = .01 # viscosity
	weight = 0.00001 # weight = 1/w


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
	outerLayer_t = .1
	#print(list(allitems[indexes]))
	#indexes = list(np.asarray(indexes) + 31)
	#print(indexes)
	#print(list(allitems[indexes]))

	global_Corrector = np.array([])
	global_pos = np.array([])

	for k in range(0,nFaces):
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
		corrector = weight*gradU.reshape(3,3).T.dot(s)

		global_Corrector=np.append(global_Corrector,corrector)
		global_pos = np.append(global_pos,pos)
	#print(np.inner(U,uAdj.T))
	#print(U)

	updated_global_pos = global_pos - global_Corrector
	facepoint_0 = np.array([updated_global_pos[0],updated_global_pos[1],0])
	facepoint_1 = np.array([updated_global_pos[1*3],updated_global_pos[1*3+1],0])
	facepoint_9 = np.array([updated_global_pos[9*3],updated_global_pos[9*3+1],0])
	facepoint_10 = np.array([updated_global_pos[10*3],updated_global_pos[10*3+1],0])
	facepoint_19 = np.array([updated_global_pos[19*3],updated_global_pos[19*3+1],0])
	facepoint_20 = np.array([updated_global_pos[20*3],updated_global_pos[20*3+1],0])
	facepoint_29 = np.array([updated_global_pos[29*3],updated_global_pos[29*3+1],0])
	facepoint_30 = np.array([updated_global_pos[30*3],updated_global_pos[30*3+1],0])
	facepoint_38 = np.array([updated_global_pos[38*3],updated_global_pos[38*3+1],0])
	facepoint_39 = np.array([updated_global_pos[39*3],updated_global_pos[39*3+1],0])

	#New coordinates of Vertices

	x_Vertex_4 = (facepoint_1[0]-facepoint_0[0])/(facepoint_1[1]-facepoint_0[1])*(-facepoint_0[1]) + facepoint_0[0]
	Vertex_4 = np.array([x_Vertex_4,0,0])

	x_Vertex_10 = (facepoint_38[0]-facepoint_39[0])/(facepoint_38[1]-facepoint_39[1])*(-facepoint_39[1]) + facepoint_39[0]
	Vertex_10 = np.array([x_Vertex_10,0,0])
	Vertices = np.array([Vertex_4,Vertex_10])

	Vertex_5 = (facepoint_9 + facepoint_10)/2
	Vertices = np.vstack([Vertices,Vertex_5])

	Vertex_6 = (facepoint_19 + facepoint_20)/2
	Vertices = np.vstack([Vertices,Vertex_6])

	Vertex_8 = (facepoint_29 + facepoint_30)/2
	Vertices = np.vstack([Vertices,Vertex_8])

	# Vertices of outer layer
	Vertex_1 = np.array([Vertex_4[0]-outerLayer_t,0,0])
	Vertices = np.vstack([Vertices,Vertex_1])

	x_Vertex_2 = Vertex_5[0]*(1+outerLayer_t/math.sqrt((Vertex_5[1])**2 +(Vertex_5[0])**2 ))
	Vertex_2 = np.array([x_Vertex_2,Vertex_5[1]/Vertex_5[0]*x_Vertex_2,0])
	Vertices = np.vstack([Vertices,Vertex_2])

	x_Vertex_9 = Vertex_8[0]*(1+outerLayer_t/math.sqrt((Vertex_8[1])**2 +(Vertex_8[0])**2 ))
	Vertex_9 = np.array([x_Vertex_9,Vertex_8[1]/Vertex_8[0]*x_Vertex_9,0])
	Vertices = np.vstack([Vertices,Vertex_9])

	if Vertex_6[0]!=0:
			x_Vertex_7 = Vertex_6[0]*(1+outerLayer_t/math.sqrt((Vertex_6[1])**2 +(Vertex_6[0])**2 ))
			Vertex_7 = np.array([x_Vertex_7,Vertex_6[1]/Vertex_6[0]*x_Vertex_7,0])
	else:
			Vertex_7 = np.array([0,Vertex_6[1]+outerLayer_t,0])

	Vertices = np.vstack([Vertices,Vertex_7])

	Vertex_11= np.array([Vertex_10[0]+outerLayer_t,0,0])
	Vertices = np.vstack([Vertices,Vertex_11])

	zOffsetMatrix = np.array([[0,0,0.1],[0,0,0.1]])
	for l in range(len(Vertices)-2):
		zOffsetMatrix = np.vstack([zOffsetMatrix,np.array([0,0,0.1])])
	Vertices = np.vstack([Vertices,Vertices+zOffsetMatrix])
	Vertices = Vertices*10

	os.chdir(Modpath)
	cwd = os.getcwd()
	print(cwd)










