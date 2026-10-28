# MacBook Pro 14" M5 세로 거치용 환기구 먼지 덮개 (2조각, 겹친 다리 + 스냅 후크 이음, H자 탭)
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd dust_cover.py
# 좌표: X = 힌지 방향(길이), Y = 맥북 두께 방향(0 = 화면 뒷면 쪽, T = 밑판 쪽), Z = 위(맥북 윗면 = 0)
# 출력 방향: 바깥 둥근 끝면을 베드에 대고 세운다(왼쪽 조각은 +X, 오른쪽 조각은 -X 방향으로 쌓임).
#   쌓는 방향과 나란한 면은 서포트가 필요 없고, 안쪽 다리의 경사는 45°를 넘지 않게 하고, 홀은 원형으로 한다.
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
ROOF_T = 3.0         # 지붕 두께
ROOF_OVERHANG = 6.0  # 다리 바깥으로 내민 지붕 처마
CLEAR = 0.6          # 맥북과 다리 사이 여유
WALL = 2.4           # 다리(스커트) 두께
# H자 탭: 다리 두 장(기둥) + 얇은 가로대. 바깥 탭은 다리가 깊고, 안쪽 탭은 이음선에서 둥글게 이어지는 다리
SKIRT_DEPTH = 14.0   # 바깥 탭 다리가 맥북 윗면 아래로 내려가는 길이
TAB = 15.0           # 바깥 탭의 X 방향 길이
INNER_DEPTH = 6.0    # 안쪽 탭 다리가 이음선에서 맥북 윗면 아래로 내려가는 길이
SEAM_R = 12.0        # 이음선에서 두 안쪽 다리의 바닥을 잇는 원호 반지름 (클수록 완만. 쌓는 각도 때문에 원호 뒤는 45° 직선으로 이어진다)
LEG_R = 3.0          # 바깥 탭 다리 아래 모서리 라운드
BAR_R = 1.5          # 바깥 탭 가로대 끝 모서리 라운드 (가로대 두께의 절반 이하)
BAR_T = 4.0          # 가로대 두께(높이)
BAR_HOLE_D = 8.0     # 가로대 원형 홀 지름 (축이 Z: 맥북 환기구 쪽에서 위로 공기가 통한다)
SKIRT_HOLE_D = 7.0   # 다리 원형 창 지름 (축이 Y: 앞뒤로 공기가 통한다)
SKIRT_HOLE_Z = 10.0  # 다리 원형 창 중심 높이 (맥북 윗면 위)
SEAM_CLEAR = 0.05    # 이음선에서 두 조각 사이 틈, 겹친 다리와 바깥 판·지붕 사이 여유 (겹친 다리가 안 들어가면 0.1)
# 이음선 아래 고정: 오른쪽 안쪽 다리(혀)가 이음선을 넘어 왼쪽 바깥 판 안쪽으로 겹치고, 혀 끝 바깥면의 턱이 바깥 판 안쪽 면의 막힌 홈에 걸린다 (영구 결합)
# 길이 방향으로 밀어 넣으면 턱의 45° 경사가 혀를 안쪽으로 휘게 했다가 홈에서 딸깍 걸린다. 턱은 다리 높이 가운데에만 있어 홈의 위아래 벽이 위아래 움직임을 막는다
LAP = 16.0           # 오른쪽 혀가 이음선을 넘어 겹치는 길이 (= 휘는 팔 길이. 짧으면 혀 뿌리가 갈라진다)
HOOK_H = 0.6         # 턱이 혀 바깥면에서 튀어나온 높이 (= 끼울 때 혀가 휘는 양. 홈 깊이는 HOOK_H + SEAM_CLEAR)
HOOK_LEN = 3.0       # 턱의 X 방향 길이 (네모 턱. 이음선 쪽 면이 90° 걸쇠 면)
HOOK_Z = 8.5         # 턱 중심 높이 (가로대 위, 지붕 아래)
HOOK_ZH = 5.0        # 턱 높이 (Z). 위아래는 혀가 평평하게 남아 홈 벽에 걸린다
HOOK_ROOT_R = 1.0    # 혀 뿌리(오른쪽 바깥 판과 만나는 안쪽 모서리) 라운드
HOOK_LEAD = 1.0      # 왼쪽 바깥 판 끝 안쪽 모서리의 45° 모따기 (네모 턱이 이 경사를 타고 혀를 휘게 한다. 턱 높이보다 커야 한다. 혀 뿌리 라운드도 이 자리에 들어간다)
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
OUTER_Y = ((-CLEAR - 2 * WALL, -CLEAR - WALL), (LAPTOP_T + CLEAR + WALL, LAPTOP_T + CLEAR + 2 * WALL))  # 안쪽 탭 다리 바깥에 덧댄 판
K45 = 0.70710678                            # cos45°
INNER_TAB = (ARCH_TOP + INNER_DEPTH) + SEAM_R * (2 * K45 - 1)   # 안쪽 탭의 X 방향 길이: 원호(수평 접선)+45° 직선이 지붕에 닿는 거리
LUG_Z0 = -INNER_DEPTH + SEAM_R * (1 - K45) + (LAP + SEAM_CLEAR - K45 * SEAM_R)   # 혀 아랫면(수평): 혀 끝에서 안쪽 다리 45° 선의 높이. 이 아래는 왼쪽 안쪽 겹·가로대가 그대로 남는다


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


def under_arch(x0, x1, shrink):
    """지붕 안쪽면 아래 공간(아치 원기둥). shrink만큼 지붕에서 떨어뜨린다."""
    return Part.makeCylinder(ARCH_R - shrink, x1 - x0, Vector(x0, YM, ARCH_ZC), Vector(1, 0, 0))


def fillet_y(shape, radius, z_ok):
    """Y 방향과 나란한 모서리 중 높이가 z_ok(z)인 것에 라운드를 준다. 실패하면 알리고 모양을 그대로 둔다."""
    edges = [e for e in shape.Edges
             if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) < 1e-6
             and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) < 1e-6
             and z_ok(e.Vertexes[0].Point.z)]
    try:
        return shape.makeFillet(radius, edges) if edges else shape
    except Exception as err:
        print("WARN fillet 실패 R=%.1f: %s" % (radius, err))
        return shape


def fuse(parts):
    s = parts[0]
    for p in parts[1:]:
        s = s.fuse(p)
    return s.removeSplitter()


def tab(x0, x1, depth):
    """바깥 탭: H자(다리 두 장 + 가로대). 다리 아래 모서리와 가로대 끝은 둥글고, 다리에 원형 창, 가로대에 원형 홀이 있다."""
    xm = (x0 + x1) / 2.0
    parts = []
    for ya, yb in SKIRT_Y:
        s = fillet_y(box(x0, x1, ya, yb, -depth, ARCH_TOP), LEG_R, lambda z: z < -depth + 0.5)
        s = s.cut(Part.makeCylinder(SKIRT_HOLE_D / 2.0, yb - ya + 2, Vector(xm, ya - 1, SKIRT_HOLE_Z), Vector(0, 1, 0)))
        parts.append(s)
    bar = fillet_y(box(x0, x1, SKIRT_Y[0][0], SKIRT_Y[1][1], PAD_T, BAR_TOP), BAR_R, lambda z: True)
    parts.append(bar.cut(Part.makeCylinder(BAR_HOLE_D / 2.0, BAR_T + 2, Vector(xm, LAPTOP_T / 2.0, PAD_T - 1), Vector(0, 0, 1))))
    return fuse(parts)


def leg_prism(seam_x, side):
    """안쪽 다리의 옆모습(XZ)을 Y 방향으로 길게 뽑은 기둥. 이음선(seam_x)에서 side(-1 왼쪽, +1 오른쪽)로 뻗는다.
    바닥은 이음선 바로 아래를 중심으로 한 반지름 SEAM_R 원호(이음선에서 수평 접선)라 반대쪽 조각의 원호와
    한 곡선처럼 이어지고, 원호 뒤는 45° 접선 직선으로 지붕까지 올라간다(쌓을 때 서포트가 필요 없는 한계 각도)."""
    zb = -INNER_DEPTH

    def p(u, z):
        return Vector(seam_x + side * u, -20, z)

    t = (K45 * SEAM_R, zb + SEAM_R * (1 - K45))                        # 원호와 45° 직선의 접점
    m = (SEAM_R * 0.38268343, zb + SEAM_R * (1 - 0.92387953))          # 원호 중간점(22.5°)
    u0 = t[0] + (ARCH_TOP - t[1])                                      # 지붕 높이에서 직선의 끝
    edges = [Part.LineSegment(p(0, zb), p(0, ARCH_TOP)).toShape(),
             Part.LineSegment(p(0, ARCH_TOP), p(u0, ARCH_TOP)).toShape(),
             Part.LineSegment(p(u0, ARCH_TOP), p(*t)).toShape(),
             Part.Arc(p(*t), p(*m), p(0, zb)).toShape()]
    return Part.Face(Part.Wire(edges)).extrude(Vector(0, 60, 0))


def inner_tab(seam_x, side):
    """이음선 쪽 안쪽 탭: 다리 두 장(바깥 판을 덧대 두 겹) + 가로대를 leg_prism 모양으로 깎은 것. 가로대에 이음선을 중심으로 한 원형 홀(조각마다 반원)이 있다."""
    x0, x1 = (seam_x - INNER_TAB, seam_x) if side < 0 else (seam_x, seam_x + INNER_TAB)
    parts = [box(x0, x1, ya, yb, -INNER_DEPTH, ARCH_TOP) for ya, yb in SKIRT_Y + OUTER_Y]
    parts.append(box(x0, x1, SKIRT_Y[0][0], SKIRT_Y[1][1], PAD_T, BAR_TOP))
    hole = Part.makeCylinder(BAR_HOLE_D / 2.0, BAR_T + 2, Vector(XJ + SEAM_CLEAR / 2.0, LAPTOP_T / 2.0, PAD_T - 1), Vector(0, 0, 1))
    return fuse(parts).common(leg_prism(seam_x, side)).cut(hole)


def outline(x0, x1, round_at_x0):
    """평면 윤곽: 바깥 끝(round_at_x0 ? x0 : x1)의 두 모서리를 CORNER_R로 둥글게 한 판.
    베드에 닿는 끝에서 곡선이 45°보다 가파르면 서포트가 필요하므로, 반지름 R 곡선의 45° 지점에서 끝을 잘라
    (R*(1-cos45°)만큼 바깥으로 늘렸다가 x0/x1에서 자른다) 곡선이 45°로 시작하게 한다."""
    cut = CORNER_R * (1.0 - K45)
    bx0, bx1 = (x0 - cut, x1) if round_at_x0 else (x0, x1 + cut)
    p = box(bx0, bx1, Y0, Y1, -SKIRT_DEPTH - 1, ROOF_TOP + 2)
    edge_x = bx0 if round_at_x0 else bx1
    edges = [e for e in p.Edges
             if abs(e.Vertexes[0].Point.x - edge_x) < 1e-6 and abs(e.Vertexes[1].Point.x - edge_x) < 1e-6
             and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
    return p.makeFillet(CORNER_R, edges) if CORNER_R > 0 else p


def hook(face, s):
    """혀 바깥면(face)에서 s쪽(-1 앞, +1 뒤)으로 HOOK_H 튀어나온 네모 턱. 혀 끝에 붙고, 이음선 쪽 면이 90° 걸쇠 면이다."""
    ya, yb = sorted((face, face + s * HOOK_H))
    return box(XJ - LAP, XJ - LAP + HOOK_LEN, ya, yb, HOOK_Z - HOOK_ZH / 2.0, HOOK_Z + HOOK_ZH / 2.0)


def hook_pocket(face, s):
    """왼쪽 바깥 판 안쪽 면의 막힌 홈: 턱보다 사방 SEAM_CLEAR 크다 (안쪽으로 1mm 더 늘려 혀 자리 빈 곳과 이어 붙인다)."""
    ya, yb = sorted((face - s * 1.0, face + s * (HOOK_H + 2 * SEAM_CLEAR)))
    z0 = HOOK_Z - HOOK_ZH / 2.0 - SEAM_CLEAR
    return box(XJ - LAP - SEAM_CLEAR, XJ - LAP + HOOK_LEN + SEAM_CLEAR, ya, yb, z0, z0 + HOOK_ZH + 2 * SEAM_CLEAR)


def root_fillet(face, s):
    """혀 뿌리 안쪽 모서리(이음선 x, 혀 바깥면 face)를 채우는 반지름 HOOK_ROOT_R 라운드 조각."""
    xs = XJ + SEAM_CLEAR
    xc, yc = xs - HOOK_ROOT_R, face + s * HOOK_ROOT_R
    ya, yb = sorted((face, yc))
    sq = box(xc, xs, ya, yb, LUG_Z0, ARCH_TOP)
    return sq.cut(Part.makeCylinder(HOOK_ROOT_R, ARCH_TOP - LUG_Z0 + 2, Vector(xc, yc, LUG_Z0 - 1), Vector(0, 0, 1)))


def lead_in(plate_face, s):
    """왼쪽 바깥 판 끝(이음선) 안쪽 모서리를 HOOK_LEAD 크기 45°로 깎아낼 삼각 기둥. plate_face는 바깥 판 안쪽 면, s는 바깥쪽."""
    pts = [(XJ - HOOK_LEAD - 0.5, plate_face - s * 0.5), (XJ + 1, plate_face - s * 0.5), (XJ + 1, plate_face + s * (HOOK_LEAD + 1)),
           (XJ - HOOK_LEAD - 0.5, plate_face - s * 0.5)]
    w = Part.makePolygon([Vector(x, y, LUG_Z0 - SEAM_CLEAR) for x, y in pts])
    return Part.Face(w).extrude(Vector(0, 0, ARCH_TOP - LUG_Z0 + SEAM_CLEAR))


def left_piece():
    parts = [roof(0, XJ)]
    parts.append(tab(0, TAB, SKIRT_DEPTH))
    (fa, fb), (ba, bb) = SKIRT_Y
    # 혀 아랫면(LUG_Z0) 위로만 안쪽 겹을 비운다. 그 아래 안쪽 겹과 가로대는 그대로 남는다
    notch = box(XJ - LAP - SEAM_CLEAR, XJ + 1, fa, bb, LUG_Z0 - SEAM_CLEAR, ARCH_TOP)
    # 턱이 걸릴 홈과 바깥 판 끝의 45° 모따기도 함께 비운다 (혀 바깥면: 앞 fa + SEAM_CLEAR, 뒤 bb - SEAM_CLEAR / 바깥 판 안쪽 면: 앞 fa, 뒤 bb)
    for face, plate_face, s in ((fa + SEAM_CLEAR, fa, -1), (bb - SEAM_CLEAR, bb, 1)):
        notch = notch.fuse(hook_pocket(face, s)).fuse(lead_in(plate_face, s))
    notch = notch.common(under_arch(XJ - LAP - 1, XJ + 1, 0))
    parts.append(inner_tab(XJ, -1).cut(notch))   # 오른쪽 혀가 들어올 자리(안쪽 겹·홈·모따기)를 비운다
    return fuse(parts).common(outline(0, XJ, True))


def right_piece():
    x_start = XJ + SEAM_CLEAR
    parts = [roof(x_start, TOTAL_LEN)]
    parts.append(inner_tab(x_start, +1))
    # 이음선을 넘어 왼쪽 조각 바깥 판 안쪽으로 들어가는 혀 (바깥 판·지붕 쪽으로 SEAM_CLEAR 여유). 아랫면은 LUG_Z0에서 수평, 끝 바깥면에 네모 턱, 뿌리에 라운드.
    # 오른쪽 조각을 길이 방향으로 밀어 넣으면 턱이 바깥 판 끝 모따기를 타고 혀를 안쪽으로 휘게 했다가 홈에 걸린다
    (fa, fb), (ba, bb) = SKIRT_Y
    for (ya, yb), face, s in (((fa + SEAM_CLEAR, fb), fa + SEAM_CLEAR, -1), ((ba, bb - SEAM_CLEAR), bb - SEAM_CLEAR, 1)):
        lug = fuse([box(XJ - LAP, x_start, ya, yb, LUG_Z0, ARCH_TOP), hook(face, s), root_fillet(face, s)])
        parts.append(lug.common(under_arch(XJ - LAP, x_start, SEAM_CLEAR)))
    parts.append(tab(TOTAL_LEN - TAB, TOTAL_LEN, SKIRT_DEPTH))
    return fuse(parts).common(outline(XJ - LAP, TOTAL_LEN, False))


def export(shape, name):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.1)
    path = os.path.join(OUT_DIR, name)
    mesh.write(path)
    print("wrote", path, "volume=%.1f mm3" % shape.Volume)


export(left_piece(), "cover-left.stl")
export(right_piece(), "cover-right.stl")
