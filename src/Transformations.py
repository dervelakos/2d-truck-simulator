# transformation_chain.py

import numpy as np
import matplotlib.pyplot as plt
from Utils import Point2D

class Transform:
    def __init__(self, rads: float, t: Point2D):
        self.T = np.array([
            [np.cos(rads), -np.sin(rads), t.x],
            [np.sin(rads),  np.cos(rads), t.y],
            [0           ,  0           , 1  ]
        ])

    def getMatrix(self):
        return self.T

class TransformChain:
    def __init__(self):
        self.chain = []
        self.T = np.eye(3)

    def addFrame(self, frame):
        self.chain.append(frame)
        self.T = self.T @ frame.getMatrix()
        return self

    def transformNew(self, points):
        transformedPoints = []
        for p in points:
            v = np.array([p.x, p.y, 1])
            v_new = self.T @ v
            transformedPoints.append(Point2D(v_new[0], v_new[1]))
        return transformedPoints
import matplotlib.pyplot as plt

def visualize_transformation(before_points, after_points, title="Transformation Visualization"):
    """
    Visualizes points before and after a transformation.
    Marks the origin (0,0). Press Esc to close the window.

    Parameters:
    - before_points: list of Point2D (original points)
    - after_points: list of Point2D (transformed points)
    - title: optional title for the plot
    """
    import matplotlib.pyplot as plt  # Import inside the function

    # Extract coordinates
    before_x = [p.x for p in before_points]
    before_y = [p.y for p in before_points]

    after_x = [p.x for p in after_points]
    after_y = [p.y for p in after_points]

    fig, ax = plt.subplots(figsize=(6,6))

    # Plot origin
    ax.scatter([0], [0], color='green', s=60, label='Origin (0,0)')
    ax.text(0.05, 0.05, "0,0", color='green')

    # Plot before points
    ax.scatter(before_x, before_y, color='blue', label='Before', s=50)
    for i, p in enumerate(before_points):
        ax.text(p.x + 0.05, p.y + 0.05, f"{i}", color='blue')

    # Plot after points
    ax.scatter(after_x, after_y, color='red', label='After', s=50)
    for i, p in enumerate(after_points):
        ax.text(p.x + 0.05, p.y + 0.05, f"{i}", color='red')

    # Draw dashed lines connecting before → after
    for bp, ap in zip(before_points, after_points):
        ax.plot([bp.x, ap.x], [bp.y, ap.y], 'k--', linewidth=0.8)

    # Configure plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(title)
    ax.legend()
    ax.axis('equal')
    ax.grid(True)

    # Key press event: Esc closes window
    def on_key(event):
        if event.key == 'escape':
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()


def run_transformation_tests():
    tests = [
        {
            "name": "Tansformation1",
            "original": [(2,3), (3,3)],
            "expected": [(3,5), (4,5)],
            "transform": TransformChain().addFrame(Transform(0, Point2D(1.0, 2.0)))
        },
        {
            "name": "Tansformation2",
            "original": [(2,3), (3,3), (3,0)],
            "expected": [(-3,2), (-3,3), (0,3)],
            "transform": TransformChain().addFrame(Transform(np.radians(90), Point2D(0.0, 0.0)))
        },
    ]

    all_passed = True

    for t in tests:
        original = [Point2D(*tup) for tup in t["original"]]
        result = t["transform"].transformNew(original)
        expected = [Point2D(*tup) for tup in t["expected"]]
        ok = result == expected
        all_passed &= ok

        print(f"{t['name']}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print("  expected:", t["expected"])
            print("  got     :", result)
        visualize_transformation(original, result)

    print("\nOverall:", "PASS" if all_passed else "FAIL")

if __name__ == "__main__":
    original = [
        Point2D(0, 0),
        Point2D(1, 100),
        Point2D(2, 0),
    ]

    transformed = [
        Point2D(400, 0),
        Point2D(1, 2),
        Point2D(2, 1),
    ]

    #visualize_transformation(original, transformed)
    run_transformation_tests()

