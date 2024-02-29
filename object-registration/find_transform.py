import matplotlib.cm as mcm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.spatial
import skimage.measure
import sys


csv1, csv2 = sys.argv[1:3]
df1 = pd.read_csv(csv1, index_col=False)
df2 = pd.read_csv(csv2, index_col=False)

if not (df1.columns ==  df2.columns).all():
    print("CSV file columns don't match")
    sys.exit(1)

df = df.rename(columns={
    "NucLocation_Center_X": "X",
    "NucLocation_Center_Y": "Y",
    "NucArea": "Area",
    "NucPerimeter": "Perimeter",
})
cg = df[(df.Well=="G03")].groupby("Cycle")
a = cg.get_group("Cyc1")
b = cg.get_group("Cyc2")
a_pos = a[["X", "Y"]].values
b_pos = b[["X", "Y"]].values

max_err = 15

dist = scipy.spatial.distance.cdist(a_pos, b_pos)
match_b = np.argmin(dist, axis=1)
model, inliers = skimage.measure.ransac(
    (a_pos, b_pos[match_b]),
    model_class=skimage.transform.EuclideanTransform,
    min_samples=2,
    residual_threshold=max_err,
    max_trials=300,
)

dist2 = scipy.spatial.distance.cdist(model(a_pos), b_pos)
match_b2 = np.argmin(dist2, axis=1)
model2, inliers2 = skimage.measure.ransac(
    (a_pos, b_pos[match_b2]),
    model_class=skimage.transform.EuclideanTransform,
    min_samples=2,
    residual_threshold=max_err,
    max_trials=300,
    initial_inliers=inliers,
)

fig, ax = plt.subplots()
a_radius = a["Perimeter"] / (2 * np.pi)
for (apx, apy), ar, i in zip(a_pos, a_radius, inliers2):
    ax.add_patch(
        mpatches.Circle((apx, apy), ar, color="tab:blue" if i else "lightgray", ec="darkgray", lw=1)
    )
for bpx, bpy in b_pos:
    ax.add_patch(
        mpatches.Circle((bpx, bpy), max_err, color="none", ec="orange")
    )
for (apx, apy), (bpx, bpy), (mpx, mpy) in zip(a_pos, b_pos[match_b], model(a_pos)):
    ax.plot([apx, bpx], [apy, bpy], color="darkturquoise", lw=1)
    ax.plot([apx, mpx], [apy, mpy], color="darkturquoise", lw=1, ls="--")
for (apx, apy), (bpx, bpy), m in zip(a_pos, b_pos[match_b2], match_b2 == match_b):
    if not m:
        ax.plot([apx, bpx], [apy, bpy], color="limegreen")
ax.set_aspect(1)
plt.show()

print(f"translation: {model2.translation}")
print(f"rotation: {model2.rotation}")
