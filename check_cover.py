# cover-left.stl / cover-right.stl 기하 검증. PASS/FAIL 줄만 판정에 쓴다.
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd check_cover.py
# 출력 방향 가정: 바깥 둥근 끝면을 베드에 대고 세운다 (왼쪽 조각은 +X, 오른쪽 조각은 -X 방향으로 쌓임).
import os
import sys
import Mesh
import Part
from FreeCAD import Placement, Rotation, Vector

DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
BED = 250.0                  # X1C 256mm에서 여유 6mm
LAPTOP_T = 15.5
GAP_RANGE = (10.0, 15.0)
OVERHANG_SIN = 0.72          # 45°(sin=0.707)보다 가파르게 내려다보는 면은 서포트가 필요하다
PATCH_LIMIT = 45.0           # 서포트가 필요한 면 덩어리 하나의 허용 면적 mm² (원형 홀 꼭대기 호는 이보다 작다)
results = []


def report(tag, ok, msg):
    results.append(ok)
    print("%s (%s) %s" % ("PASS" if ok else "FAIL", tag, msg))
    sys.stdout.flush()


def load(name):
    m = Mesh.Mesh(os.path.join(DIR, name))
    s = Part.Shape()
    s.makeShapeFromMesh(m.Topology, 0.01)
    return m, Part.Solid(Part.Shell(s.Faces))


def slab(x0, x1):
    return Part.makeBox(x1 - x0, 200, 200, Vector(x0, -100, -100))


def overhang_patch(m, bed_x, d):
    """쌓는 방향 d(+1/-1, X축)에서 서포트가 필요한 면(오버행 >45°, 베드 접촉면 제외)을 이웃끼리 묶어 가장 큰 덩어리 면적을 돌려준다."""
    parent = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    flagged = []
    for f in m.Facets:
        idx = f.PointIndices
        if all(abs(m.Points[i].x - bed_x) < 0.05 for i in idx):
            continue
        if -f.Normal.x * d > OVERHANG_SIN:
            flagged.append((idx, f.Area))
            for i in idx:
                parent.setdefault(i, i)
    for idx, _ in flagged:
        for i in idx[1:]:
            parent[find(i)] = find(idx[0])
    area = {}
    for idx, a in flagged:
        r = find(idx[0])
        area[r] = area.get(r, 0.0) + a
    return max(area.values()) if area else 0.0


try:
    ml, L = load("cover-left.stl")
    mr, R = load("cover-right.stl")
except Exception as e:
    print("FAIL (load) %s" % e)
    sys.stdout.flush()
    raise SystemExit(1)

lb, rb = L.BoundBox, R.BoundBox
# 이음선 = 오른쪽 지붕이 시작하는 곳 (오른쪽 다리는 이음선을 넘어 왼쪽으로 겹치므로 rb.XMin이 아니다. 높이 17 위에는 지붕만 있다. 다리 꼭대기는 16.6)
xj = R.common(Part.makeBox(400, 200, 100, Vector(-100, -100, 17.0))).BoundBox.XMin

# (a) 출력 영역 + 서 있는 방향에서 서포트 없이 쌓이는가
dims = [(b.XLength, b.YLength, b.ZLength) for b in (lb, rb)]
pl = overhang_patch(ml, lb.XMin, +1)
pr = overhang_patch(mr, rb.XMax, -1)
report("a", all(max(d) <= BED for d in dims) and pl <= PATCH_LIMIT and pr <= PATCH_LIMIT,
       "bbox L=%.1f×%.1f×%.1f R=%.1f×%.1f×%.1f (한계 %.0f), 서포트 필요 면 최대 덩어리 L=%.1f R=%.1f mm² (허용 %.0f)" % (dims[0] + dims[1] + (BED, pl, pr, PATCH_LIMIT)))

# (b) 간섭과 조립 경로: 제자리에서 간섭 0, 오른쪽 조각을 아래에서 40mm 올리거나 오른쪽에서 20mm 밀어 넣는 동안 어디서도 걸리지 않아야 한다
inter = L.common(R).Volume
def path_hit(v):
    s = R.copy()
    s.translate(v)
    return L.common(s).Volume

path_up = max(path_hit(Vector(0, 0, -dz)) for dz in range(1, 41))
path_slide = max(path_hit(Vector(dx, 0, 0)) for dx in range(1, 21))
report("b", inter < 1e-3 and path_up < 1e-3 and path_slide < 1e-3,
       "간섭 부피 %.4fmm3, 조립 경로 간섭 아래에서 %.4f / 옆에서 %.4fmm3" % (inter, path_up, path_slide))

# (c) 지붕 간격, 사방 개방, 다리 없음, 처마가 맥북 두께를 덮음, 바깥 탭의 원형 홀(가로대 홀·다리 창)이 뚫려 있음
mid_l = slab(lb.XMin + 20, lb.XMin + 85)
mid_r = slab(rb.XMax - 85, rb.XMax - 20)
ok_c = True
detail = []
for name, S, mid, b in (("L", L, mid_l, lb), ("R", R, mid_r, rb)):
    part = S.common(mid)
    zmin = part.BoundBox.ZMin
    below = S.common(Part.makeBox(mid.BoundBox.XLength, 200, 100 + (GAP_RANGE[0] - 0.5), Vector(mid.BoundBox.XMin, -100, -100))).Volume
    covers = b.YMin < 0 and b.YMax > LAPTOP_T
    xc = b.XMin + 7.5 if name == "L" else b.XMax - 7.5          # 바깥 탭 중심
    bar_hole = S.common(Part.makeBox(4, 4, 10.5, Vector(xc - 2, LAPTOP_T / 2 - 2, 0.5))).Volume       # 가로대 홀(Z 축)
    win = sum(S.common(Part.makeBox(3, 2.8, 2, Vector(xc - 1.5, y0, 9))).Volume for y0 in (-3.2, LAPTOP_T + 0.4))  # 다리 창(Y 축)
    detail.append("%s 간격 %.1f 하부부피 %.3f 덮음 %s 홀막힘 %.3f/%.3f" % (name, zmin, below, covers, bar_hole, win))
    ok_c = ok_c and GAP_RANGE[0] <= zmin <= GAP_RANGE[1] and below < 1e-3 and covers and bar_hole < 1e-3 and win < 1e-3
# 이음선 양쪽의 안쪽 탭 다리가 맞붙는지(이음선 3mm 안쪽, 맥북 윗면 아래 Z -5~-1에 양쪽 다리 재료가 있어야 한다)
legs = []
for S, x0, ys in ((L, xj - 3.0, (-5.4, LAPTOP_T + 3.0)), (R, xj, (-3.0, LAPTOP_T + 0.6))):   # 왼쪽은 이음선 쪽에서 바깥 판만 남는다
    legs.append(sum(S.common(Part.makeBox(3.0, 2.0, 4.0, Vector(x0, y0 + 0.2, -5.0))).Volume for y0 in ys))   # 판 면과 겹치는 면이 생기지 않게 0.2 들여 잰다(메시 불리언이 한쪽을 놓친 적 있음)
seam_hole = sum(S.common(Part.makeBox(4, 4, 10.5, Vector(xj - 2, LAPTOP_T / 2 - 2, 0.5))).Volume for S in (L, R))  # 이음선 가로대 홀(Z 축)
ok_c = ok_c and min(legs) > 1.0 and seam_hole < 1e-3
detail.append("이음선 다리 부피 L=%.1f R=%.1f 이음선 홀막힘 %.3f" % (legs[0], legs[1], seam_hole))
report("c", ok_c, "; ".join(detail))

# (e) 고정 나사: M3 × 10 접시머리 나사(머리 Ø6 90°, 심 Ø2.4 = 골지름)를 앞뒤 바깥 판에 박았을 때 머리가 접시 자리에 들어가고 심이 구멍을 지나가며(간섭 0),
#     나사를 왼쪽 조각에 고정한 채 오른쪽 조각을 6방향으로 0.5mm 옮기거나 나사 축을 경첩 삼아 ±1° 꺾으면 왼쪽 조각이나 나사에 걸린다
pin = None
for y, d in ((-5.4, 1), (LAPTOP_T + 5.4, -1)):
    head = Part.makeCone(3.0, 0, 3.0, Vector(xj - 4.05, y, 8.5), Vector(0, d, 0)).common(Part.makeBox(10, 1.75, 10, Vector(xj - 9.05, y if d > 0 else y - 1.75, 3.5)))
    screw = head.fuse(Part.makeCylinder(1.2, 10, Vector(xj - 4.05, y, 8.5), Vector(0, d, 0)))
    pin = screw if pin is None else pin.fuse(screw)
def blocked(pl):
    s = R.copy()
    s.Placement = pl
    return L.common(s).Volume + pin.common(s).Volume

pin_free = pin.common(L).Volume + pin.common(R).Volume
moves = [Placement(Vector(*v), Rotation()) for v in ((0.5, 0, 0), (-0.5, 0, 0), (0, 0.5, 0), (0, -0.5, 0), (0, 0, 0.5), (0, 0, -0.5))]
moves += [Placement(Vector(), Rotation(Vector(0, 1, 0), deg), Vector(xj - 4.05, 0, 8.5)) for deg in (1.0, -1.0)]
pin_lock = min(blocked(pl) for pl in moves)
report("e", pin_free < 1e-3 and pin_lock > 0.01, "나사 간섭 %.4fmm3, 이동·꺾임 8가지 중 가장 약한 걸림 %.3fmm3" % (pin_free, pin_lock))

# (d) 닫힌 솔리드
report("d", ml.isSolid() and mr.isSolid() and L.isValid() and R.isValid() and ml.countComponents() == 1 and mr.countComponents() == 1, "isSolid L=%s R=%s, 덩어리 L=%d R=%d" % (ml.isSolid(), mr.isSolid(), ml.countComponents(), mr.countComponents()))

sys.stdout.flush()
raise SystemExit(0 if all(results) else 1)
