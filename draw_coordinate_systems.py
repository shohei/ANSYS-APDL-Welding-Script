"""
Visualization of the three local coordinate systems in weld_goldak.ans:
  csys_num_cart (120) : Cartesian  - used to get element centroid (x1, y1, z1)
  csys_num_cyl  (121) : Cylindrical - intermediate (created by clocal)
  csys_num_sph  (122) : Spherical   - used for sphere selection (nsel,loc,x,0,L_select)

All three share the same origin (heat source center) and orientation
(Local X = weld direction).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D

# ── heat source parameters (same as weld_goldak.ans) ──────────────────────
L_x1 = 0.005   # front radius [m]
L_x2 = 0.010   # rear  radius [m]
L_y  = 0.004
L_z  = 0.003
L_select = L_x2 * 5   # sphere selection radius = 0.05 m

# ── helpers ────────────────────────────────────────────────────────────────
def goldak_surface(L_x, L_y, L_z, n=40):
    """Return x,y,z points on the Goldak ellipsoid half."""
    u = np.linspace(0, np.pi, n)
    v = np.linspace(0, 2*np.pi, n)
    U, V = np.meshgrid(u, v)
    X = L_x * np.cos(U)          # ±L_x along local X
    Y = L_y * np.sin(U)*np.cos(V)
    Z = L_z * np.sin(U)*np.sin(V)
    return X, Y, Z

def sphere_surface(r, n=30):
    u = np.linspace(0, np.pi, n)
    v = np.linspace(0, 2*np.pi, n)
    U, V = np.meshgrid(u, v)
    return r*np.sin(U)*np.cos(V), r*np.sin(U)*np.sin(V), r*np.cos(U)

def draw_arc(ax, r, theta_range, phi=np.pi/2, color='gray', lw=1, ls='--', alpha=0.6):
    """Draw arc on XZ plane (phi=pi/2 → Y=0 plane)."""
    th = np.linspace(*theta_range, 60)
    x = r * np.sin(th) * np.cos(phi)
    y = r * np.sin(th) * np.sin(phi)
    z = r * np.cos(th)
    ax.plot(x, y, z, color=color, lw=lw, ls=ls, alpha=alpha)

# ── figure layout ──────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 10))
fig.patch.set_facecolor('#f8f9fa')

gs = gridspec.GridSpec(1, 2, width_ratios=[3, 2], wspace=0.05)
ax  = fig.add_subplot(gs[0], projection='3d')   # main 3-D view
ax2 = fig.add_subplot(gs[1])                     # 2-D schematic (XZ cross-section)

ax.set_facecolor('#eef2f7')
ax2.set_facecolor('#eef2f7')

# ═══════════════════════════════════════════════════════════════════════════
# LEFT: 3-D view
# ═══════════════════════════════════════════════════════════════════════════

ORIGIN = np.array([0., 0., 0.])

# ── selection sphere (csys_num_sph) ─────────────────────────────────────
sx, sy, sz = sphere_surface(L_select)
ax.plot_surface(sx, sy, sz, alpha=0.06, color='royalblue', linewidth=0)
# equator & meridian wireframe
for phi in [0, np.pi/2, np.pi, 3*np.pi/2]:
    th = np.linspace(0, np.pi, 60)
    ax.plot(L_select*np.sin(th)*np.cos(phi),
            L_select*np.sin(th)*np.sin(phi),
            L_select*np.cos(th), 'royalblue', lw=0.5, alpha=0.3)
for th_val in [np.pi/4, np.pi/2, 3*np.pi/4]:
    ph = np.linspace(0, 2*np.pi, 60)
    ax.plot(L_select*np.sin(th_val)*np.cos(ph),
            L_select*np.sin(th_val)*np.sin(ph),
            L_select*np.cos(th_val), 'royalblue', lw=0.5, alpha=0.3)

# ── Goldak ellipsoid (front half: +X, rear half: -X) ────────────────────
for (lx, col, label, alpha) in [(L_x1, '#e74c3c', 'Front ellipsoid (L_x1)', 0.25),
                                  (L_x2, '#e67e22', 'Rear ellipsoid (L_x2)',  0.15)]:
    Xg, Yg, Zg = goldak_surface(lx, L_y, L_z)
    # keep only front or rear half
    mask = (Xg >= 0) if lx == L_x1 else (Xg <= 0)
    Xg[~mask] = np.nan
    ax.plot_surface(Xg, Yg, Zg, alpha=alpha, color=col, linewidth=0)

# ellipsoid outline (XY and XZ planes)
for plane, col in [('XZ', '#c0392b'), ('XY', '#e67e22')]:
    ang = np.linspace(-np.pi, np.pi, 200)
    if plane == 'XZ':
        xf = np.where(ang >= 0,  L_x1*np.cos(ang), L_x2*np.cos(ang))
        ax.plot(xf, np.zeros_like(ang), L_z*np.sin(ang), col, lw=1.5, alpha=0.8)
    else:
        xf = np.where(ang >= 0,  L_x1*np.cos(ang), L_x2*np.cos(ang))
        ax.plot(xf, L_y*np.sin(ang), np.zeros_like(ang), col, lw=1.5, alpha=0.6)

# ── LOCAL AXES (csys_num_cart) ───────────────────────────────────────────
AL = L_select * 0.7   # arrow length
colors_ax = {'X': '#c0392b', 'Y': '#1abc9c', 'Z': '#8e44ad'}
dirs = {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}
for name, d in dirs.items():
    ax.quiver(0, 0, 0, d[0]*AL, d[1]*AL, d[2]*AL,
              color=colors_ax[name], linewidth=2.5, arrow_length_ratio=0.12)
    ax.text(d[0]*AL*1.08, d[1]*AL*1.08, d[2]*AL*1.08,
            f'Local {name}\n(cart)', color=colors_ax[name], fontsize=10, fontweight='bold')

# ── CYLINDRICAL axes (csys_num_cyl) ─────────────────────────────────────
# show r, theta in the YZ plane (perpendicular to local X)
r_cyl = L_y * 1.6
theta_demo = np.pi / 4
y_demo = r_cyl * np.cos(theta_demo)
z_demo = r_cyl * np.sin(theta_demo)

# r arrow
ax.quiver(0, 0, 0, 0, y_demo, z_demo,
          color='#f39c12', linewidth=2, arrow_length_ratio=0.12)
ax.text(0, y_demo*1.1, z_demo*1.1, 'r (cyl)', color='#f39c12', fontsize=9, fontweight='bold')

# theta arc in YZ plane
th_arc = np.linspace(0, theta_demo, 40)
ax.plot(np.zeros(40), r_cyl*0.5*np.cos(th_arc), r_cyl*0.5*np.sin(th_arc),
        color='#f39c12', lw=2, ls='--')
ax.text(0, r_cyl*0.45, r_cyl*0.15, 'θ (cyl)', color='#f39c12', fontsize=9)

# cylinder outline
ang = np.linspace(0, 2*np.pi, 80)
ax.plot(np.zeros(80), r_cyl*np.cos(ang), r_cyl*np.sin(ang),
        color='#f39c12', lw=1, ls=':', alpha=0.5)

# ── SPHERICAL coordinates (csys_num_sph) ────────────────────────────────
# show R, polar angle (theta_sph), azimuthal (phi_sph) for a demo point
R_demo = L_select * 0.55
theta_sph = np.pi / 3   # from local X axis
phi_sph   = np.pi / 4   # azimuth in YZ

xp = R_demo * np.cos(theta_sph)
yp = R_demo * np.sin(theta_sph) * np.cos(phi_sph)
zp = R_demo * np.sin(theta_sph) * np.sin(phi_sph)

# R arrow (from origin to demo point)
ax.quiver(0, 0, 0, xp, yp, zp,
          color='royalblue', linewidth=2, arrow_length_ratio=0.1)
ax.text(xp*1.05, yp*1.05, zp*1.05, 'R (sph)\n← nsel uses this\n   for sphere select',
        color='royalblue', fontsize=8.5, fontweight='bold')

# theta_sph arc (in XY plane projected to demo phi)
th_arc2 = np.linspace(0, theta_sph, 40)
ax.plot(R_demo*0.4*np.cos(th_arc2),
        R_demo*0.4*np.sin(th_arc2)*np.cos(phi_sph),
        R_demo*0.4*np.sin(th_arc2)*np.sin(phi_sph),
        color='royalblue', lw=2, ls='--')
ax.text(R_demo*0.3, R_demo*0.15, R_demo*0.05, 'θ (sph)', color='royalblue', fontsize=8)

# heat source origin
ax.scatter(0, 0, 0, color='#f1c40f', s=250, zorder=9, depthshade=False, marker='*')
ax.text(0.001, 0.001, 0.002, 'Heat source\n(ORIGIN)', color='#f1c40f',
        fontsize=9, fontweight='bold')

# ── sample element and its local-cart coordinates ────────────────────────
ex, ey, ez = 0.003, 0.002, -0.002   # inside front ellipsoid
ax.scatter(ex, ey, ez, color='lime', s=100, zorder=9, depthshade=False, marker='s')
ax.text(ex+0.001, ey+0.001, ez, 'Element centroid\n(x1, y1, z1) in cart',
        color='lime', fontsize=8.5, fontweight='bold')
ax.plot([0,ex],[0,0],[0,0], 'lime', lw=1, ls=':')
ax.plot([ex,ex],[0,ey],[0,0], 'lime', lw=1, ls=':')
ax.plot([ex,ex],[ey,ey],[0,ez], 'lime', lw=1, ls=':')

# axis limits and labels
lim = L_select * 0.85
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_zlim(-lim, lim)
ax.set_xlabel('Local X\n(weld direction)', fontsize=9, labelpad=6)
ax.set_ylabel('Local Y\n(width)', fontsize=9, labelpad=6)
ax.set_zlabel('Local Z\n(depth)', fontsize=9, labelpad=6)
ax.view_init(elev=20, azim=-50)
ax.set_title('3D view: Three local coordinate systems\n(origin = heat source center)',
             fontsize=11, fontweight='bold')

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT: 2-D cross-section schematic (Local X – Local Z plane, Y=0)
# ═══════════════════════════════════════════════════════════════════════════
ax2.set_aspect('equal')
ax2.set_facecolor('#eef2f7')
ax2.axhline(0, color='gray', lw=0.5, ls=':')
ax2.axvline(0, color='gray', lw=0.5, ls=':')

# selection sphere (circle in 2D)
circle_sel = plt.Circle((0,0), L_select, color='royalblue', fill=True,
                         alpha=0.07, lw=1.5, ls='--', ec='royalblue')
ax2.add_patch(circle_sel)
ax2.annotate('', xy=(L_select*0.72, L_select*0.72),
             xytext=(0, 0),
             arrowprops=dict(arrowstyle='->', color='royalblue', lw=2))
ax2.text(L_select*0.36, L_select*0.42,
         'R  (sph)\nnsel,s,loc,x,0,L_select\n→ selects all nodes\n   inside this sphere',
         color='royalblue', fontsize=8.5, ha='center',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#dce9f7', alpha=0.8))

# Goldak ellipse outline in XZ plane
ang = np.linspace(-np.pi, np.pi, 300)
xf  = np.where(ang >= 0, L_x1*np.cos(ang), L_x2*np.cos(ang))
zf  = L_z * np.sin(ang)
ax2.plot(xf, zf, '#e74c3c', lw=2.5, label='Goldak ellipse (XZ cross-section)')
ax2.fill(xf, zf, alpha=0.15, color='#e74c3c')

# front / rear labels
ax2.annotate('', xy=(L_x1, 0), xytext=(0, 0),
             arrowprops=dict(arrowstyle='->', color='#c0392b', lw=2))
ax2.text(L_x1/2, 0.001, 'L_x1\n(front)', color='#c0392b', ha='center', fontsize=9)
ax2.annotate('', xy=(-L_x2, 0), xytext=(0, 0),
             arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2))
ax2.text(-L_x2/2, 0.001, 'L_x2\n(rear)', color='#e67e22', ha='center', fontsize=9)
ax2.annotate('', xy=(0, -L_z), xytext=(0, 0),
             arrowprops=dict(arrowstyle='->', color='#8e44ad', lw=2))
ax2.text(0.002, -L_z/2, 'L_z\n(depth)', color='#8e44ad', fontsize=9)

# L_y label (out of plane – just note)
ax2.text(0.003, L_z*1.3,
         'L_y = out-of-plane\n(into screen = Local Y)',
         color='#1abc9c', fontsize=8.5, ha='left',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#d5f5ee', alpha=0.8))

# origin star
ax2.scatter(0, 0, color='#f1c40f', s=200, zorder=9, marker='*', label='Origin (heat source)')

# axes arrows
for (dx, dy, col, lbl, off) in [
    (L_select*0.6, 0,             '#c0392b', 'Local X (weld dir →)', ( 0.001,  0.001)),
    (0,            L_select*0.45, '#8e44ad', 'Local Z (↑ depth)',    ( 0.001,  0.001)),
]:
    ax2.annotate('', xy=(dx, dy), xytext=(0,0),
                 arrowprops=dict(arrowstyle='->', color=col, lw=2.5))
    ax2.text(dx+off[0], dy+off[1], lbl, color=col, fontsize=9, fontweight='bold')

# sample element
ex2, ez2 = 0.003, -0.002
ax2.scatter(ex2, ez2, color='lime', s=120, zorder=9, marker='s')
ax2.plot([0,ex2],[0,0], 'lime', lw=1, ls=':')
ax2.plot([ex2,ex2],[0,ez2], 'lime', lw=1, ls=':')
ax2.text(ex2+0.001, ez2-0.001,
         f'x1 = {ex2*1000:.0f} mm  (>0 → front)\nz1 = {ez2*1000:.0f} mm',
         color='lime', fontsize=8.5,
         bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a1a', alpha=0.6))

# coordinate system table
table_txt = (
    "csys  | Type       | APDL No | Used for\n"
    "──────┼────────────┼─────────┼──────────────────────────────\n"
    "cart  │ Cartesian  │   120   │ *get x1,y1,z1 (elem centroid)\n"
    "      │            │         │ → Goldak formula calculation\n"
    "cyl   │ Cylindrical│   121   │ intermediate (clocal chain)\n"
    "sph   │ Spherical  │   122   │ nsel,s,loc,x,0,L_select\n"
    "      │            │         │ → sphere-shaped element select\n"
)
ax2.text(-L_select*0.98, -L_select*0.88, table_txt,
         fontsize=7.8, family='monospace', va='bottom',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#fffde7',
                   edgecolor='#c8a800', lw=1.5))

ax2.set_xlim(-L_select*1.0, L_select*1.0)
ax2.set_ylim(-L_select*1.0, L_select*1.0)
ax2.set_xlabel('Local X  (weld direction) [m]', fontsize=10)
ax2.set_ylabel('Local Z  (depth direction) [m]', fontsize=10)
ax2.set_title('Cross-section: X–Z plane (Local Y = 0)\nShowing sphere selection vs Goldak ellipsoid',
              fontsize=10, fontweight='bold')
ax2.grid(True, alpha=0.3)

# ── overall title ──────────────────────────────────────────────────────────
fig.suptitle(
    'Relationship between csys_num_cart / csys_num_cyl / csys_num_sph\n'
    'All share the same origin (heat source center) and orientation (Local X = weld direction)',
    fontsize=12, fontweight='bold', y=1.01
)

plt.tight_layout()
plt.savefig('weld_coordinate_systems.png', dpi=160, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("Saved: weld_coordinate_systems.png")
plt.show()
