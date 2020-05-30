import cv2
import numpy as np


def apply(img):

    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    mean = np.mean(np.abs(laplacian))
    print(mean)
