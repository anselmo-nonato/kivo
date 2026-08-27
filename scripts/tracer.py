import numpy as np
from PIL import Image

def find_contours(mask):
    """Simple marching squares / boundary tracer for binary masks"""
    h, w = mask.shape
    padded = np.pad(mask, 1, mode='constant', constant_values=0)
    visited = np.zeros_like(padded, dtype=bool)
    contours = []
    
    # 8-connectivity directions
    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, 1, 1, 1, 0, -1, -1, -1]
    
    for y in range(1, h + 1):
        for x in range(1, w + 1):
            if padded[y, x] and not padded[y, x-1] and not visited[y, x]:
                # Start of a boundary
                contour = []
                curr_x, curr_y = x, y
                d = 0
                start = (curr_x, curr_y)
                
                while True:
                    contour.append((curr_x - 1, curr_y - 1))
                    visited[curr_y, curr_x] = True
                    
                    found = False
                    for i in range(8):
                        nd = (d + i) % 8
                        nx = curr_x + dx[nd]
                        ny = curr_y + dy[nd]
                        if padded[ny, nx]:
                            curr_x, curr_y = nx, ny
                            d = (nd + 6) % 8 # Turn back 90 deg
                            found = True
                            break
                    
                    if not found or (curr_x, curr_y) == start:
                        break
                
                if len(contour) > 10:
                    contours.append(np.array(contour))
    return contours

def rdp(points, epsilon):
    """Ramer-Douglas-Peucker algorithm for polyline simplification"""
    if len(points) < 3:
        return points
    
    start = points[0]
    end = points[-1]
    
    # Line vector
    line_vec = end - start
    line_len = np.linalg.norm(line_vec)
    
    if line_len == 0:
        dists = np.linalg.norm(points - start, axis=1)
    else:
        line_unit = line_vec / line_len
        vecs = points - start
        proj = np.dot(vecs, line_unit)
        proj_pts = start + np.outer(proj, line_unit)
        dists = np.linalg.norm(points - proj_pts, axis=1)
    
    dmax_idx = np.argmax(dists)
    dmax = dists[dmax_idx]
    
    if dmax > epsilon:
        res1 = rdp(points[:dmax_idx+1], epsilon)
        res2 = rdp(points[dmax_idx:], epsilon)
        return np.vstack((res1[:-1], res2))
    else:
        return np.array([start, end])

print('Tracer helper ready')
