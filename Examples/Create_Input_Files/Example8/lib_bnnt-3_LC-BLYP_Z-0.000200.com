%nproc=8
%mem=24Gb
%chk=lib_bnnt-3_LC-BLYP_Z-0.000200.chk
#P cam-b3lyp/6-31g(d')
nosymm gfinput pop=full polar=(dcshg,cubic) cphf=sg1grid
IOp(3/14=-6)

Log Step Example

0 2
 O                 -5.52356051    0.92923972   -0.01216441
 H                 -4.56356051    0.92923972   -0.01216441
 H                 -5.84401509    1.83417555   -0.01216441

0.0000e+00 0.0000e+00 -2.0000e-04


