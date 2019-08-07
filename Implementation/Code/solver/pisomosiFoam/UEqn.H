// Solve the Momentum equation

MRF.correctBoundaryVelocity(UAdj);

fvVectorMatrix UAdjEqn
(
    -fvm::ddt(UAdj)  + (UAdj & fvc::grad(U)) -fvm::div(phi,UAdj)
  //+ MRF.DDt(U)
  - turbulence->divDevReff(UAdj)
 ==
    fvOptions(UAdj)
);

UAdjEqn.relax();

fvOptions.constrain(UAdjEqn);

if (piso.momentumPredictor())
{
    solve(UAdjEqn == -fvc::grad(pAdj));

    fvOptions.correct(UAdj);
}
