import math

from Utils import Point2D

def sign(x):
    """
    Returns the sign of x.
    +1 if x > 0
    -1 if x < 0
     0 if x == 0
    """
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def visualize_line_matplotlib(cells, margin=1):
    import matplotlib.pyplot as plt
    """
    Visualize Bresenham output using matplotlib,
    with automatic grid sizing.
    """
    xs_cells = [c.x for c in cells]
    ys_cells = [c.y for c in cells]

    min_x = min(xs_cells) - margin
    max_x = max(xs_cells) + margin + 1
    min_y = min(ys_cells) - margin
    max_y = max(ys_cells) + margin + 1

    # Cell centers
    xs = [x + 0.5 for x in xs_cells]
    ys = [y + 0.5 for y in ys_cells]

    # Start and end (centers)
    sx, sy = xs[0], ys[0]
    ex, ey = xs[-1], ys[-1]

    plt.figure(figsize=(6, 6))

    # Draw grid
    for x in range(min_x, max_x + 1):
        plt.plot([x, x], [min_y, max_y], color="lightgray", linewidth=0.5)
    for y in range(min_y, max_y + 1):
        plt.plot([min_x, max_x], [y, y], color="lightgray", linewidth=0.5)

    # Ideal continuous line
    plt.plot([sx, ex], [sy, ey],
             color="black", linestyle="--", linewidth=2,
             label="Ideal line")

    # Bresenham cells
    plt.scatter(xs, ys, color="blue", s=100, label="Bresenham cells")

    # Start and end
    plt.scatter(sx, sy, color="green", s=150, label="Start")
    plt.scatter(ex, ey, color="red", s=150, label="End")

    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)
    plt.gca().set_aspect("equal")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.title("Bresenham vs Ideal Line (Auto Grid Size)")
    plt.show()

def bresenham(p0: Point2D, p1: Point2D):
    """
    Enumerate all grid cells from (x0, y0) to (x1, y1) using Bresenham's line algorithm.
    
    Returns:
        List of Point2D(x, y) grid coordinates along the line, including start and end.
    """
    cells = []

    dx = abs(p1.x - p0.x)
    dy = abs(p1.y - p0.y)
    sx = sign(p1.x - p0.x)
    sy = sign(p1.y - p0.y)

    p = p0.copy();

    if dx > dy:
        err = dx // 2
        while p.x != p1.x:
            cells.append(p.copy())
            err -= dy
            if err < 0:
                p.y += sy
                err += dx
            p.x += sx
        cells.append(p.copy())
    else:
        err = dy // 2
        while p.y != p1.y:
            cells.append(p.copy())
            err -= dx
            if err < 0:
                p.x += sx
                err += dy
            p.y += sy
        cells.append(p.copy())

    return cells

def run_bresenham_tests(bresenham_fn):
    tests = [
        {
            "name": "Horizontal right",
            "start": (2, 3),
            "end": (7, 3),
            "expected": [(2,3), (3,3), (4,3), (5,3), (6,3), (7,3)],
        },
        {
            "name": "Vertical up",
            "start": (4, 1),
            "end": (4, 6),
            "expected": [(4,1), (4,2), (4,3), (4,4), (4,5), (4,6)],
        },
        {
            "name": "Diagonal 45 degrees",
            "start": (1, 1),
            "end": (6, 6),
            "expected": [(1,1), (2,2), (3,3), (4,4), (5,5), (6,6)],
        },
        {
            "name": "Shallow slope (dx > dy)",
            "start": (2, 2),
            "end": (9, 5),
            "expected": [(2,2), (3,2), (4,3), (5,3), (6,4), (7,4), (8,5), (9,5)],
        },
        {
            "name": "Steep slope (dy > dx)",
            "start": (3, 2),
            "end": (6, 9),
            "expected": [(3,2), (3,3), (4,4), (4,5), (5,6), (5,7), (6,8), (6,9)],
        },
        {
            "name": "Negative direction",
            "start": (8, 6),
            "end": (3, 2),
            "expected": [(8,6), (7,5), (6,5), (5,4), (4,3), (3,2)],
        },
        {
            "name": "Single point",
            "start": (5, 5),
            "end": (5, 5),
            "expected": [(5,5)],
        },
        {
            "name": "LiDAR-style ray",
            "start": (10, 10),
            "end": (16, 13),
            "expected": [(10,10), (11,10), (12,11), (13,11), (14,12), (15,12), (16,13)],
        },
    ]

    all_passed = True

    for t in tests:
        result = bresenham_fn(Point2D(*t["start"]), Point2D(*t["end"]))
        expected = [Point2D(*tup) for tup in t["expected"]]
        ok = result == expected
        all_passed &= ok

        print(f"{t['name']}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print("  expected:", t["expected"])
            print("  got     :", result)
        visualize_line_matplotlib(result)

    print("\nOverall:", "PASS" if all_passed else "FAIL")


if __name__ == "__main__":
    # Example start and end cells (e.g., robot to LiDAR hit)
    #start_x, start_y = 2, 2
    #end_x, end_y = 9, 5

    #cells = bresenham(start_x, start_y, end_x, end_y)

    #print("Ray-traced cells, Expected:\n[(2,2) (3,2) (4,3) (5,3) (6,4) (7,4) (8,5) (9,5)]")
    #print("Result")
    #print(cells)

    run_bresenham_tests(bresenham)

