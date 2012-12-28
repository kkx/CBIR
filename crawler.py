#! /usr/bin/env python
import Image
import time
import urllib
import cv2
import cv
import math
import numpy as np
import cv2
import numpy as np
from urllib2 import urlopen
from cStringIO import StringIO
#from multiprocessing import Process, Queue
import multiprocessing, Queue
import cPickle
import scipy.io as sio
import create_bag_words

url = "http://img3.douban.com/lpic/s%d.jpg"
init = 24211018
fin =  24223033

def create_opencv_image_from_stringio(img_stream, cv2_img_flag=0):
    img_stream.seek(0)
    img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2_img_flag)

def create_opencv_image_from_url(url, cv2_img_flag=0):
    request = urlopen(url)
    img_array = np.asarray(bytearray(request.read()), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2_img_flag)

class Worker(multiprocessing.Process):

    def __init__(self, work_queue, result_queue):

        # base class initialization
        multiprocessing.Process.__init__(self)
        # job management stuff
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.kill_received = False

    def run(self):
        while not self.kill_received:
            if self.result_queue.qsize() > 500:
                time.sleep(3)
                continue

            job = self.work_queue.get()
            image_id = job
            try:
                img = create_opencv_image_from_url(url%(image_id))
                surfDetector = cv2.FeatureDetector_create("SIFT")
                surfDescriptorExtractor = cv2.DescriptorExtractor_create("SIFT")
                keypoints = surfDetector.detect(img)
                (keypoints, descriptors) = surfDescriptorExtractor.compute(img, keypoints)
                center = (img.shape[0]/2, img.shape[1]/2)
                attributes = [None] * len(keypoints)
                for i in range(len(keypoints)):
                    kp = keypoints[i]
                    d_x = center[1]-kp.pt[0]
                    d_y = center[0]-kp.pt[1]
                    gradient = math.radians(kp.angle)
                    scale = kp.size
                    tx = math.cos(gradient) * d_x - math.sin(gradient) * d_y
                    tx /= scale
                    ty = math.sin(gradient) * d_x + math.cos(gradient) * d_y
                    ty /= scale
                    attributes[i] = [tx,ty]
                self.result_queue.put((image_id, attributes, descriptors))
            except:
                print job
                self.result_queue.put((-1, [], []))


def download_codebook_images():
    """
    Download 100000 images to create a codebook
    """

    init = 24123033
    num_jobs = 100000
    num_processes=100
    # run
    # load up work queue
    work_queue = multiprocessing.Queue()
    for job in range(num_jobs):
        work_queue.put(init+job)

    # create a queue to pass to workers to store the results
    result_queue = multiprocessing.Queue()

    # spawn workers
    for i in range(num_processes):
        worker = Worker(work_queue, result_queue)
        worker.start()

    # collect the results off the queue
    results = []
    num_sifts_img = num_jobs*[None]

    image_attributes = {}
    f = open("book_cover_sifts","wb")
    count = 0
    for i in range(num_jobs):
        print i
        image_id, attributes, descriptors = result_queue.get()
        image_attributes[image_id] = attributes
        if descriptors == None:
            length = 0
        else:
            #descriptors =  np.array(descriptors, dtype=np.int16)
            for d in descriptors:
                d = [str(int(k)) for k in list(d)]
                f.write(" ".join(d)+"\n")
            length = len(descriptors)

        num_sifts_img[image_id-init] = count + length
        count = num_sifts_img[image_id-init]
    f.close()
    cPickle.dump(image_attributes, open('book_cover_image_attributes.txt','wb'))
    cPickle.dump(num_sifts_img, open('book_cover_num_sifts_img.txt','wb'))


if __name__ == "__main__":

    num_jobs = 100000
    num_processes=70

    # run
    # load up work queue
    work_queue = multiprocessing.Queue()

    # donwload images reversely
    for job in range(num_jobs):
        work_queue.put(fin-job)

    # create a queue to pass to workers to store the results
    result_queue = multiprocessing.Queue()

    list_works = []
    # spawn workers
    for i in range(num_processes):
        worker = Worker(work_queue, result_queue)
        worker.start()
        list_works.append(worker)

    # collect the results off the queue
    num_sifts_img = num_jobs*[None]

    image_attributes = {}
    codebook = sio.loadmat('./book_cover_codebook.mat',struct_as_record=False)['codebook']
    flann = create_bag_words.load_index(codebook)

    count = 0
    image_codes = {}
    inverted_index = {}
    f = open("book_cover_image_codes.txt","wb")
    error_count = 0
    for i in range(num_jobs):
        image_id, attributes, descriptors = result_queue.get()
        if image_id == -1:
            error_count += 1
            print "num_errors", error_count # error due to no valid images
            continue
        if descriptors == None:
            pass
        else:
            descriptors = np.array(descriptors, dtype=np.int)
            indexes, dists = flann.nn_index(descriptors, 1);

            for j in range(len(indexes)):
                f.write("%d %d %.2f %.2f\n"%(image_id, indexes[j], attributes[j][0], attributes[j][1]))

        if (i % 1000) == 0:
            print i, result_queue.qsize()
        if (i % 100000) == 0:
            print i, "images processed"

    print "saving"
    f.close()
    print "saved"


