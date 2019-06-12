/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Copyright (C) 2011-2018 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Application
    pisoFoam

Description
    Transient solver for incompressible, turbulent flow, using the PISO
    algorithm.

    Sub-models include:
    - turbulence modelling, i.e. laminar, RAS or LES
    - run-time selectable MRF and finite volume options, e.g. explicit porosity

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"
#include "pisoControl.H"
#include "fvOptions.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    #include "postProcess.H"

    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createControl.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    turbulence->validate();

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info<< "\nStarting time loop\n" << endl;

    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << nl << endl;

        #include "CourantNo.H"

        // Pressure-velocity PISO corrector
        {
            #include "UAdjEqn.H"

            // --- PISO loop
            while (piso.correct())
            {
                #include "pAdjEqn.H"
            }
        }

        laminarTransport.correct();
        turbulence->correct();

        runTime.write();

        Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
            << "  ClockTime = " << runTime.elapsedClockTime() << " s"
            << nl << endl;
    }

	Info<<"Creating boundary results for grad calculation..."<<endl;
	fileName outputFile("BoundaryResults.txt");
	OFstream os(outputFile);
	os << "Position	  U	PAdj	UAdj	grad(U)	  grad(UAdj)	facenormal\n"<<endl;
	label inletPatchID = mesh.boundaryMesh().findPatchID("subBoundary"); //Patch identifier of the boundary condition
        
	fvPatchVectorField subU = U.boundaryField()[inletPatchID];
	fvPatchScalarField subPAdj = pAdj.boundaryField()[inletPatchID];
	fvPatchVectorField subUAdj = UAdj.boundaryField()[inletPatchID];
	fvPatchTensorField subgradU = gradU.boundaryField()[inletPatchID];
	fvPatchTensorField subgradUAdj = gradUAdj.boundaryField()[inletPatchID];
        forAll(subU, faceI)  // Loop over each face of the patch
        {
        vector pos(mesh.Cf().boundaryField()[inletPatchID][faceI]);
	vector nor(mesh.Sf().boundaryField()[inletPatchID][faceI]/mesh.magSf().boundaryField()[inletPatchID][faceI]);
        os<<pos<<" "<<subU[faceI]<<" ("<<subPAdj[faceI]<<") "<<subUAdj[faceI]<<" "<<subgradU[faceI]<<" "<<
	subgradUAdj[faceI]<<" "<<nor<<endl;
        
        }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
