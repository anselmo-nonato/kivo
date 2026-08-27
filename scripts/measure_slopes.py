from PIL import Image
import numpy as np

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)
alpha = arr[:, :, 3]

# 1. Lower Arm Edges:
# Let's find the top straight edge of the lower arm across X=320 to 440:
print("--- Lower Arm Top Edge Points ---")
top_points = []
for x in range(320, 440, 10):
    # Search for first solid pixel from Y=450 to 650
    ys = np.where(alpha[450:650, x] > 100)[0] + 450
    if len(ys) > 0:
        top_points.append((x, ys.min()))
        print(f"X={x}: Top Y={ys.min()}")

# Linear fit on lower arm top edge: y = m*x + b
xs = np.array([p[0] for p in top_points])
ys = np.array([p[1] for p in top_points])
m_arm, b_arm = np.polyfit(xs, ys, 1)
angle_arm = np.degrees(np.arctan(m_arm))
print(f"Lower Arm Top Edge Slope: m={m_arm:.4f}, Angle={angle_arm:.2f} deg, b={b_arm:.2f}")

# 2. Arrow Shaft Top Edge Points:
print("--- Arrow Shaft Top Edge Points ---")
arrow_points = []
for y in range(330, 430, 10):
    xs = np.where(alpha[y, 300:480] > 100)[0] + 300
    if len(xs) > 0:
        arrow_points.append((xs.min(), y))
        print(f"Y={y}: Leftmost X={xs.min()}")

xs_arr = np.array([p[0] for p in arrow_points])
ys_arr = np.array([p[1] for p in arrow_points])
m_arrow, b_arrow = np.polyfit(xs_arr, ys_arr, 1)
angle_arrow = np.degrees(np.arctan(m_arrow))
print(f"Arrow Shaft Left Edge Slope: m={m_arrow:.4f}, Angle={angle_arrow:.2f} deg, b={b_arrow:.2f}")
