# MacBook Pro 14" M5 세로 거치용 환기구 먼지 덮개 (2조각, 도브테일 이음, H자 탭)
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd dust_cover.py
# 좌표: X = 힌지 방향(길이), Y = 맥북 두께 방향(0 = 화면 뒷면 쪽, T = 밑판 쪽), Z = 위(맥북 윗면 = 0)
# 출력 방향: 바깥 둥근 끝면을 베드에 대고 세운다(왼쪽 조각은 +X, 오른쪽 조각은 -X 방향으로 쌓임).
#   쌓는 방향과 나란한 면은 서포트가 필요 없고, 안쪽 탭의 앞쪽 끝은 45°로 깎고, 홀은 원형으로 한다.
import os
import FreeCAD
import Part
import MeshPart
from FreeCAD import Vector

# ---- 파라미터 (mm). 시험 출력 후 여기만 고친다 ----
LAPTOP_T = 15.5      # 맥북 두께 (Apple 공식 15.5)
TOTAL_LEN = 272.0    # 덮개 전체 길이 (힌지 띠 추정 240~270 + 여유) [추정]
GAP = 12.0           # 맥북 윗면에서 지붕 안쪽면 가장자리까지 간격 (10~15)
ROOF_RISE = 6.0      # 지붕 가운데가 가장자리보다 높은 정도 (0 = 평평, 클수록 둥글다)
CORNER_R = 8.0       # 덮개 바깥 끝 모서리 둥글기 (평면에서 본 모양)
PAD_T = 1.0          # 가로대 밑에 붙일 펠트/TPU 패드 두께 (GAP에 포함)
ROOF_T = 4.0         # 지붕 두께
ROOF_OVERHANG = 6.0  # 다리 바깥으로 내민 지붕 처마
CLEAR = 0.6          # 맥북과 다리 사이 여유
WALL = 2.4           # 다리(스커트) 두께
# H자 탭: 다리 두 장(기둥) + 얇은 가로대. 바깥 탭은 다리가 깊고, 안쪽 탭은 45°로 깎인 삼각 다리
SKIRT_DEPTH = 14.0   # 바깥 탭 다리가 맥북 윗면 아래로 내려가는 길이
TAB = 15.0           # 바깥 탭의 X 방향 길이
INNER_DEPTH = 6.0    # 안쪽 탭 다리가 맥북 윗면 아래로 내려가는 길이
INNER_TAB = 24.0     # 안쪽 탭의 X 방향 길이 (= GAP+ROOF_RISE+INNER_DEPTH, 45° 경사가 되도록)
BAR_T = 4.0          # 가로대 두께(높이)
BAR_HOLE_D = 8.0     # 가로대 원형 홀 지름 (축이 Z: 맥북 환기구 쪽에서 위로 공기가 통한다)
SKIRT_HOLE_D = 7.0   # 다리 원형 창 지름 (축이 Y: 앞뒤로 공기가 통한다)
SKIRT_HOLE_Z = 10.0  # 다리 원형 창 중심 높이 (맥북 윗면 위)
# 도브테일: 왼쪽 조각의 장부(끝이 넓은 사다리꼴)가 오른쪽 조각의 홈에 끼워진다 (쌓는 방향으로 15° 벌어져 서포트 불필요)
DT_LEN = 19.0        # 장부 길이 = 맞물림 길이 (15~20)
DT_ROOT = 10.0       # 장부 뿌리 폭
DT_FLARE = 3.0       # 끝으로 갈수록 한쪽당 넓어지는 양. 끝 반폭(뿌리/2+FLARE+CLEAR)은 다리 안쪽 면(8.35)보다 작아야 다리가 이음선까지 온다
DT_CLEAR = 0.12      # 장부와 홈 사이 한쪽 여유 (꽉 끼면 0.15, 헐거우면 0.1). 두 조각의 안쪽 다리 사이 틈도 이 값이다
OUT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

XJ = TOTAL_LEN / 2.0                         # 두 조각의 경계
Y0 = -CLEAR - WALL - ROOF_OVERHANG
Y1 = LAPTOP_T + CLEAR + WALL + ROOF_OVERHANG
YM = (Y0 + Y1) / 2.0
W = Y1 - Y0
ARCH_R = (W * W / 4.0 + ROOF_RISE ** 2) / (2.0 * ROOF_RISE) if ROOF_RISE > 0 else 1e9
ARCH_ZC = GAP + ROOF_RISE - ARCH_R          # 아치 중심 높이 (안쪽면이 가장자리에서 GAP, 가운데에서 GAP+RISE)
ROOF_TOP = GAP + ROOF_RISE + ROOF_T
ARCH_TOP = GAP + ROOF_RISE                  # 지붕 안쪽면의 가장 높은 곳 (다리가 지붕에 닿는 높이)
BAR_TOP = PAD_T + BAR_T
SKIRT_Y = ((-CLEAR - WALL, -CLEAR), (LAPTOP_T + CLEAR, LAPTOP_T + CLEAR + WALL))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def roof(x0, x1):
    """아치형 지붕 한 장 (X 방향으로 뽑음)."""
    if ROOF_RISE <= 0:
        return box(x0, x1, Y0, Y1, GAP, GAP + ROOF_T)
    d = Vector(1, 0, 0)
    outer = Part.makeCylinder(ARCH_R + ROOF_T, x1 - x0, Vector(x0, YM, ARCH_ZC), d)
    inner = Part.makeCylinder(ARCH_R, x1 - x0, Vector(x0, YM, ARCH_ZC), d)
    return outer.cut(inner).common(box(x0, x1, Y0, Y1, GAP, ROOF_TOP + 1))


def prism(points_xy):
    """평면 다각형을 Z 방향으로 길게 뽑은 기둥 (지붕과 겹쳐 모양을 자르는 용도)."""
    z0 = -SKIRT_DEPTH - 2.0
    pts = [Vector(x, y, z0) for x, y in points_xy]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return face.extrude(Vector(0, 0, ROOF_TOP + 4.0 - z0))


def dovetail(grow):
    """장부 사다리꼴. grow = 홈 쪽 여유(0이면 장부). 끝(X=XJ+DT_LEN)이 더 넓다."""
    hr = DT_ROOT / 2.0 + grow
    ht = DT_ROOT / 2.0 + DT_FLARE + grow
    xe = XJ + DT_LEN + grow
    return [(XJ - 1.0, YM - hr), (XJ, YM - hr), (xe, YM - ht), (xe, YM + ht), (XJ, YM + hr), (XJ - 1.0, YM + hr)]


def wedge(x0, x1, lead, depth):
    """안쪽 탭 앞쪽 끝을 45°로 깎는 쐐기. lead='low' 면 x0 쪽이, 'high' 면 x1 쪽이 쌓을 때 먼저 올라오는 쪽."""
    z_lo = -depth - 2.0
    if lead == "low":
        pts = [(x0 - 1, ARCH_TOP + 1), (x1 + 1, ARCH_TOP - (x1 + 1 - x0)), (x1 + 1, z_lo), (x0 - 1, z_lo)]
    else:
        pts = [(x1 + 1, ARCH_TOP + 1), (x0 - 1, ARCH_TOP - (x1 + 1 - x0)), (x0 - 1, z_lo), (x1 + 1, z_lo)]
    face = Part.Face(Part.makePolygon([Vector(x, -20, z) for x, z in pts] + [Vector(pts[0][0], -20, pts[0][1])]))
    return face.extrude(Vector(0, 60, 0))


def tab(x0, x1, depth, lead=None, holes=True):
    """H자 탭 하나: 다리 두 장(원형 창) + 가로대(원형 홀). lead가 있으면 안쪽 탭으로 앞쪽 끝을 45°로 깎는다.
    holes=False 면 홀을 뚫지 않는다(가운데 이음선 쪽 안쪽 탭)."""
    xm = (x0 + x1) / 2.0
    parts = []
    for ya, yb in SKIRT_Y:
        s = box(x0, x1, ya, yb, -depth, ARCH_TOP)
        if holes:
            s = s.cut(Part.makeCylinder(SKIRT_HOLE_D / 2.0, yb - ya + 2, Vector(xm, ya - 1, SKIRT_HOLE_Z), Vector(0, 1, 0)))
        parts.append(s)
    bar = box(x0, x1, SKIRT_Y[0][0], SKIRT_Y[1][1], PAD_T, BAR_TOP)
    if holes:
        bar = bar.cut(Part.makeCylinder(BAR_HOLE_D / 2.0, BAR_T + 2, Vector(xm, LAPTOP_T / 2.0, PAD_T - 1), Vector(0, 0, 1)))
    parts.append(bar)
    shape = fuse(parts)
    if lead:
        shape = shape.cut(wedge(x0, x1, lead, depth))
    return shape



def fuse(parts):
    s = parts[0]
    for p in parts[1:]:
        s = s.fuse(p)
    return s.removeSplitter()


def outline(x0, x1, round_at_x0):
    """평면 윤곽: 바깥 끝(round_at_x0 ? x0 : x1)의 두 모서리를 CORNER_R로 둥글게 한 판.
    베드에 닿는 끝에서 곡선이 45°보다 가파르면 서포트가 필요하므로, 반지름 R 곡선의 45° 지점에서 끝을 잘라
    (R*(1-cos45°)만큼 바깥으로 늘렸다가 x0/x1에서 자른다) 곡선이 45°로 시작하게 한다."""
    cut = CORNER_R * (1.0 - 0.70710678)
    bx0, bx1 = (x0 - cut, x1) if round_at_x0 else (x0, x1 + cut)
    p = box(bx0, bx1, Y0, Y1, -SKIRT_DEPTH - 1, ROOF_TOP + 2)
    edge_x = bx0 if round_at_x0 else bx1
    edges = [e for e in p.Edges
             if abs(e.Vertexes[0].Point.x - edge_x) < 1e-6 and abs(e.Vertexes[1].Point.x - edge_x) < 1e-6
             and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
    return p.makeFillet(CORNER_R, edges) if CORNER_R > 0 else p


def left_piece():
    tongue = roof(XJ - 1.0, XJ + DT_LEN).common(prism(dovetail(0.0)))
    parts = [roof(0, XJ), tongue]
    parts.append(tab(0, TAB, SKIRT_DEPTH))
    parts.append(tab(XJ - INNER_TAB, XJ, INNER_DEPTH, "low", holes=False))  # 수직 모서리가 이음선(XJ)에 닿는다
    return fuse(parts).common(outline(0, XJ + DT_LEN, True))


def right_piece():
    x_start = XJ + DT_CLEAR
    roof_part = roof(x_start, TOTAL_LEN).cut(prism(dovetail(DT_CLEAR)))  # 지붕에만 홈을 판다(다리·가로대는 그대로)
    parts = [roof_part]
    parts.append(tab(x_start, x_start + INNER_TAB, INNER_DEPTH, "high", holes=False))  # 수직 모서리가 왼쪽 다리와 맞붙는다
    parts.append(tab(TOTAL_LEN - TAB, TOTAL_LEN, SKIRT_DEPTH))
    return fuse(parts).common(outline(x_start, TOTAL_LEN, False))


def export(shape, name):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.1)
    path = os.path.join(OUT_DIR, name)
    mesh.write(path)
    print("wrote", path, "volume=%.1f mm3" % shape.Volume)


export(left_piece(), "cover-left.stl")
export(right_piece(), "cover-right.stl")
