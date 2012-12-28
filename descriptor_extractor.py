import cv2
import sys
import os
import numpy as np
import scipy.io as sio
import cPickle

FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
AUTOTUNED = 255
flann_params = dict(algorithm = FLANN_INDEX_KDTREE,
                    trees = 4,
                    target_precision = 1,
                    build_weight = 0.01,
                    memory_weight = 0)

def get_key_points_from_img(img):
    if isinstance(img,str):
        img = cv2.imread(img)
    if len(img.shape)>2:
        im = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        im = img 

    surfDetector = cv2.FeatureDetector_create("SIFT")
    surfDescriptorExtractor = cv2.DescriptorExtractor_create("SIFT")
    keypoints = surfDetector.detect(im)
    
    (keypoints, descriptors) = surfDescriptorExtractor.compute(im, keypoints)
    return (keypoints, descriptors)


if __name__ == "__main__":

    #stone_flies_train=sio.loadmat('./sifts.mat',struct_as_record=False)['sifts']
    num_sifts_img = cPickle.load(open('num_sifts_img.txt','rb'))
    #print stone_flies_train
    print num_sifts_img
    count = 0
    for  i in range(len(num_sifts_img)):
        num_sifts_img[i] += count
        count = num_sifts_img[i]
    print num_sifts_img
    exit(1)

    import time
    path = "./data/oxford5000/"
    files = os.listdir(path)
    #train_descriptors = np.array([0]*128, dtype=np.int16)
    num_sifts_img = len(files)*[None]
    num_sifts_img[0] = 0
    
    (keypoints, descriptors) = (get_key_points_from_img(path + files[0]))
    descriptors =  np.array(descriptors, dtype=np.int16)
    train_descriptors = descriptors
    print train_descriptors.shape

    count = 0
    sift_output = open("./sift_output.txt","w")
    for i in range(len(files))[:]:
        print i, files[i]
        (keypoints, descriptors) = (get_key_points_from_img(path + files[i]))
        if descriptors == None:
            descriptors = []
        else:
            #descriptors =  np.array(descriptors, dtype=np.int16)

            for d in descriptors:
                d = [str(int(k)) for k in list(d)]
                sift_output.write(" ".join(d)+"\n")

            #train_descriptors = np.vstack((train_descriptors,descriptors))
        num_sifts_img[i] = count + len(descriptors)
        count = num_sifts_img[i]

    #train_descriptors = np.array(train_descriptors, dtype=np.int16)
    print train_descriptors.shape
    sift_output.close() 
    cPickle.dump(num_sifts_img, open('num_sifts_img.txt','wb'))
    #sio.savemat('sifts.mat',{'sifts':train_descriptors})       

    
