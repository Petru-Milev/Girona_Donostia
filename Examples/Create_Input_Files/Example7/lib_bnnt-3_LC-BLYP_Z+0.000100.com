%nproc=8
%mem=24Gb
%oldchk=lib_bnnt-3_LC-BLYP_Z+0.chk
%chk=lib_bnnt-3_LC-BLYP_Z+0.000100.chk
#P LC-BLYP
Symmetry(PG=C4v,SaveOrientation,axis=z)
geom=check density=current ChkBasis guess=(read) IOp(9/75=2)
GFINPUT IOP(6/7=3) IOp(6/80=1) IOp(3/59=10) IOp(99/18=-1)
SCF(Conver=11,MaxCycles=300) Integral(Grid=ultrafine,Acc2E=14)
IOp(3/14=-6) polar cphf(grid=ultrafine)

Performing LC-BLYP calculation and saving the results
F=Z+1.dF
dF=0.00005au

0 2

0.0000e+00 0.0000e+00 1.0000e-04


