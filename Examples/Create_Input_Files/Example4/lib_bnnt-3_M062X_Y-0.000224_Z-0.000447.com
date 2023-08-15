%nproc=8
%mem=24Gb
%oldchk=lib_bnnt-3_M062X_Y+0_Z+0.chk
%chk=lib_bnnt-3_M062X_Y-0.000224_Z-0.000447.chk
#P M062X/gen
Symmetry(PG=C4v,SaveOrientation,axis=z)
geom=nocrowd density=current IOp(9/75=2)
GFINPUT IOP(6/7=3) IOp(6/80=1) IOp(3/59=10) IOp(99/18=-1)
SCF(XQC,Conver=11,MaxCycles=300) Integral(Grid=fine,Acc2E=14,NoXCTest,NoXCTest,NoXCTest,NoXCTest,NoXCTest)
IOp(3/33=5) polar
IOp(3/14=-6)
ChkBasis geom=check guess=(read) GFInput

Title Example2 
Spherical Coordinates. Z direction. Referencing all chk to n-1 

0 2

0.000000 -0.000224 -0.000447

B N Li H 0
6-31+G(d)
****

B N Li H 0
6-31+G(d)
****

B N Li H 0
6-31+G(d)
****

B N Li H 0
6-31+G(d)
****

B N Li H 0
6-31+G(d)
****


