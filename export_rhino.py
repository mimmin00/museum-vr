import rhino3dm as rh
import math

model = rh.File3dm()

# ── 색상 레이어 생성
def add_layer(name, r, g, b):
    layer = rh.Layer()
    layer.Name = name
    layer.Color = (r, g, b, 255)
    idx = model.Layers.Add(layer)
    return idx

layer_floor = add_layer("Floor", 17, 17, 17)
layer_walls = add_layer("Walls", 18, 18, 16)
layer_ceiling = add_layer("Ceiling", 10, 10, 10)
layer_molding = add_layer("Gold Molding", 154, 125, 74)
layer_pedestal = add_layer("Pedestals", 26, 26, 22)
layer_pedestal_gold = add_layer("Pedestal Gold", 154, 125, 74)
layer_mirror_frame = add_layer("Mirror Frames", 138, 112, 64)
layer_mirror = add_layer("Mirrors", 136, 153, 153)
layer_rug = add_layer("Rug", 15, 14, 10)
layer_grid = add_layer("Floor Grid", 26, 26, 26)
layer_ceil_fixture = add_layer("Ceiling Fixtures", 154, 125, 74)
layer_nameplate = add_layer("Nameplates", 14, 13, 10)

# ── 헬퍼: Box 생성
def add_box(cx, cy, cz, sx, sy, sz, layer_idx):
    """중심점(cx,cy,cz)과 크기(sx,sy,sz)로 박스 생성"""
    x0, y0, z0 = cx - sx/2, cy - sy/2, cz - sz/2
    x1, y1, z1 = cx + sx/2, cy + sy/2, cz + sz/2

    pts = [
        rh.Point3d(x0, y0, z0), rh.Point3d(x1, y0, z0),
        rh.Point3d(x1, y1, z0), rh.Point3d(x0, y1, z0),
        rh.Point3d(x0, y0, z1), rh.Point3d(x1, y0, z1),
        rh.Point3d(x1, y1, z1), rh.Point3d(x0, y1, z1),
    ]
    brep = rh.Brep()

    # Box를 6개의 면으로
    faces = [
        [0,1,2,3], [4,5,6,7],  # bottom, top
        [0,1,5,4], [2,3,7,6],  # front, back
        [0,3,7,4], [1,2,6,5],  # left, right
    ]

    # Mesh로 대체 (더 안정적)
    mesh = rh.Mesh()
    for p in pts:
        mesh.Vertices.Add(p.X, p.Y, p.Z)

    mesh.Faces.AddFace(0,1,2,3)  # bottom
    mesh.Faces.AddFace(4,5,6,7)  # top
    mesh.Faces.AddFace(0,1,5,4)  # front
    mesh.Faces.AddFace(2,3,7,6)  # back
    mesh.Faces.AddFace(0,3,7,4)  # left
    mesh.Faces.AddFace(1,2,6,5)  # right

    mesh.Normals.ComputeNormals()

    attr = rh.ObjectAttributes()
    attr.LayerIndex = layer_idx
    model.Objects.AddMesh(mesh, attr)

# ── 헬퍼: Cylinder 생성 (근사 다각형)
def add_cylinder(cx, cy, cz, radius, height, layer_idx, segments=24):
    """바닥 중심(cx, cy, cz)에서 위로 height만큼"""
    mesh = rh.Mesh()

    # 아래 원 + 위 원
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + radius * math.cos(angle)
        z = cz + radius * math.sin(angle)
        mesh.Vertices.Add(x, cy, z)           # bottom ring
        mesh.Vertices.Add(x, cy + height, z)  # top ring

    # 중심점
    bc = len(mesh.Vertices)
    mesh.Vertices.Add(cx, cy, cz)          # bottom center
    mesh.Vertices.Add(cx, cy + height, cz) # top center

    for i in range(segments):
        i2 = (i + 1) % segments
        # 옆면
        mesh.Faces.AddFace(i*2, i2*2, i2*2+1, i*2+1)
        # 아래면
        mesh.Faces.AddFace(bc, i*2, i2*2)
        # 위면
        mesh.Faces.AddFace(bc+1, i2*2+1, i*2+1)

    mesh.Normals.ComputeNormals()
    attr = rh.ObjectAttributes()
    attr.LayerIndex = layer_idx
    model.Objects.AddMesh(mesh, attr)

# ── 헬퍼: Plane (사각 면)
def add_plane(cx, cy, cz, w, h, normal, layer_idx):
    """normal: 'y+'(바닥/천장), 'z+'(벽), 'x+'(좌우벽)"""
    mesh = rh.Mesh()

    if normal == 'y-':  # 바닥 (XZ plane)
        mesh.Vertices.Add(cx-w/2, cy, cz-h/2)
        mesh.Vertices.Add(cx+w/2, cy, cz-h/2)
        mesh.Vertices.Add(cx+w/2, cy, cz+h/2)
        mesh.Vertices.Add(cx-w/2, cy, cz+h/2)
    elif normal == 'y+':  # 천장
        mesh.Vertices.Add(cx-w/2, cy, cz+h/2)
        mesh.Vertices.Add(cx+w/2, cy, cz+h/2)
        mesh.Vertices.Add(cx+w/2, cy, cz-h/2)
        mesh.Vertices.Add(cx-w/2, cy, cz-h/2)
    elif normal == 'z+':  # 뒷벽 (XY plane, z 방향)
        mesh.Vertices.Add(cx-w/2, cy-h/2, cz)
        mesh.Vertices.Add(cx+w/2, cy-h/2, cz)
        mesh.Vertices.Add(cx+w/2, cy+h/2, cz)
        mesh.Vertices.Add(cx-w/2, cy+h/2, cz)
    elif normal == 'x+':  # 좌벽 (ZY plane)
        mesh.Vertices.Add(cx, cy-h/2, cz-w/2)
        mesh.Vertices.Add(cx, cy-h/2, cz+w/2)
        mesh.Vertices.Add(cx, cy+h/2, cz+w/2)
        mesh.Vertices.Add(cx, cy+h/2, cz-w/2)
    elif normal == 'x-':  # 우벽
        mesh.Vertices.Add(cx, cy-h/2, cz+w/2)
        mesh.Vertices.Add(cx, cy-h/2, cz-w/2)
        mesh.Vertices.Add(cx, cy+h/2, cz-w/2)
        mesh.Vertices.Add(cx, cy+h/2, cz+w/2)

    mesh.Faces.AddFace(0, 1, 2, 3)
    mesh.Normals.ComputeNormals()

    attr = rh.ObjectAttributes()
    attr.LayerIndex = layer_idx
    model.Objects.AddMesh(mesh, attr)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Museum Room 수치 (vr.html과 동일)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
roomW = 16
roomH = 7
roomD = 20
roomZ = -roomD / 2 + 3  # = -7

# ── 바닥
add_plane(0, 0, roomZ, roomW, roomD, 'y-', layer_floor)

# ── 바닥 그리드
for x_val in range(-8, 9, 2):
    add_box(x_val, 0.001, roomZ, 0.01, 0.002, roomD, layer_grid)
z_start = roomZ - roomD/2
z_end = roomZ + roomD/2
z_val = z_start
while z_val <= z_end:
    add_box(0, 0.001, z_val, roomW, 0.002, 0.01, layer_grid)
    z_val += 2

# ── 뒷벽
add_plane(0, roomH/2, roomZ - roomD/2, roomW, roomH, 'z+', layer_walls)

# ── 좌벽
add_plane(-roomW/2, roomH/2, roomZ, roomD, roomH, 'x+', layer_walls)

# ── 우벽
add_plane(roomW/2, roomH/2, roomZ, roomD, roomH, 'x-', layer_walls)

# ── 천장
add_plane(0, roomH, roomZ, roomW, roomD, 'y+', layer_ceiling)

# ── 바닥 골드 몰딩
add_box(0, 0.03, roomZ - roomD/2 + 0.03, roomW, 0.06, 0.06, layer_molding)
add_box(-roomW/2 + 0.03, 0.03, roomZ, 0.06, 0.06, roomD, layer_molding)
add_box(roomW/2 - 0.03, 0.03, roomZ, 0.06, 0.06, roomD, layer_molding)

# ── 천장 몰딩
add_box(0, roomH - 0.02, roomZ - roomD/2 + 0.02, roomW, 0.04, 0.04, layer_molding)
add_box(-roomW/2 + 0.02, roomH - 0.02, roomZ, 0.04, 0.04, roomD, layer_molding)
add_box(roomW/2 - 0.02, roomH - 0.02, roomZ, 0.04, 0.04, roomD, layer_molding)

# ── 거울 3개 + 골드 프레임
for i in [-1, 0, 1]:
    mx = i * 3.2
    mz = roomZ - roomD/2 + 0.02

    # 거울면
    add_plane(mx, 3.2, mz, 2.4, 4, 'z+', layer_mirror)

    # 프레임
    add_box(mx, 5.23, mz + 0.01, 2.6, 0.06, 0.06, layer_mirror_frame)
    add_box(mx, 1.17, mz + 0.01, 2.6, 0.06, 0.06, layer_mirror_frame)
    add_box(mx - 1.27, 3.2, mz + 0.01, 0.06, 4.18, 0.06, layer_mirror_frame)
    add_box(mx + 1.27, 3.2, mz + 0.01, 0.06, 4.18, 0.06, layer_mirror_frame)

# ── 천장 조명 장식
for pos in [(0, -3), (0, -6), (0, -9)]:
    cx, cz = pos
    add_cylinder(cx, roomH - 0.03, cz, 0.4, 0.03, layer_ceil_fixture)

# ── 센터 러그
add_plane(0, 0.003, -3, 8, 12, 'y-', layer_rug)
# 러그 골드 테두리
add_box(0, 0.004, -3 - 6, 8.1, 0.003, 0.04, layer_molding)
add_box(0, 0.004, -3 + 6, 8.1, 0.003, 0.04, layer_molding)
add_box(-4.05, 0.004, -3, 0.04, 0.003, 12.1, layer_molding)
add_box(4.05, 0.004, -3, 0.04, 0.003, 12.1, layer_molding)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pedestals (4개)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pedH = 1.15
pedR = 0.5

pedestal_positions = [
    (-3, 0, -4),
    (3, 0, -4),
    (-3, 0, -8),
    (3, 0, -8),
]

pedestal_names = [
    "Crown of Empress Eugenie",
    "Emerald Teardrop Necklace",
    "Sapphire Necklace & Earrings",
    "Earrings of Empress Eugenie",
]

for px, py, pz in pedestal_positions:
    # 하단 베이스
    bw = pedR * 2.6
    add_box(px, 0.04, pz, bw, 0.08, bw, layer_pedestal)

    # 베이스 골드 테두리
    add_box(px, 0.085, pz, pedR*2.7, 0.015, pedR*2.7, layer_pedestal_gold)

    # 기둥
    pw = pedR * 1.8
    add_box(px, pedH/2 + 0.02, pz, pw, pedH - 0.15, pw, layer_pedestal)

    # 상단 플레이트
    tw = pedR * 2.4
    add_box(px, pedH + 0.03, pz, tw, 0.06, tw, layer_pedestal)

    # 상단 골드 테두리
    add_box(px, pedH + 0.065, pz, pedR*2.5, 0.015, pedR*2.5, layer_pedestal_gold)

    # 중간 골드 라인
    add_box(px, pedH*0.5, pz, pedR*1.9, 0.015, pedR*1.9, layer_pedestal_gold)

    # 네임 플레이트
    add_box(px, pedH*0.3, pz + pedR*0.92, 0.8, 0.12, 0.02, layer_nameplate)
    add_box(px, pedH*0.3, pz + pedR*0.92 + 0.011, 0.84, 0.14, 0.01, layer_pedestal_gold)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 저장
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
output_path = "/Users/min/Desktop/museum-vr/museum_exhibition.3dm"
model.Write(output_path, 7)  # version 7
print(f"✅ 라이노 파일 저장 완료: {output_path}")
print(f"   레이어: {len(model.Layers)}개")
print(f"   오브젝트: {len(model.Objects)}개")
