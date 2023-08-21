import numpy as np 

def RR(fp, fm, xp, xm):
	return (fp-fm)/(xp-xm)
def P(p,k):
	if p==0:
		romberg_matrix[k,p] = RR(v_y[p_max - k - 1], v_y[k+p_max+1], v_x[p_max - k - 1], v_x[k+p_max+1])
		return RR(v_y[p_max - k - 1], v_y[k+p_max+1], v_x[p_max - k - 1], v_x[k+p_max+1])
	else:
		romberg_matrix[k,p] = (4**p * P(p-1, k) - P(p-1, k+1))/(4**p - 1) 
		return (4**p * P(p-1, k) - P(p-1, k+1))/(4**p - 1)



v_x = [-0.1024, -0.0512, -0.0256, -0.0128, -0.0064, -0.0032, -0.0016, -0.0008, -0.0004, 0, 0.0004, 0.0008, 0.0016, 0.0032, 0.0064, 0.0128, +0.0256 +0.0512, 0.1024]
v_x = np.longdouble(np.array(v_x))
v_y = (v_x+1)** 6 + 2
p_max = len(v_x)/2 - 1 
p_max = int(p_max)
romberg_matrix = np.zeros((p_max+1, p_max+1))
P(p_max, 0)
np.savetxt("romberg_matrix.csv", romberg_matrix)
print(romberg_matrix)
print(v_x[p_max])