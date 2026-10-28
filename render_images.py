# README용 이미지를 FreeCAD 화면에서 캡처한다 (cover-left.stl / cover-right.stl 필요).
# 실행: /Applications/FreeCAD.app/Contents/MacOS/FreeCAD render_images.py   (GUI가 잠깐 열렸다 닫힌다)
import os
import FreeCAD
import FreeCADGui as Gui
import Mesh
from FreeCAD import Placement, Rotation, Vector

DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
OUT = os.path.join(DIR, "images")
os.makedirs(OUT, exist_ok=True)
BLUE = (0.30, 0.55, 0.90)
ORANGE = (0.95, 0.60, 0.20)
doc = FreeCAD.newDocument("render")


def load(name, color, placement=None):
    Mesh.insert(os.path.join(DIR, name), "render")
    obj = doc.Objects[-1]
    obj.ViewObject.ShapeColor = color
    if placement:
        obj.Placement = placement
    return obj


def shot(name, view, objs, size=(1600, 1000)):
    v = Gui.activeDocument().activeView()
    getattr(v, view)()
    Gui.SendMsgToActiveView("ViewFit")
    path = os.path.join(OUT, name)
    v.saveImage(path, size[0], size[1], "White")
    for o in objs:
        doc.removeObject(o.Name)
    print("saved", path)


def pair(left_pl=None, right_pl=None):
    return [load("cover-left.stl", BLUE, left_pl), load("cover-right.stl", ORANGE, right_pl)]


# 1) 조립한 모습 (위에서 비스듬히)
shot("assembled-iso.png", "viewIsometric", pair())
# 2) 아래에서 본 모습: 전체를 X축으로 180° 돌려 놓고 같은 각도로 본다 (H자 탭, 원형 홀, 이음선 다리)
flip = Placement(Vector(0, 0, 0), Rotation(Vector(1, 0, 0), 180))
shot("assembled-under.png", "viewIsometric", pair(flip, flip))
# 3) 옆에서 본 모습 (V자로 이어지는 안쪽 다리)
shot("side-view.png", "viewFront", pair())
# 4) 위에서 본 모습 (이음선)
shot("top-view.png", "viewTop", pair())
# 5) 출력 방향: 둥근 바깥 끝을 베드에 대고 세운다 (왼쪽은 +X, 오른쪽은 -X 방향으로 쌓임)
left_pl = Placement(Vector(0, 0, 0), Rotation(Vector(0, 1, 0), -90))
right_pl = Placement(Vector(0, 60, 272), Rotation(Vector(0, 1, 0), 90))
shot("print-orientation.png", "viewIsometric", pair(left_pl, right_pl))
# 6) 조립: 오른쪽 조각을 길이 방향으로 밀어 넣으면 혀 끝 턱이 홈에 걸린다 (오른쪽으로 30mm 띄운 모습)
shot("assembly-exploded.png", "viewIsometric", pair(None, Placement(Vector(30, 0, 0), Rotation())))
os._exit(0)
