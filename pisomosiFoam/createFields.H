Info<< "Reading/calculating face flux field U\n" << endl;

volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading/calculating field p\n" << endl;

volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::NO_WRITE
    ),
	mesh
    //linearInterpolate(p) & mesh.Sf()
);

Info<< "Reading field pAdj\n" << endl;
volScalarField pAdj
(
    IOobject
    (
        "pAdj",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);


Info<< "Reading field UAdj\n" << endl;
volVectorField UAdj
(
    IOobject
    (
        "UAdj",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading/calculating face flux field phi\n" << endl;

surfaceScalarField phi
(
    IOobject
    (
        "phi",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    fvc::flux(U)
);

Info<< "Reading/calculating face flux field phiAdj\n" << endl;

surfaceScalarField phiAdj
(
    IOobject
    (
        "phiAdj",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    fvc::flux(UAdj)
);

volTensorField gradU
(
    IOobject
    (
        "gradU",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    fvc::grad(U)
);


//#include "createPhi.H"


label pAdjRefCell = 0;
scalar pAdjRefValue = 0.0;
setRefCell(pAdj, piso.dict(), pAdjRefCell, pAdjRefValue);
mesh.setFluxRequired(pAdj.name());


singlePhaseTransportModel laminarTransport(UAdj, phiAdj);

autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New(UAdj, phiAdj, laminarTransport)
);

#include "createMRF.H"
#include "createFvOptions.H"
