'''
Created on 2025/07/25

@author: sin
'''
import numpy as np
from rdp import rdp
import matplotlib.pyplot as plt


if __name__ == '__main__':
    
    
    # 1. Create a sample polyline (e.g., a noisy line)
    # In a real application, these could be GPS coordinates, sensor data, etc.
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.2, 100) # Add some noise
    points = np.column_stack([x, y])
    print(points)
    # 2. Apply the RDP algorithm
    # epsilon is the maximum distance a point can be from the simplified line segment
    # and still be removed. A larger epsilon results in more simplification.
    epsilon = 0.5
    simplified_points = rdp(points, epsilon=epsilon)
    
    # 3. Visualize the results
    plt.figure(figsize=(10, 6))
    plt.plot(points[:, 0], points[:, 1], 'b-', label='Original Points', alpha=0.7)
    plt.plot(simplified_points[:, 0], simplified_points[:, 1], 'ro-', label=f'Simplified Points (epsilon={epsilon})')
    plt.title('Ramer-Douglas-Peucker Algorithm for Line Simplification')
    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    print(f"Original number of points: {len(points)}")
    print(f"Simplified number of points: {len(simplified_points)}")
