"""
Visualization of weld path geometry in weld_goldak.ans
Shows: start/finish points, direct_len, cos_x/cos_y/cos_z, local CS
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ── parameters (use a diagonal weld for clearer illustration) ──────────────
plate_x = 0.030   # plate width  [m]
plate_y = 0.010   # plate height [m]
plate_z = 0.100   # plate length [m]

# Diagonal weld to better illustrate all three direction cosines
x_start, y_start, z_start   = 0.005, 0.010, 0.010
x_finish, y_finish, z_finish = 0.025, 0.010, 0.090

# ── derived geometry ───────────────────────────────────────────────────────
dx = x_finish - x_start
dy = y_finish - y_start
dz = z_finish - z_start
direct_len = np.sqrt(dx**2 + dy**2 + dz**2)

cos_x = dx / direct_len
cos_y = dy / direct_len
cos_z = dz / direct_len

# heat source at midpoint (for local CS illustration)
t_mid = 0.5
xw = x_start + dx * t_mid
yw = y_start + dy * t_mid
zw = z_start + dz * t_mid

# ── figure setup ────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#f8f9fa')

ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#f0f4f8')

# ── draw plate (transparent box) ────────────────────────────────────────────
def draw_box(ax, x0, x1, y0, y1, z0, z1, color='steelblue', alpha=0.08):
    verts = [
        # bottom
        [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],
        # top
        [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],
        # front
        [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],
        # back
        [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],
        # left
        [(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)],
        # right
        [(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)],
    ]
    poly = Poly3DCollection(verts, alpha=alpha, facecolor=color, edgecolor='#4a7ba7', linewidth=0.6)
    ax.add_collection3d(poly)

draw_box(ax, 0, plate_x, 0, plate_y, 0, plate_z)

# ── weld path line ───────────────────────────────────────────────────────────
ax.plot([x_start, x_finish], [y_start, y_finish], [z_start, z_finish],
        color='#e74c3c', linewidth=3, zorder=5, label='Weld path')

# start / finish markers
ax.scatter(*[x_start], *[y_start], *[z_start],
           color='#27ae60', s=120, zorder=6, depthshade=False)
ax.scatter(*[x_finish], *[y_finish], *[z_finish],
           color='#e74c3c', s=120, zorder=6, depthshade=False)

ax.text(x_start - 0.006, y_start, z_start - 0.005,
        'START\n(x_start, y_start, z_start)', color='#27ae60', fontsize=10, fontweight='bold')
ax.text(x_finish + 0.001, y_finish, z_finish + 0.002,
        'FINISH\n(x_finish, y_finish, z_finish)', color='#e74c3c', fontsize=10, fontweight='bold')

# ── direct_len label on path ─────────────────────────────────────────────────
mid_x = (x_start + x_finish) / 2
mid_y = (y_start + y_finish) / 2
mid_z = (z_start + z_finish) / 2
ax.text(mid_x + 0.002, mid_y + 0.002, mid_z,
        f'direct_len\n= {direct_len*1000:.1f} mm', color='#e74c3c',
        fontsize=9, fontweight='bold', ha='left')

# ── direction cosine projections (dashed lines from start to finish) ─────────
# cos_x component: along X axis only
ax.plot([x_start, x_finish], [y_start, y_start], [z_start, z_start],
        'b--', linewidth=1.5, alpha=0.8)
ax.text((x_start+x_finish)/2, y_start - 0.001, z_start - 0.003,
        f'cos_x = {cos_x:.3f}', color='blue', fontsize=8.5)

# cos_z component: along Z axis only
ax.plot([x_start, x_start], [y_start, y_start], [z_start, z_finish],
        'g--', linewidth=1.5, alpha=0.8)
ax.text(x_start - 0.005, y_start, (z_start+z_finish)/2,
        f'cos_z = {cos_z:.3f}', color='green', fontsize=8.5)

# cos_y component (here dy=0, show as a note)
ax.text(x_finish + 0.001, y_finish + 0.002, z_start,
        f'cos_y = {cos_y:.3f}', color='#8e44ad', fontsize=8.5)

# helper projection lines (dotted grey)
ax.plot([x_finish, x_finish], [y_finish, y_finish], [z_start, z_finish],
        'gray', linewidth=0.8, linestyle=':', alpha=0.6)
ax.plot([x_start, x_finish], [y_start, y_start], [z_finish, z_finish],
        'gray', linewidth=0.8, linestyle=':', alpha=0.6)
ax.plot([x_finish, x_finish], [y_start, y_finish], [z_finish, z_finish],
        'gray', linewidth=0.8, linestyle=':', alpha=0.5)

# ── right-angle marks ────────────────────────────────────────────────────────
def right_angle(ax, corner, d1, d2, size=0.002, color='gray'):
    p1 = [corner[i] + d1[i]*size for i in range(3)]
    p2 = [corner[i] + d2[i]*size for i in range(3)]
    p3 = [corner[i] + d1[i]*size + d2[i]*size for i in range(3)]
    ax.plot([corner[0],p1[0]], [corner[1],p1[1]], [corner[2],p1[2]], color=color, lw=0.8)
    ax.plot([p1[0],p3[0]], [p1[1],p3[1]], [p1[2],p3[2]], color=color, lw=0.8)
    ax.plot([corner[0],p2[0]], [corner[1],p2[1]], [corner[2],p2[2]], color=color, lw=0.8)
    ax.plot([p2[0],p3[0]], [p2[1],p3[1]], [p2[2],p3[2]], color=color, lw=0.8)

right_angle(ax, [x_finish, y_start, z_start], [0,0,1], [-1,0,0], size=0.003)

# ── heat source position (midpoint) ─────────────────────────────────────────
ax.scatter(xw, yw, zw, color='#f39c12', s=200, zorder=7, depthshade=False,
           marker='*', label='Heat source position')
ax.text(xw + 0.002, yw + 0.001, zw,
        'Heat source\n(current position)', color='#f39c12', fontsize=8.5, fontweight='bold')

# ── local coordinate system at heat source ──────────────────────────────────
arrow_len = 0.012
# local X = weld direction (unit vector)
lx = np.array([cos_x, cos_y, cos_z])
# local Z = surface normal (up) after rotation: simplified here as global Y
lz = np.array([0, 1, 0])
ly = np.cross(lz, lx)
ly /= np.linalg.norm(ly)

def draw_arrow(ax, origin, direction, length, color, label):
    end = [origin[i] + direction[i]*length for i in range(3)]
    ax.quiver(*origin, *[direction[i]*length for i in range(3)],
              color=color, linewidth=2, arrow_length_ratio=0.25)
    ax.text(*end, f' {label}', color=color, fontsize=9, fontweight='bold')

draw_arrow(ax, [xw, yw, zw], lx, arrow_len, '#c0392b', 'Local X\n(weld dir)')
draw_arrow(ax, [xw, yw, zw], ly, arrow_len, '#1abc9c', 'Local Y')
draw_arrow(ax, [xw, yw, zw], lz, arrow_len, '#8e44ad', 'Local Z\n(normal)')

# ── formula box ─────────────────────────────────────────────────────────────
formula = (
    "direct_len = √(dx² + dy² + dz²)\n"
    f"  dx = x_finish - x_start = {dx*1000:.1f} mm\n"
    f"  dy = y_finish - y_start = {dy*1000:.1f} mm\n"
    f"  dz = z_finish - z_start = {dz*1000:.1f} mm\n"
    f"  → direct_len = {direct_len*1000:.1f} mm\n\n"
    "cos_x = dx / direct_len\n"
    "cos_y = dy / direct_len\n"
    "cos_z = dz / direct_len\n\n"
    "Used for:\n"
    "  • Heat source position update\n"
    "    x_weld = x_start + vel×t×cos_x\n"
    "  • Local CS orientation\n"
    "    (ang_x, ang_y from cos values)"
)
fig.text(0.72, 0.20, formula, fontsize=8.5, family='monospace',
         verticalalignment='bottom',
         bbox=dict(boxstyle='round,pad=0.6', facecolor='#fffde7',
                   edgecolor='#f0a500', linewidth=1.5))

# ── legend ───────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color='#e74c3c', label='Weld path (direct_len)'),
    mpatches.Patch(color='blue',    label='cos_x component (dx)'),
    mpatches.Patch(color='green',   label='cos_z component (dz)'),
    mpatches.Patch(color='#8e44ad', label='cos_y component (dy)'),
    mpatches.Patch(color='#f39c12', label='Heat source position'),
    mpatches.Patch(color='#c0392b', label='Local X axis (weld direction)'),
    mpatches.Patch(color='#1abc9c', label='Local Y axis'),
    mpatches.Patch(color='#8e44ad', label='Local Z axis (surface normal)'),
]
ax.legend(handles=legend_items, loc='upper left', fontsize=8,
          bbox_to_anchor=(-0.02, 1.02), framealpha=0.9)

# ── axis labels and view ─────────────────────────────────────────────────────
ax.set_xlabel('X [m]\n(plate width)', fontsize=10, labelpad=8)
ax.set_ylabel('Y [m]\n(plate height)', fontsize=10, labelpad=8)
ax.set_zlabel('Z [m]\n(weld direction)', fontsize=10, labelpad=8)

ax.set_xlim(0, plate_x)
ax.set_ylim(-0.005, plate_y + 0.005)
ax.set_zlim(0, plate_z)

ax.view_init(elev=28, azim=-60)
ax.set_title('Weld Path Geometry: direction cosines & local coordinate system\n'
             '(weld_goldak.ans)',
             fontsize=12, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('weld_geometry.png', dpi=160, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("Saved: weld_geometry.png")
plt.show()
