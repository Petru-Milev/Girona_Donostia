%nproc=8
%mem=24Gb
%oldchk=lib_bnnt-3_M062X_Example_4_Y+0_Z+0.chk
%chk=lib_bnnt-3_M062X_Example_4_Y-0.000745_Z-0.001491.chk
#P M062X/gen
Symmetry(PG=C4v,SaveOrientation,axis=z)
geom=check density=current ChkBasis guess=(read) IOp(9/75=2)
GFINPUT IOP(6/7=3) IOp(6/80=1) IOp(3/59=10) IOp(99/18=-1)
SCF(Conver=11,MaxCycles=300) Integral(Grid=fine,Acc2E=14,NoXCTest)
IOp(3/14=-6) polar
GFInput

Title Example4
Cartesian Coordinates. Specified direction. Referencing all zero
Keywords Automatically Updated

0 2

0.000000 -0.000745 -0.001491

B N Li H 0
6-31+G(d)
****


