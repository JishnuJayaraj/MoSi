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
    icoFoam

Description
    Transient solver for incompressible, laminar flow of Newtonian fluids.

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "pisoControl.H"
#include "OFstream.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"

    pisoControl piso(mesh);

    #include "createFields.H"
    #include "initContinuityErrs.H"

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info<< "\nStarting time loop\n" << endl;

	fileName outputFile("TEST.txt");
	OFstream os(outputFile);
	os << "Position	P	U	PAdj	UAdj.\n"<<endl;
	label inletPatchID = mesh.boundaryMesh().findPatchID("subBoundary"); //Patch identifier of the boundary condition
        fvPatchScalarField subP = p.boundaryField()[inletPatchID];
	fvPatchVectorField subU = U.boundaryField()[inletPatchID];
  // Obtain a patchScalar field on the BC
	double x;
	double y;

        forAll(subP, faceI)  // Loop over each face of the patch
        {
        vector pos(mesh.Cf().boundaryField()[inletPatchID][faceI]);
        os<<"("<<pos[0]<<" "<<pos[1]<<")"<<" ("<<subP[faceI]<<")"<<" ("<<subU[faceI]<<")"<<endl;
        
        //oswallP[faceI]=Foam::cos(22/7*x)*Foam::cos(22/7*y);;
        }


    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << nl << endl;

        #include "UAdjCourantNo.H"

        // Momentum predictor
	
	//volVectorField UAdj_app = UAdj & fvc::grad(U);
        fvVectorMatrix UAdjEqn
        (
           - fvm::ddt(UAdj)
          + (UAdj & fvc::grad(U))
	  - fvm::div(phi,UAdj)
          - fvm::laplacian(nu, UAdj)
        );
Info<<"Momentum predictor UAdjEqn"<<endl;

        if (piso.momentumPredictor())
        {
            solve(UAdjEqn == -fvc::grad(pAdj));
        }

Info<<"PISO loop"<<endl;
        // --- PISO loop
        while (piso.correct())
        {
            volScalarField rAU(1.0/UAdjEqn.A());
            volVectorField HbyA(constrainHbyA(rAU*UAdjEqn.H(), UAdj, pAdj));
            surfaceScalarField phiHbyA
            (
                "phiHbyA",
                fvc::flux(HbyA)
              + fvc::interpolate(rAU)*fvc::ddtCorr(UAdj, phiAdj)
            );

            adjustPhi(phiHbyA, UAdj, pAdj);

            // Update the pressure BCs to ensure flux consistency
            constrainPressure(pAdj, UAdj, phiHbyA, rAU);

            // Non-orthogonal pressure corrector loop
            while (piso.correctNonOrthogonal())
            {
                // Pressure corrector

                fvScalarMatrix pAdjEqn
                (
                    fvm::laplacian(rAU, pAdj) == fvc::div(phiHbyA)
                );

                pAdjEqn.setReference(pAdjRefCell, pAdjRefValue);

                pAdjEqn.solve(mesh.solver(pAdj.select(piso.finalInnerIter())));

                if (piso.finalNonOrthogonalIter())
                {
                    phiAdj = phiHbyA - pAdjEqn.flux();
                }
            }

            #include "continuityErrs.H"

            UAdj = HbyA - rAU*fvc::grad(pAdj);
            UAdj.correctBoundaryConditions();
        }

        runTime.write();

        Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
            << "  ClockTime = " << runTime.elapsedClockTime() << " s"
            << nl << endl;
    }
	

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
