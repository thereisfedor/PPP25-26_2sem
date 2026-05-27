import math
import itertools
import functools
import matplotlib.pyplot as plt

def visualize_polygons(polygons, title="Polygons", colors=None, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    if colors is None:
        colors = itertools.cycle(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'])
    for poly, color in zip(polygons, colors):
        if not poly or len(poly) < 3:
            continue
        closed_poly = list(poly) + [poly[0]]
        xs, ys = zip(*closed_poly)
        ax.fill(xs, ys, alpha=0.4, fc=color, ec='black', linewidth=1.5)
        ax.plot(xs, ys, color='black', linewidth=1)
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.grid(True)
    return ax

def gen_rectangle(step_x=1.5, step_y=0, width=1, height=1, start=(0,0)):
    x0, y0 = start
    i = 0
    while True:
        x = x0 + i * step_x
        y = y0 + i * step_y
        yield ((x, y), (x+width, y), (x+width, y+height), (x, y+height))
        i += 1

def gen_triangle(step_x=1.5, step_y=0.8, base=1, height=1, start=(0,0)):
    x0, y0 = start
    i = 0
    while True:
        x = x0 + i * step_x
        y = y0 + i * step_y
        yield ((x, y), (x+base, y), (x+base/2, y+height))
        i += 1

def gen_hexagon(step_x=1.8, step_y=0, radius=0.6, start=(0,0)):
    x0, y0 = start
    i = 0
    while True:
        cx = x0 + i * step_x
        cy = y0 + i * step_y
        hexagon = []
        for k in range(6):
            angle = math.pi/2 + k * math.pi/3
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            hexagon.append((x, y))
        yield tuple(hexagon)
        i += 1

def tr_translate(dx, dy):
    return lambda poly: tuple((x+dx, y+dy) for (x, y) in poly)

def tr_rotate(angle_deg, cx=0, cy=0):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    def transform(poly):
        return tuple((cx + (x-cx)*cos_a - (y-cy)*sin_a,
                      cy + (x-cx)*sin_a + (y-cy)*cos_a) for (x,y) in poly)
    return transform

def tr_symmetry(axis='x', line_y=None, line_x=None):
    def transform(poly):
        if axis == 'x':
            return tuple((x, -y) for (x,y) in poly)
        elif axis == 'y':
            return tuple((-x, y) for (x,y) in poly)
        return poly
    return transform

def tr_homothety(k, cx=0, cy=0):
    return lambda poly: tuple((cx + (x-cx)*k, cy + (y-cy)*k) for (x,y) in poly)

def cross(o, a, b):
    return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

def is_convex(poly):
    if len(poly) < 3:
        return False
    n = len(poly)
    prev = cross(poly[-2], poly[-1], poly[0])
    for i in range(n):
        cur = cross(poly[i-1], poly[i], poly[(i+1)%n])
        if cur * prev < 0:
            return False
        prev = cur
    return True

def flt_convex_polygon(polygons):
    return filter(is_convex, polygons)

def polygon_area(poly):
    if len(poly) < 3:
        return 0
    s = 0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1)%n]
        s += x1*y2 - x2*y1
    return 0.5 * abs(s)

def flt_square(polygons, max_area):
    return filter(lambda p: polygon_area(p) < max_area, polygons)

def flt_short_side(polygons, max_len):
    def shortest_side(poly):
        n = len(poly)
        min_len = float('inf')
        for i in range(n):
            x1,y1 = poly[i]
            x2,y2 = poly[(i+1)%n]
            length = math.hypot(x2-x1, y2-y1)
            if length < min_len:
                min_len = length
        return min_len
    return filter(lambda p: shortest_side(p) < max_len, polygons)

def flt_angle_point(polygons, point):
    def has_angle_at_point(poly):
        for v in poly:
            if math.hypot(v[0]-point[0], v[1]-point[1]) < 1e-7:
                return True
        return False
    return filter(has_angle_at_point, polygons)

def flt_point_inside(polygons, point):
    def point_in_poly(poly):
        if not is_convex(poly):
            return False
        n = len(poly)
        for i in range(n):
            if cross(poly[i], poly[(i+1)%n], point) < 0:
                return False
        return True
    return filter(point_in_poly, polygons)

def flt_polygon_angles_inside(polygons, target_poly):
    target_points = set(target_poly)
    def has_angle_inside(poly):
        for pt in target_points:
            for p in poly:
                if math.hypot(p[0]-pt[0], p[1]-pt[1]) < 1e-7:
                    return True
        return False
    return filter(has_angle_inside, polygons)

def flt_convex_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return flt_convex_polygon(result)
    return wrapper

def tr_translate_decorator(dx, dy):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            polygons = func(*args, **kwargs)
            return map(tr_translate(dx, dy), polygons)
        return wrapper
    return decorator

def agr_origin_nearest(polygons):
    poly_list = list(polygons)
    min_dist = float('inf')
    min_point = None
    min_poly = None
    for poly in poly_list:
        for x,y in poly:
            dist = math.hypot(x,y)
            if dist < min_dist:
                min_dist = dist
                min_point = (x,y)
                min_poly = poly
    return min_point, min_poly

def agr_max_side(polygons):
    poly_list = list(polygons)
    max_len = -1
    max_idx = -1
    max_poly = None
    for poly in poly_list:
        n = len(poly)
        for i in range(n):
            x1,y1 = poly[i]
            x2,y2 = poly[(i+1)%n]
            length = math.hypot(x2-x1, y2-y1)
            if length > max_len:
                max_len = length
                max_idx = i
                max_poly = poly
    return max_len, max_idx, max_poly

def agr_min_area(polygons):
    poly_list = list(polygons)
    min_area = float('inf')
    min_poly = None
    for poly in poly_list:
        area = polygon_area(poly)
        if area < min_area:
            min_area = area
            min_poly = poly
    return min_area, min_poly

def agr_perimeter(polygons):
    total = 0.0
    for poly in polygons:
        n = len(poly)
        for i in range(n):
            x1,y1 = poly[i]
            x2,y2 = poly[(i+1)%n]
            total += math.hypot(x2-x1, y2-y1)
    return total

def agr_area(polygons):
    total = 0.0
    for poly in polygons:
        total += polygon_area(poly)
    return total

def zip_polygons(iterator1, iterator2):
    for p1, p2 in zip(iterator1, iterator2):
        yield tuple(list(p1) + list(p2))

if __name__ == "__main__":
    print("=== ГЕНЕРАЦИЯ ВСЕХ ВИЗУАЛИЗАЦИЙ ===\n")
    
    print("1. Три параллельные ленты под острым углом...")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    lena1 = list(itertools.islice(gen_triangle(1.2, 0.5, 0.8, 0.8, (0,0)), 5))
    lena2 = list(itertools.islice(gen_triangle(1.2, 0.5, 0.8, 0.8, (0,1.2)), 5))
    lena3 = list(itertools.islice(gen_triangle(1.2, 0.5, 0.8, 0.8, (0,2.4)), 5))
    visualize_polygons(itertools.chain(lena1, lena2, lena3), "Три параллельные ленты под углом", ax=ax1)
    
    print("2. Две пересекающиеся ленты...")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    cross1 = list(itertools.islice(gen_triangle(1.2, 0.6, 0.8, 0.8, (1,0)), 4))
    cross2 = list(itertools.islice(gen_triangle(1.2, -0.6, 0.8, 0.8, (0,2)), 4))
    visualize_polygons(itertools.chain(cross1, cross2), "Две пересекающиеся ленты", ax=ax2)
    
    print("3. Симметричные ленты треугольников...")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sym1 = list(itertools.islice(gen_triangle(1.2, 0.6, 0.8, 0.8, (0,0)), 5))
    sym2_gen = itertools.islice(gen_triangle(1.2, 0.6, 0.8, 0.8, (0,-1.5)), 5)
    sym2 = list(map(tr_symmetry(axis='x'), sym2_gen))
    visualize_polygons(itertools.chain(sym1, sym2), "Симметричные ленты треугольников", ax=ax3)
    
    print("4. Четырёхугольники в разном масштабе...")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    quads = []
    for k in [0.5, 0.8, 1.0, 1.3, 1.6, 2.0]:
        quad = ((k, 0.5*k), (k*1.5, 0.3*k), (k*1.2, -0.4*k), (k*0.7, -0.2*k))
        quads.append(quad)
    visualize_polygons(quads, "Четырёхугольники в разном масштабе", ax=ax4)
    
    print("5. Семь фигур трёх типов...")
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    rect_gen = gen_rectangle(1.5, 0, 1, 1)
    tri_gen = gen_triangle(1.5, 0.8, 1, 1)
    hex_gen = gen_hexagon(1.8, 0, 0.6)
    seven_shapes = list(itertools.islice(rect_gen, 3)) + list(itertools.islice(tri_gen, 3)) + [next(hex_gen)]
    visualize_polygons(seven_shapes, "7 фигур (прямоугольники, треугольники, шестиугольник)", ax=ax5)
    
    print("\n=== РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ И АГРЕГАЦИИ ===")
    test_polys = [
        ((0,0),(2,0),(2,2),(0,2)),
        ((0,0),(1,0),(0,1)),
        ((0,0),(2,0),(1,1),(0,1))
    ]
    filtered = list(flt_convex_polygon(flt_square(test_polys, 1.0)))
    print(f"Отфильтровано (выпуклые+площадь<1.0): {len(filtered)} полигонов")
    
    polys_for_aggr = [
        ((0,0),(1,0),(0.5,0.8)),
        ((1,1),(2,1),(1.5,1.8)),
        ((-1,-1),(0,-1),(-0.5,-0.2))
    ]
    nearest_pt, _ = agr_origin_nearest(polys_for_aggr)
    print(f"Ближайшая к (0,0) точка: {nearest_pt}")
    
    max_len, _, _ = agr_max_side(polys_for_aggr)
    print(f"Максимальная сторона: {max_len:.3f}")
    
    min_a, _ = agr_min_area(polys_for_aggr)
    print(f"Минимальная площадь: {min_a:.3f}")
    
    print(f"Суммарный периметр: {agr_perimeter(polys_for_aggr):.3f}")
    print(f"Суммарная площадь: {agr_area(polys_for_aggr):.3f}")
    
    print("\n=== ДЕМОНСТРАЦИЯ zip_polygons ===")
    rects = gen_rectangle(1.5, 0, 0.8, 0.8, (0,0))
    tris = gen_triangle(1.5, 0, 0.8, 0.8, (0,0.5))
    zipped = list(itertools.islice(zip_polygons(rects, tris), 3))
    print(f"Склеено {len(zipped)} полигонов")
    for i, p in enumerate(zipped):
        print(f"  Полигон {i+1}: {len(p)} вершин")
    
    print("\n✓ Все задания выполнены! Закройте окна с графиками...")
    plt.show()
