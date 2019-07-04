# cd /opt/pycharm-*/bin
# ./pycharm.sh

import numpy as np
from pathlib import Path
import shutil
import os, re, sys, math, fileinput

#Path Definitions
Modpath     = os.getcwd()
Refpath     = Modpath+'/Reference'
Itpath      = Modpath+'/Iteration_'
NSpath      = Refpath+'/NS'
OSpath      = Refpath+'/OS'

forceResultfile = open("DragForce.dat","w+")
forceResultfile.write("Iteration\tDragForce\n")

# Reading nu from Reference/transportProperties
transport_property = open('Reference/NS/constant/transportProperties','r')
for line in transport_property:
        if 'nu' in line:
                term = '[^;(())\t\n ]+'
                splitline = re.findall(term, line)
                break
nu = float(splitline[8])


folderMultiples = 50
for i in range(700):
    if i%folderMultiples ==1 and i!=1:
        folderNo = i-folderMultiples
        while folderNo%folderMultiples!=0:
            if Path(Itpath+str(folderNo)).exists() == True and folderNo!=1:
                shutil.rmtree(Itpath+str(folderNo))
            folderNo +=1	
    if Path(Itpath+str(i+1)).exists() == False:
        os.mkdir('Iteration_'+str(i+1))
        print('Starting Iteration '+str(i+1)+'.....')
        os.system('cp -r '+Refpath+'/* '+Itpath+str(i+1))
        os.chdir(Itpath+str(i+1)+'/NS')

        blockMeshDict = os.path.isfile(NSpath+'/system/blockMeshDict')
        VertexList = ("1","2","4","5","6","7","8","9","10","11","20","21","23","24","25","26","27", "28","29","30")
        splineList = ("4 5","5 6","6 8","8 10","23 24","24 25","25 27","27 29","1 2","2 7","7 9","9 11","20 21","21 26","26 28","28 30")
        if blockMeshDict:
                if i != 0:
                        index = 0
                        flag = False
                        flagSpline = False
                        for vertex in VertexList:
                                f = open(Itpath+str(i+1)+"/NS/system/blockMeshDict", "r")
                                for line in f:
                                        findText = '//Vertex_' + vertex + '*'
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

                        index =0
                        flag = False
                        for vertex in boundaryVertexList:
                                f = open(Itpath+str(i+1)+"/NS/system/blockMeshDict", "r")
                                for line in f:
                                        findText = '//Vertex_' + vertex + '*'
                                        if findText in line:
                                                replaceline = line
                                                flag = True
                                f.close()

                                if flag == True:
                                        s = open(Itpath+str(i+1)+"/NS/system/blockMeshDict").read()
                                        StripVertex = ' '.join(map(str, boundaryVertices[index]))
                                        s = s.replace(replaceline, '(' + StripVertex + ') ' + findText + '\n')
                                        f = open(Itpath+str(i+1)+"/NS/system/blockMeshDict", 'w')
                                        f.write(s)
                                        f.close()
                                        index = index + 1
                                        flag = False
                        end = 10
                        count = 0
                        p = 0
                        for spline in splineList:
                                f = open(Itpath + str(i + 1) + "/NS/system/blockMeshDict", "r")
                                for line in f:
                                        findText = '//Spline ' + spline
                                        if findText in line:
                                                replaceline = line
                                                flagSpline = True
                                f.close()

                                StripSplinePtList = []
                                if flagSpline == True:
                                        s = open(Itpath+str(i+1)+"/NS/system/blockMeshDict").read()
                                        if count <= (np.size(splineList)/4)-1 or count >= (np.size(splineList)/2) and count < np.size(splineList)*3/4:
                                                zVal = 0
                                        else:
                                                zVal = 0.1
                                        if count < (np.size(splineList)/2):
                                                while p < end:
                                                        StripSplinePt = ' '.join(map(str,np.array([updated_global_pos[p*3],updated_global_pos[p*3+1],zVal])))
                                                        StripSplinePtList.append(StripSplinePt)
                                                        p += 2
                                        else:
                                                while p < end:
                                                        x0_int = updated_global_pos[p*3] * (outerLayer_t + math.sqrt(
                                                                updated_global_pos[p*3+1]**2 + updated_global_pos[p*3]**2)) / math.sqrt(
                                                                updated_global_pos[p*3+1]**2 + updated_global_pos[p*3]**2)
                                                        y0_int = updated_global_pos[p*3+1] * x0_int / updated_global_pos[p*3]
                                                        StripSplinePt = ' '.join(map(str, np.array([x0_int, y0_int, zVal])))
                                                        StripSplinePtList.append(StripSplinePt)
                                                        p += 2
                                        count += 1
                                        end += 10
                                        s = s.replace(replaceline,
                                                                'spline ' + spline + '((' + StripSplinePtList[0] + ')(' + StripSplinePtList[1] + ')(' + \
                                                                StripSplinePtList[2] + ')(' + StripSplinePtList[3] + ')(' + StripSplinePtList[4] + '))' + findText + '\n')
                                        f = open(Itpath+str(i+1)+"/NS/system/blockMeshDict", 'w')
                                        f.write(s)
                                        f.close()
                                        index += 1
                                        if count == (np.size(splineList)/4) or count == (np.size(splineList)/2) or count == np.size(splineList)*3/4:
                                                p = 0
                                                end = 10
                                        flagSpline = False
                
                os.system('blockMesh >outputblockMesh.txt')
                os.system('checkMesh >outputcheckMesh.txt')
                
                #ToDo: if checkmesh last but second line says mesh: ok, then execute next line
                print('Iter-'+str(i+1)+' (NS): Meshing done and checked!')
                print('Iter-'+str(i+1)+' (NS): Running solver...')
                os.system('simpleFoam > outputNS.txt')
                print('Iter-'+str(i+1)+' (NS): End of solution!')
        else:
                print('Block Mesh Dictionary is not available')
                sys.exit(1)
        endTimeNS = '0'
        iterationNSFolder = os.listdir(Itpath+str(i+1)+'/NS')
        for directory in iterationNSFolder:
	        if directory.replace('.','',1).isdigit():
		        if float(endTimeNS) < float(directory):
			        endTimeNS = str(directory)
        
        os.system('cp '+Itpath+str(i+1)+'/NS/'+endTimeNS+'/p '+Itpath+str(i+1)+'/OS/0')
        os.system('cp '+Itpath+str(i+1)+'/NS/'+endTimeNS+'/U '+Itpath+str(i+1)+'/OS/0')
        
        dragForceFile   = open(Itpath+str(i+1)+'/NS/postProcessing/forces/0/forces.dat','r')
        lastline        = dragForceFile.readlines()
        lastline        = lastline[-1]
        term = '[^(())\t\n ]+'
        splitDoubleBraces = re.findall(term, lastline)
        DragForceX      = float(splitDoubleBraces[1])+float(splitDoubleBraces[4])
        print('Iter-'+str(i+1)+': Writing drag force to file..!')
        
        forceResultfile.write(str(i)+"\t"+str(DragForceX)+"\n")
        
        f = fileinput.FileInput(Itpath+str(i+1)+'/OS/0/UAdj', inplace=True)
        for line in f:
                findText = 'value           uniform (1 0 0);'
                replaceText = 'value           uniform ('+str(DragForceX)+' 0 0);'
                print(line.replace(findText, replaceText), end='')
        
        f.close()

        os.chdir(Itpath+str(i+1)+'/OS')
        os.system('cp '+Itpath+str(i+1)+'/NS/system/blockMeshDict '+Itpath+str(i+1)+'/OS/system/')
        os.system('blockMesh >outputblockMesh.txt')
        os.system('checkMesh >outputcheckMesh.txt')
        
        
        print('Iter-'+str(i+1)+' (OS): Meshing done and checked!')
        print('Iter-'+str(i+1)+' (OS): Running solver...')
        os.system('pisomosiFoam >outputOS.txt')
        print('Iter-'+str(i+1)+' (OS): End of solution!')

        # Calculation of new boundary Coordinates
        print('Iter-'+str(i+1)+': Calculating new boundary points...')
        #TODO=====> DONE <======: to be read from the Transportproperties dictfile
        #nu = .01 # viscosity =====> Added above : read only once from Reference

        #TODO: to be updated to control the sudden jump of coordinates
        weight =1 # weight = 1/w


        word = []
        with open (Itpath+str(i+1)+'/OS/BoundaryResults.txt') as file:
                for line in file:
                        word.append(re.findall(r'[^(())\t\n ]+',line))
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

        lineSize = len(indicespos)+len(indicesU)+len(indicesPadj)+len(indicesUadj)+len(indicesGradu)+len(indicesGraduAdj) +len(indicesNormal)
        
        boundaryFile = open(Itpath+str(i+1)+'/NS/constant/polyMesh/boundary','r')
        boundaryFound = False
        for line in boundaryFile:
                if 'subBoundary' in line:
                        boundaryFound = True
                if boundaryFound:
                        if 'nFaces' in line:
                                term = '[^;(())\t\n ]+'
                                splitline = re.findall(term, line)
                                break
        nFaces = int(splitline[1])

        outerLayer_t = 1

        global_Corrector = np.array([])
        global_pos = np.array([])

        for k in range(0,nFaces):
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
                corrector = gradU.reshape(3,3).T.dot(s)

                global_Corrector=np.append(global_Corrector,corrector)
                global_pos = np.append(global_pos,pos)
        minWeight = 1e-5
        tol = 0.001
        while weight > minWeight:
                updated_global_pos = global_pos - weight*global_Corrector
                withinTolFlag = np.allclose(updated_global_pos,global_pos,rtol=tol, atol=1e-08, equal_nan=False)
                if not withinTolFlag:
                        weight = 0.1*weight
                else:
                        break
        if weight<minWeight:
                print('Weight used: '+str(weight/0.1))
        else:
                print('Weight used: '+str(weight))

        # Constraining the updation of coordinates
        coordCount = 0
        for coordindex in range (len(updated_global_pos)):
                if updated_global_pos[coordindex] > (global_pos[coordindex]*(1+tol)):
                        coordCount = coordCount +1
                        updated_global_pos[coordindex] = (global_pos[coordindex]*(1+tol))
                elif updated_global_pos[coordindex] < (global_pos[coordindex]*(1-tol)):
                        coordCount = coordCount +1
                        updated_global_pos[coordindex] = (global_pos[coordindex]*(1-tol))
        print(str(coordCount)+' Coordinates constrained back to the tolerance limit '+str(tol))

        UnitConversionFactor = 0.1 #TODO to be read from blockMeshDict file

        updated_global_pos = updated_global_pos*1/UnitConversionFactor
        #TODO include the below in a for loop
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
        
        Vertex_5 = (facepoint_9 + facepoint_10)/2
        
        Vertex_6 = (facepoint_19 + facepoint_20)/2
        
        Vertex_8 = (facepoint_29 + facepoint_30)/2
        
        # Vertices of outer layer
        Vertex_1 = np.array([Vertex_4[0]-outerLayer_t,0,0])
        
        x_Vertex_2 = Vertex_5[0]*(1+outerLayer_t/math.sqrt((Vertex_5[1])**2 +(Vertex_5[0])**2 ))
        Vertex_2 = np.array([x_Vertex_2,Vertex_5[1]/Vertex_5[0]*x_Vertex_2,0])
        
        x_Vertex_9 = Vertex_8[0]*(1+outerLayer_t/math.sqrt((Vertex_8[1])**2 +(Vertex_8[0])**2 ))
        Vertex_9 = np.array([x_Vertex_9,Vertex_8[1]/Vertex_8[0]*x_Vertex_9,0])

        if Vertex_6[0]!=0:
                        x_Vertex_7 = Vertex_6[0]*(1+outerLayer_t/math.sqrt((Vertex_6[1])**2 +(Vertex_6[0])**2 ))
                        Vertex_7 = np.array([x_Vertex_7,Vertex_6[1]/Vertex_6[0]*x_Vertex_7,0])
        else:
                        Vertex_7 = np.array([0,Vertex_6[1]+outerLayer_t,0])

        
        Vertex_11= np.array([Vertex_10[0]+outerLayer_t,0,0])
        
        Vertices = np.array([Vertex_1,Vertex_2])
        Vertices = np.vstack([Vertices,Vertex_4])
        Vertices = np.vstack([Vertices,Vertex_5])
        Vertices = np.vstack([Vertices,Vertex_6])
        Vertices = np.vstack([Vertices,Vertex_7])
        Vertices = np.vstack([Vertices,Vertex_8])
        Vertices = np.vstack([Vertices,Vertex_9])
        Vertices = np.vstack([Vertices,Vertex_10])
        Vertices = np.vstack([Vertices,Vertex_11])
        
        zOffset = 0.1
        
        zOffsetMatrix = np.array([[0,0,zOffset],[0,0,zOffset]])
        for l in range(len(Vertices)-2):
                zOffsetMatrix = np.vstack([zOffsetMatrix,np.array([0,0,zOffset])])
        Vertices = np.vstack([Vertices,Vertices+zOffsetMatrix])
        xLeft=-3
        xRight= 5
        yTop=5
        yBottom=0
        zOffsetMatrix = np.array([[0,0,zOffset],[0,0,zOffset]])
        
        boundaryVertexList = ("3","13","15","16","17","22","32","34","35","36")
        boundaryVertices = np.array([[xLeft,Vertex_2[1],0],[xRight,Vertex_9[1],0]])
        boundaryVertices = np.vstack([boundaryVertices,[Vertex_9[0],yTop,0]])
        boundaryVertices = np.vstack([boundaryVertices,[Vertex_7[0],yTop,0]])
        boundaryVertices = np.vstack([boundaryVertices,[Vertex_2[0],yTop,0]])
        for l in range(len(boundaryVertices)-2):
                zOffsetMatrix = np.vstack([zOffsetMatrix,np.array([0,0,zOffset])])
        boundaryVertices = np.vstack([boundaryVertices,boundaryVertices+zOffsetMatrix])

        os.chdir(Modpath)
        print('End of Iteration '+str(i+1)+'.')
        print('\n')
forceResultfile.close()
