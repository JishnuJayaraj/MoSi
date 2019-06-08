volScalarField rAU(1.0/UAdjEqn.A());
volVectorField HbyA(constrainHbyA(rAU*UAdjEqn.H(), UAdj, pAdj));
surfaceScalarField phiHbyA
(
    "phiHbyA",
    fvc::flux(HbyA)
  + MRF.zeroFilter(fvc::interpolate(rAU)*fvc::ddtCorr(UAdj, phiAdj))
);

MRF.makeRelative(phiHbyA);

adjustPhi(phiHbyA, UAdj, pAdj);

// Update the pressure BCs to ensure flux consistency
constrainPressure(pAdj, UAdj, phiHbyA, rAU, MRF);

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
fvOptions.correct(U);
