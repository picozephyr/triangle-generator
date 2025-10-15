import cv2
import numpy as np
from skimage import io
import matplotlib.pyplot as plt



my_image = io.imread("/Users/zephyrburka/Downloads/red-cube-icon-isometric-red-cube-vector-icon-web-design-isolated-white-background_96318-42681.jpg")
my_image = cv2.resize(my_image, (256, 256))
plt.imshow(my_image)
plt.axis("off")
plt.show()

canvas = np.zeros_like(my_image) + 255
plt.imshow(canvas)
plt.axis("off")
plt.show()

def mse_fast(image, canvas):
    return np.mean((image.astype("float") - canvas.astype("float")) ** 2)
print(mse_fast(my_image, canvas))
true_mse = mse_fast(my_image, canvas)
fake_mse = true_mse
h, w, c = my_image.shape
def random_triangle(height, width):
    pts = np.array([
        [np.random.randint(0, width), np.random.randint(0, height)],
        [np.random.randint(0, width), np.random.randint(0, height)],
        [np.random.randint(0, width), np.random.randint(0, height)]
    ], dtype=np.int32)
    return pts

def random_color():
    return (np.random.randint(0,256), np.random.randint(0,256), np.random.randint(0,256))


def mutate_triangle(triangle, w, h):
    new_triangle = triangle.copy()
    new_triangle["pts"] = triangle["pts"].copy()
    i = np.random.randint(0, 3)
    addx = np.random.uniform(-(w/10), (w/10)+1)
    addy = np.random.uniform(-(h/10), (h/10)+1)
    new_triangle["pts"][i][0] = np.clip(new_triangle["pts"][i][0] + addx, 0, w)
    new_triangle["pts"][i][1] = np.clip(new_triangle["pts"][i][1] + addy, 0, h)
    return new_triangle

def mutate_color(triangle):
    new_triangle = triangle.copy()
    new_color = list(triangle["color"])
    i = np.random.randint(0, 3)
    change = np.random.randint(-30, 31)
    new_value = new_color[i] + change
    if new_value < 0:
        new_value = 0
    if new_value > 255:
        new_value = 255
    new_color[i] = new_value
    new_triangle["color"] = tuple(new_color)
    return new_triangle



num = 1
true_mse = mse_fast(my_image, canvas)  # Initialize

for i in range(20):  # Add 20 shapes
    best_triangle = None
    best_triangle_mse = true_mse
    
    # Try 10 random candidate shapes
    for shapes in range(10):
        # Random starting triangle
        triangle = {
            "pts": random_triangle(h, w),
            "color": random_color()
        }
        
        candidate_mse = true_mse  # ← KEY: Start from current baseline
        best_shape = triangle
        
        # === PHASE 1: Optimize SHAPE (keep color fixed) ===
        for mutations in range(1500):
            test_triangle = best_shape.copy()
            test_triangle["pts"] = best_shape["pts"].copy()
            
            # Only mutate shape
            test_triangle = mutate_triangle(test_triangle, w, h)

            test_canvas = canvas.copy()
            cv2.fillPoly(test_canvas, [test_triangle["pts"]], test_triangle["color"])
            test_mse = mse_fast(my_image, test_canvas)

            if test_mse < candidate_mse:
                best_shape = test_triangle
                candidate_mse = test_mse
        
        # === PHASE 2: Optimize COLOR (keep shape fixed) ===
        for mutations in range(1500):
            test_triangle = best_shape.copy()
            
            # Only mutate color
            test_triangle = mutate_color(test_triangle)

            test_canvas = canvas.copy()
            cv2.fillPoly(test_canvas, [test_triangle["pts"]], test_triangle["color"])
            test_mse = mse_fast(my_image, test_canvas)

            if test_mse < candidate_mse:
                best_shape = test_triangle
                candidate_mse = test_mse
        
        # Is this the best candidate so far?
        if candidate_mse < best_triangle_mse:
            best_triangle = best_shape
            best_triangle_mse = candidate_mse
    
    # Add best triangle to canvas (safety check)
    if best_triangle is not None:
        cv2.fillPoly(canvas, [best_triangle["pts"]], best_triangle["color"])
        true_mse = best_triangle_mse
        print(f"Shape {num}/20, MSE: {true_mse:.2f}")
    else:
        print(f"Shape {num}/20: No improvement found, skipping")
    num += 1
        
    cv2.fillPoly(canvas, [best_triangle["pts"]], best_triangle["color"])
    true_mse = mse_fast(my_image, canvas)
    print(num)
    num = num + 1



    
plt.imshow(canvas)
plt.axis("off")
plt.show()

