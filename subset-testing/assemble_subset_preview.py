import numpy as np
import skimage
import skimage.exposure
import skimage.io
import sklearn.mixture
import sys
import tifffile


def auto_threshold(img):

    assert img.ndim == 2

    ss = max(*img.shape) // 200
    img = img[::ss, ::ss]
    img_log = np.log(img[img > 0])
    gmm = sklearn.mixture.GaussianMixture(3, max_iter=1000, tol=1e-6)
    gmm.fit(img_log.reshape((-1,1)))
    means = gmm.means_[:, 0]
    covars = gmm.covariances_[:, 0, 0]
    _, i1, i2 = np.argsort(means)

    def fromlog(a):
        return np.round(np.exp(a)).astype(int)

    vmin, vmax = means[[i1, i2]] + covars[[i1, i2]] ** 0.5 * 2
    if vmin >= means[i2]:
        vmin = means[i2] + covars[i2] ** 0.5 * -1
    vmin = max(fromlog(vmin), img.min())
    vmax = min(fromlog(vmax), img.max())

    return vmin, vmax


def rescale(img, vmin, vmax):

    assert img.ndim == 2

    img = (img.astype(np.float32) - vmin) / (vmax - vmin)
    img = np.clip(img, 0, 1)
    img = skimage.exposure.adjust_gamma(img, 1/2.2)
    img = skimage.img_as_ubyte(img)
    return img


images = []

for p in sys.argv[1:]:
    print(p)
    a = tifffile.imread(p, series=0, key=0, level=3)
    b = tifffile.imread(p, series=0, key=5, level=3)
    ar = rescale(a, *auto_threshold(a))
    br = rescale(b, *auto_threshold(b))
    img = np.empty(ar.shape + (3,), np.uint8)
    img[..., 0] = ar
    img[..., 1] = br
    img[..., 2] = ar
    images.append(img)

mind = min(i.shape[:2] for i in images)
images = [i[:mind[0], :mind[1]] for i in images]

img_out = skimage.util.montage(
    images,
    channel_axis=3,
    grid_shape=(2, 3),
    padding_width=30,
)
skimage.io.imsave("preview.jpg", img_out)
