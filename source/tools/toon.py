"""Crop a face from a photo and give it a cartoon look (flat colours + bold outlines), circle-masked PNG."""
import sys
import cv2
import numpy as np

def toon(src, cx, cy, half, out, size=320):
    img = cv2.imread(src)
    h, w = img.shape[:2]
    x0, y0 = max(0, cx - half), max(0, cy - half)
    x1, y1 = min(w, cx + half), min(h, cy + half)
    crop = cv2.resize(img[y0:y1, x0:x1], (size, size), interpolation=cv2.INTER_AREA)
    # gentle grey-world white balance so warm sunset light doesn't turn skin red
    f = crop.astype(np.float32)
    means = f.reshape(-1, 3).mean(0)
    f = f * (0.5 + 0.5 * means.mean() / means)
    crop = np.clip(f, 0, 255).astype(np.uint8)

    # smooth into flat areas while keeping edges
    smooth = crop.copy()
    for _ in range(5):
        smooth = cv2.bilateralFilter(smooth, 9, 60, 60)
    # reduce to a small palette
    data = smooth.reshape((-1, 3)).astype(np.float32)
    k = 10
    _, labels, centers = cv2.kmeans(data, k, None,
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0),
                                    4, cv2.KMEANS_PP_CENTERS)
    flat = centers.astype(np.uint8)[labels.flatten()].reshape(smooth.shape)
    # a little extra colour
    hsv = cv2.cvtColor(flat, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 0.95, 0, 255)
    hsv[..., 2] = np.clip(255 * (hsv[..., 2] / 255) ** 0.8, 0, 255)  # lift shadows a little
    flat = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    # bold outlines, only the strong ones
    gray = cv2.medianBlur(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), 9)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 9)
    # drop tiny specks of outline
    inv = 255 - edges
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv, 8)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 40:
            inv[lab == i] = 0
    edges = 255 - inv
    cartoon = cv2.bitwise_and(flat, flat, mask=edges)

    # keep only the head: an oval around it, everything else becomes the team colour
    oval = np.zeros((size, size), np.uint8)
    cv2.ellipse(oval, (int(size * OX), int(size * OY)), (int(size * AX), int(size * AY)), 0, 0, 360, 255, -1)
    oval = cv2.GaussianBlur(oval, (0, 0), 3).astype(np.float32)[..., None] / 255.0
    team = np.zeros_like(cartoon); team[:] = BG
    cartoon = (cartoon * oval + team * (1 - oval)).astype(np.uint8)
    cv2.ellipse(cartoon, (int(size * OX), int(size * OY)), (int(size * AX), int(size * AY)), 0, 0, 360, (20, 16, 26), 3)

    # circle mask -> transparent PNG
    mask = np.zeros((size, size), np.uint8)
    cv2.circle(mask, (size // 2, size // 2), size // 2 - 2, 255, -1)
    rgba = cv2.cvtColor(cartoon, cv2.COLOR_BGR2BGRA)
    rgba[..., 3] = mask
    cv2.imwrite(out, rgba)

OX, OY, AX, AY, BG = 0.5, 0.5, 0.36, 0.45, (228, 111, 47)

if __name__ == "__main__":
    src, cx, cy, half, out = sys.argv[1], *map(int, sys.argv[2:5]), sys.argv[5]
    OX, OY, AX, AY = map(float, sys.argv[6:10])
    BG = tuple(int(sys.argv[10][i:i + 2], 16) for i in (4, 2, 0))  # hex RRGGBB -> BGR
    toon(src, cx, cy, half, out)
