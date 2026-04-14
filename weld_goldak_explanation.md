---
marp: true
theme: default
paginate: true
style: |
  section {
    font-size: 22px;
  }
  h1 { color: #1a5276; border-bottom: 2px solid #1a5276; }
  h2 { color: #1f618d; }
  code { background: #f0f0f0; }
  pre { background: #f8f8f8; border-left: 4px solid #1a5276; }
  .note { background: #eaf4fb; padding: 8px; border-radius: 4px; }
---

# ANSYS APDL 溶接シミュレーションスクリプト解説
## `weld_goldak.ans`

Goldak 二重楕円熱源モデルを用いた過渡熱解析

---

# 目次

1. スクリプト全体の構造
2. ソルバー設定
3. Goldak 熱源パラメータ
4. 溶接パスの定義
5. メインループの処理フロー
6. 局所座標系の構築
7. 熱源の適用（要素ループ）
8. 冷却ステップ
9. パラメータ調整のガイド

---

# 1. スクリプト全体の構造

```
weld_goldak.ans
│
├── [1] ソルバー設定          (/solu, ANTYPE, EQSLV, ...)
├── [2] デバッグフラグ         (debug = 1/0)
├── [3] 熱源パラメータ         (L_y, L_z, L_x1, L_x2, ff, W_p, vel)
├── [4] パス定義               (path_num, steps, 座標配列)
│
└── [5] メインループ
    │
    ├── 外側ループ (kk = 1 〜 path_num)   ← 溶接パスごと
    │   │
    │   └── 内側ループ (ii = 1 〜 steps+1) ← タイムステップごと
    │       ├── 前ステップの荷重を削除
    │       ├── 熱源位置を計算
    │       ├── 局所座標系を構築
    │       ├── 近傍要素を選択
    │       ├── 各要素に発熱量を適用 (BFE,HGEN)
    │       └── SOLVE
    │
    └── [6] 冷却ステップ (autots)
```

---

# 2. ソルバー設定

```apdl
/solu

ANTYPE,4       ! 解析タイプ: 4 = 過渡解析 (Transient)
EQSLV,PCG      ! 連立方程式ソルバー: PCG (前処理共役勾配法)
               !   大規模モデルに有効。収束しない場合は SPARSE に変更
TRNOPT,full    ! 過渡解析オプション: full = フル法 (縮退なし)
NEQIT,60       ! Newton-Raphson 反復の最大回数
               !   材料非線形が強い溶接解析では多めに設定
thopt,full     ! 熱解析オプション: full = 完全ニュートン法
```

**ポイント**
- `ANTYPE,4` で時間発展する温度場を解く
- PCG は大規模モデルで SPARSE より速いが、条件数が悪い場合は収束しないことがある
- `NEQIT,60` は温度依存材料特性による強い非線形を吸収するための安全マージン

---

# 3. Goldak 二重楕円熱源モデル

## 数式

$$
q(x,y,z) = \frac{6\sqrt{3} \cdot f_i \cdot W_p}{L_x \cdot L_y \cdot L_z \cdot \pi\sqrt{\pi}}
\exp\!\left(-\frac{3x^2}{L_x^2}\right)
\exp\!\left(-\frac{3y^2}{L_y^2}\right)
\exp\!\left(-\frac{3z^2}{L_z^2}\right)
$$

- $f_i$ : 前方 $f_f$ / 後方 $f_r = 2 - f_f$ のエネルギー配分係数
- $L_x, L_y, L_z$ : 熱源の半径（楕円の軸長）
- $W_p$ : 入熱 [W]
- 座標は **熱源中心を原点とした局所座標系**

---

# 3. Goldak パラメータの設定

```apdl
L_y  = 0.004   ! y方向半径 [m] ← 溶接幅の半分に対応
L_z  = 0.003   ! z方向半径 [m] ← 溶け込み深さに対応
L_x1 = 0.005   ! 前方半径   [m] ← アーク前方の加熱範囲
L_x2 = 0.010   ! 後方半径   [m] ← アーク後方の加熱範囲 (通常 L_x1 の 2倍)

ff = 0.6       ! 前方エネルギー係数 (0 < ff < 1, 通常 0.4〜0.6)
fr = 2 - ff    ! 後方エネルギー係数 (自動計算、変更不要)
               ! ※ ff + fr = 2 となるように設計されている

W_p = 2000     ! 入熱 [W] = 電圧 × 電流 × 熱効率
               !   例: 20V × 150A × 0.67 = 2010 W
vel = 0.005    ! 溶接速度 [m/s] = 5 mm/s
```

**L_x1 < L_x2 の理由**: アーク後方は溶融池が広がるため、前方より加熱範囲が広い

---

# 4. 溶接パスの定義

```apdl
path_num = 1          ! 溶接パス数 (多パス溶接では 2 以上に設定)

*dim,x_start,array,path_num   ! 各パスの開始・終了座標を配列で定義
*dim,y_start,array,path_num
...
*dim,steps,array,path_num

steps(1) = 100        ! パスを分割するタイムステップ数
                      ! 多いほど精度が上がるが計算時間も増加

x_start(1) = 0.015   ! 開始点 X [m]
y_start(1) = 0.010   ! 開始点 Y [m] (板の上面)
z_start(1) = 0.005   ! 開始点 Z [m]

x_finish(1) = 0.015  ! 終了点 X [m] (X は変わらない = 直線溶接)
y_finish(1) = 0.010  ! 終了点 Y [m]
z_finish(1) = 0.095  ! 終了点 Z [m]

z_angle(1) = 0       ! 溶接方向周りの回転角 [deg]
                     ! 0 = 上面が法線方向 (水平板の溶接)
```

---

# 5. メインループ: 外側ループ（パスごと）

```apdl
*do,kk,1,path_num

    ! パスの長さを計算 (3次元距離)
    direct_len = ((x_start(kk)-x_finish(kk))**2
                + (y_start(kk)-y_finish(kk))**2
                + (z_start(kk)-z_finish(kk))**2)**0.5

    ! 溶接方向の方向余弦 (単位ベクトルの各成分)
    cos_x = (x_finish(kk)-x_start(kk)) / direct_len
    cos_y = (y_finish(kk)-y_start(kk)) / direct_len
    cos_z = (z_finish(kk)-z_start(kk)) / direct_len

    time_weld      = direct_len / vel           ! このパスの溶接時間 [s]
    time_step_weld = time_weld / steps(kk)      ! 1ステップの時間幅 [s]
```

**方向余弦**: 溶接方向の単位ベクトル成分。後の局所座標系構築に使用。

---

# 5. メインループ: 内側ループ（タイムステップごと）

```apdl
    *do,ii,1,steps(kk)+1

        ! 前のステップの荷重をすべて削除 (重要: 前ステップの熱源を消す)
        allsel
        bfedele,all,HGEN    ! 全要素の発熱量 (HGEN) を削除
        ddele,all,temp      ! 全ノードの温度拘束を削除

        ! 解析時間の設定
        time_stepped = ii * time_step_weld              ! パス内の経過時間
        wtime        = time_weld_overall + time_stepped  ! 全体の経過時間
        time,wtime                                       ! ANSYSに時刻を指示

        ! 現在の熱源位置 (等速直線運動)
        x_weld = x_s_active + vel * time_sol * cos_x
        y_weld = y_s_active + vel * time_sol * cos_y
        z_weld = z_s_active + vel * time_sol * cos_z
```

**なぜ steps+1 回ループするか**: 最終ステップ完了後も `SOLVE` を1回実行し、パス終端の温度場を記録するため。

---

# 6. 局所座標系の構築

熱源の数式は「熱源中心を原点・X軸が溶接方向」の局所座標系で定義される。

```apdl
*afun,deg   ! 角度をdegree単位で計算

! 方向余弦から回転角を計算
*if,cos_y,eq,0,then
    ang_x = 0
*else
    ang_x = acos(cos_x) * SIGN(1,cos_y)   ! Y方向への傾き
*endif
ang_y = -(90 - acos(cos_z)) * SIGN(1,cos_x)  ! Z方向への傾き
ang_z = z_angle(kk)                           ! 上面法線の回転

csys,0   ! グローバル座標系に戻る

! 熱源位置を原点にした直交座標系を作成 (段階的に回転)
clocal,csys_num_cart,cart, x_weld,y_weld,z_weld, ang_x,0,0
clocal,csys_num_cart,cart, 0,0,0, 0,0,ang_y
clocal,csys_num_cart,cart, 0,0,0, 0,ang_z,0

! 同じ原点で球座標系も作成 (球内の要素選択に使用)
clocal,csys_num_cyl,cylin,0,0,0
clocal,csys_num_sph,sphe, 0,0,0
```

---

# 6. 局所座標系の役割

```
グローバル座標系 (csys=0)         局所座標系 (csys_num_cart)
                                  (熱源中心 = 原点)
    Z (溶接方向)
    ↑                                  X (溶接方向 ←→ LOCAL X)
    |    * 熱源                        |
    |   /                              |--→ Y (幅方向)
    |  /                               |
    +-→ X (板の幅方向)                ↓ Z (深さ方向)

```

- **csys_num_cart (120)**: 直交座標系 → 各要素の x1, y1, z1 を取得
- **csys_num_sph (122)**: 球座標系 → 熱源から半径 `L_select` 以内の要素を高速選択

---

# 7. 熱源の適用: 要素選択

```apdl
! Step 1: 熱を受け取れる要素グループから開始
cmsel,s,heated_elements

! Step 2: 球座標系で熱源中心から L_select 以内のノードを選択
csys,csys_num_sph
nsel,s,loc,x,0,L_select    ! 球の半径 = L_x2 × 5

! Step 3: 選択ノードに属する要素に絞り込む
esln

! Step 4: 生きている要素だけを対象に (element birth/death使用時)
esel,r,live

csys,0
cm,selected_elements,elem   ! 選択結果を "selected_elements" として保存
```

**L_select = L_x2 × 5 の意味**:
後方半径 (10mm) の5倍 = 50mm 以内の要素を候補とする。
熱源から遠すぎる要素への無駄な計算を省くフィルター。

---

# 7. 熱源の適用: Goldak 発熱量の計算

```apdl
cmsel,s,selected_elements
curr_el = 0
curr_el = elnext(curr_el)   ! 最初の要素番号を取得

*dowhile,curr_el            ! 選択内の全要素をループ

    ! 要素重心の局所座標を取得
    csys,csys_num_cart
    *get,x1,elem,curr_el,cent,x
    *get,y1,elem,curr_el,cent,y
    *get,z1,elem,curr_el,cent,z

    ! 前方 / 後方の判定 (局所X座標の符号で判定)
    *if,x1,gt,0,then
        L_x = L_x1  &  f1 = ff   ! 熱源前方
    *else
        L_x = L_x2  &  f1 = fr   ! 熱源後方
    *endif

    ! Goldak 式を2段階に分けて計算 (ループ外に出せない部分を最小化)
    part1 = (6*sqrt(3)*f1*W_p) / (L_x*L_y*L_z*pi*sqrt(pi))
    part2 = exp(-3*(x1/L_x)**2) * exp(-3*(y1/L_y)**2) * exp(-3*(z1/L_z)**2)
    qf = part1 * part2

    bfe,curr_el,HGEN,,qf    ! 発熱量 [W/m³] を要素に適用

    cmsel,s,selected_elements
    curr_el = elnext(curr_el)   ! 次の要素へ
*enddo

allsel
solve
```

---

# 7. `part1` / `part2` 分割の理由

```apdl
part1 = (6*sqrt(3)*f1*W_p) / (L_x*L_y*L_z*pi*sqrt(pi))
part2 = exp(-3*(x1/L_x)**2) * exp(-3*(y1/L_y)**2) * exp(-3*(z1/L_z)**2)
```

**`part1`**: $W_p$, $L_x$, $L_y$, $L_z$ のみに依存 → 要素ごとに変わらない定数部分

**`part2`**: 各要素の位置 $(x_1, y_1, z_1)$ に依存 → 要素ごとに計算が必要な部分

この分割により、コンパイラ的な最適化が明示的になり、
スクリプト内での再計算を最小限に抑えている。

> 溶接シミュレーションは要素数×ステップ数の組み合わせが膨大になるため、
> ループ内の計算を1命令でも減らすことが実用上重要。

---

# 8. 冷却ステップ

```apdl
! 溶接完了後の冷却
allsel

TIME,time_weld_overall           ! 溶接終了時刻をまず設定
autots,on                        ! 自動時間刻み幅制御をON
deltim,10,5,40,on                ! 時間刻み: 初期=10s, 最小=5s, 最大=40s

TIME,time_weld_overall + time_cool   ! 冷却終了時刻

allsel
solve
```

**溶接フェーズとの違い**:

| | 溶接フェーズ | 冷却フェーズ |
|--|--|--|
| 時間刻み | 固定 (= `time_weld/steps`) | 自動 (`autots`) |
| SOLVE 回数 | `steps+1` 回 | ~20〜30 回 |
| 非線形の強さ | 強い (急激な温度変化) | 弱い (緩やかに冷却) |

`autots` は収束が速いときは刻みを大きく、遅いときは小さくして効率化する。

---

# 9. パラメータ調整ガイド

## 精度を上げるには

| パラメータ | 方向 | 効果 |
|------------|------|------|
| `steps` | 増やす | 熱源位置の時間分解能が上がる |
| `L_select` の倍率 | 上げる | より広い範囲の要素に熱を適用 |
| メッシュサイズ | 細かく | 温度勾配の空間分解能が上がる |
| `NEQIT` | 増やす | 収束しにくい条件でも計算を継続 |

## 速度を上げるには

| パラメータ | 方向 | 効果 |
|------------|------|------|
| `steps` | 減らす | SOLVE 回数が減る |
| `time_cool` | 減らす | 冷却 substep 数が減る |
| `L_select` の倍率 | 下げる | 要素ループの対象が減る |
| `debug = 1` | - | steps=5, time_cool=15 に自動切替 |

---

# 9. デバッグフラグ

```apdl
! スクリプト先頭のフラグ1つで計算量を切り替え
debug = 1    ! テスト実行 (~1/20 の計算量)
debug = 0    ! 本番実行  (フル解像度)

! 内部での動作:
*if,debug,eq,1,then
    time_cool = 15    ! 冷却時間を短縮
*else
    time_cool = 300
*endif

*if,debug,eq,1,then
    steps(1) = 5      ! 溶接ステップ数を削減
*else
    steps(1) = 100
*endif
```

---

# まとめ: データフロー

```
入力パラメータ
(L_y, L_z, L_x1, L_x2, ff, W_p, vel)
        ↓
パス座標・ステップ数の定義
(x_start, x_finish, steps, ...)
        ↓
外側ループ (パスごと)
  → 方向余弦の計算
  → 溶接時間・時間刻みの計算
        ↓
内側ループ (タイムステップごと)
  → 熱源位置の更新
  → 局所座標系の再構築
  → 球内要素の選択
  → Goldak 式で発熱量を計算・適用 (BFE,HGEN)
  → SOLVE (過渡熱解析)
        ↓
冷却ステップ (autots)
  → SOLVE
        ↓
結果ファイル (.rth) → post_animation.ans で可視化
```

---

# 参考: 主要 APDL コマンド対応表

| コマンド | 役割 |
|----------|------|
| `ANTYPE,4` | 過渡解析モードに設定 |
| `time,t` | 現在のロードステップの終了時刻を設定 |
| `bfe,el,HGEN,,q` | 要素 `el` に体積発熱量 `q` [W/m³] を適用 |
| `bfedele,all,HGEN` | 全要素の発熱量を削除 |
| `ddele,all,temp` | 全ノードの温度拘束を削除 |
| `clocal,n,type,x,y,z,rx,ry,rz` | 局所座標系を定義 |
| `csys,n` | アクティブな座標系を切り替え |
| `nsel,s,loc,x,r1,r2` | 現在の座標系で loc 範囲内のノードを選択 |
| `esln` | 選択ノードに属する要素を選択 |
| `elnext(n)` | 選択内で `n` の次の要素番号を返す関数 |
| `cm,name,elem` | 現在の要素選択を名前付きコンポーネントに保存 |
| `autots,on` | 自動時間刻み幅制御を有効化 |
| `deltim,dt,dtmin,dtmax` | 時間刻み幅の初期値・範囲を設定 |
| `solve` | 現在のロードステップを解く |
