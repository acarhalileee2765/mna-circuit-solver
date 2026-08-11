import numpy as np
matrix = np.array([[8,2 ,1 ], 
                   [0, 4, 7], 
                   [3, -3, 1]])
solve = np.linalg.solve(matrix, [4,9,-5])
print (solve)

print(matrix.shape)
print(f"I1 is {solve[0]} ampere")
print(f"I2 is {solve[1]} ampere")
print(f"I3 is {solve[2]} ampere")



