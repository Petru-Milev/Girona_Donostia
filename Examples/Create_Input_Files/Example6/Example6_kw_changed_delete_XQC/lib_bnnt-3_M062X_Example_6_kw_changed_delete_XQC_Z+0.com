%nproc=8
%mem=24Gb
%chk=lib_bnnt-3_M062X_Example_6_kw_changed_delete_XQC_Z+0.chk
#P M062X/gen
Symmetry(PG=C4v,SaveOrientation,axis=z)
geom=nocrowd  IOp(9/75=2)
GFINPUT IOP(6/7=3) IOp(6/80=1) IOp(3/59=10) IOp(99/18=-1)
SCF(XQC,Conver=11,MaxCycles=300) Integral(Grid=fine,Acc2E=14,NoXCTest)
IOp(3/33=5) polar

Title Example1 
Cartesian Coordinates. Z direction. Referencing all chk to n-1 

0 2
 O                 -5.52356051    0.92923972   -0.01216441
 H                 -4.56356051    0.92923972   -0.01216441
 H                 -5.84401509    1.83417555   -0.01216441

B N Li H 0
6-31+G(d)
****


