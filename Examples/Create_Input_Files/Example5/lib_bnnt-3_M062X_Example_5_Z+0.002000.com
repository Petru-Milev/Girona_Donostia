%nproc=8
%mem=24Gb
%oldchk=lib_bnnt-3_M062X_Example_5_Z+0.001500.chk
%chk=lib_bnnt-3_M062X_Example_5_Z+0.002000.chk
#P M062X
Symmetry(PG=C4v,SaveOrientation,axis=z)
density=current IOp(9/75=2)
GFINPUT IOP(6/7=3) IOp(6/80=1) IOp(3/59=10) IOp(99/18=-1)
SCF(Conver=11,MaxCycles=300) Integral(Grid=fine,Acc2E=14,NoXCTest)
IOp(3/14=-6) polar
ChkBasis geom=check guess=(read) GFInput

Title Example5
Cartesian Coordinates. Z direction. Assymetrical Range.  Referencing n-1
Keywords Automatically Updated. Using only keywords in Gaussian Section. No new_kw keyword. 
Usage of Automatically_update_keywords is vital here. 

0 2

0.000000 0.000000 0.002000


