%nproc=8
%mem=24Gb
%chk=lib_bnnt-3_LC-BLYP_Z+0.chk
#P LC-BLYP/gen
Symmetry(PG=C4v,SaveOrientation,axis=z)
geom=nocrowd density=current IOp(9/75=2)
GFINPUT IOP(6/7=3) IOp(6/80=1) IOp(3/59=10) IOp(99/18=-1)
SCF(XQC,Conver=11,MaxCycles=300) Integral(Grid=ultrafine,Acc2E=14)
IOp(3/33=5) polar cphf(grid=ultrafine)

Performing LC-BLYP calculation and saving the results
F=Z+1.dF
dF=0.00005au

0 2
 O                 -5.52356051    0.92923972   -0.01216441
 H                 -4.56356051    0.92923972   -0.01216441
 H                 -5.84401509    1.83417555   -0.01216441

B N Li H 0=
6-31+G(d)
****


