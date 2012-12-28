import cv2
import sys
import os
import numpy as np
import time
import scipy.io as sio
import math
import cPickle
import linecache
import random
import scipy.spatial.distance as distance
import pyflann
import descriptor_extractor
import sqlite3
import cv2
import crawler

num_lines = 5973294
file_name = "./sift_output.txt"
#paper An Efficient Key Point Quantization Algorithm for Large Scale Image
#Retrieval
#Here we implement this keypoints quantization algorithm with is based on random
# centers

FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
AUTOTUNED = 255
flann_params = dict(algorithm = FLANN_INDEX_KDTREE,
                    trees = 4,
                    target_precision = 1,
                    build_weight = 0.01,
                    memory_weight = 0)


def manhattan_distance(vector_a, vector_b):
    return distance.cityblock(vector_a, vector_b)

def euclidean_distance(vector_a, vector_b):
    return distance.euclidean(vector_a, vector_b)

def calculate_range_distance(total_points):
    #calculated previously
    #mean_distnace = 4044.1130971
    #return mean_distnace

    #sampling randomly 1000 keypoints and calculate the distances for every
    # par. The mean distance * 0.75 is the range distance we need
    f = open(file_name, 'r')
    sequence = range(total_points)
    random.shuffle(sequence)
    sample_size = 1000
    random_seeds = sequence[:sample_size]
    sorted_seeds = sorted(random_seeds)

    current_line = 0
    count_elem = 0
    data_list = [None]*sample_size
    while count_elem < len(sorted_seeds):
        position = sorted_seeds[count_elem]
        for i in range(position - current_line):
            f.readline()
        data_list[count_elem] = f.readline()
        current_line = position + 1
        count_elem += 1

    random_seeds = np.reshape(np.array([int(i) for line in data_list for i in line.split()]), (sample_size,128))
    count = 0
    accumulated_distnaces = 0
    for i in range(sample_size):
        for j in range(sample_size)[i+1:]:
            count += 1
            accumulated_distnaces += euclidean_distance(random_seeds[i,:], random_seeds[j,:])
    mean_distnace = float(accumulated_distnaces) / count
    print mean_distnace, count
    return mean_distnace


def generate_code_book():
    codebook = sio.loadmat('./codebook.mat',struct_as_record=False)['codebook']
    return codebook

    f = open(file_name, 'r')
    sequence = range(5973294)
    random.shuffle(sequence)
    sample_size = 1000000
    sorted_seeds = sorted(sequence[:sample_size])
    current_line = 0
    count_elem = 0
    data_list = [None]*sample_size
    while count_elem < len(sorted_seeds):
        position = sorted_seeds[count_elem]
        for i in range(position - current_line):
            f.readline()
        data_list[count_elem] = f.readline()
        current_line = position + 1
        count_elem += 1

    random_seeds = np.reshape(np.array([int(i) for line in data_list for i in line.split()]), (sample_size,128))
    sio.savemat('codebook.mat',{'codebook':random_seeds})

    return random_seeds

def occurance_distance(v1, v2):
    pass


def create_index(codebook, indexname="codebook.index"):
    flann = pyflann.FLANN()
    #params = flann.build_index(codebook, algorithm="autotuned", target_precision=1, log_level = "info");
    params = flann.build_index(codebook, algorithm="kmeans", max_iterations=15, branching=256, log_level = "info");
    flann.save_index(indexname)
    return flann

def load_index(codebook):
    flann = pyflann.FLANN()
    flann.load_index("codebook.index", codebook)
    return flann


def query_images(indexes, inverted_index, image_codes):
    image_scores = {}
    for key in indexes.keys():
        for image_index in inverted_index[key]:
            image_scores[image_index] = image_scores.setdefault(image_index, 0) +\
            float(min(indexes[key], image_codes[image_index][key])) / max(indexes[key], image_codes[image_index][key])
    return image_scores

def add_image_to_database(image_id, cur, flann, codebook):
    img = crawler.create_opencv_image_from_url(crawler.url%(image_id))
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

    descriptors = np.array(descriptors, dtype=np.int)
    indexes, dists = flann.nn_index(descriptors, 1);

    for i in range(len(indexes)):
        print indexes[i],image_id,attributes[i][0], attributes[i][1]

    #conn.execute("select image_id from word_record where code_id = %d"%(key))

def query_images_in_database(indexes, cur):
    image_scores = {}
    for key in indexes.keys():
        cur.execute("select image_id from word_record where code_id = %d"%(key))
        rows = cur.fetchall()
        print rows
        times_count = {}
        for r in rows:
            times_count[r[0]] = times_count.setdefault(r[0], 0) + 1

        for image_index in times_count.keys():
            image_scores[image_index] = image_scores.setdefault(image_index, 0) +\
            float(min(indexes[key], times_count[image_index])) / max(indexes[key], times_count[image_index])
    return image_scores

def describe_image(image_path, flann, codebook):
    keypoints, descriptors = descriptor_extractor.get_key_points_from_img(image_path)
    indexes = image_encode(descriptors, flann, codebook, 1)
    return indexes


def image_encode(sift_descriptors, flann, codebook, distance):
    sift_descriptors = np.array(sift_descriptors, dtype=np.int)
    indexes, dists = flann.nn_index(sift_descriptors, 1);
    image_code = {}
    for i in indexes:
        image_code[i] = image_code.setdefault(i, 0) + 1

    return image_code

def create_codebook(sift_file_name, num_sifts, codebook_name, num_seeds=1000000):
    sequence = range(num_sifts)
    random_seeds = random.sample(sequence, num_seeds)
    sorted_seeds = sorted(random_seeds)
    f = open(sift_file_name)

    current_line = 0
    count_elem = 0
    data_list = [None]*num_seeds
    while count_elem < len(sorted_seeds):
        position = sorted_seeds[count_elem]
        for i in range(position - current_line):
            f.readline()
        data_list[count_elem] = f.readline()
        current_line = position + 1
        count_elem += 1

    random_seeds = np.reshape(np.array([int(i) for line in data_list for i in line.split()]), (num_seeds,128))
    sio.savemat(codebook_name,{'codebook':random_seeds})



if __name__ == "__main__":
    #create_codebook("./book_cover_sifts.txt", 12654576, "book_cover_codebook.mat")
    codebook = sio.loadmat('./book_cover_codebook.mat',struct_as_record=False)['codebook']
    create_index(codebook, "book_cover_codebook.index")
    exit(1)

    #mean_distnace = calculate_range_distance(num_lines)
    #print mean_distnace

    print "creating codebook"
    codebook = generate_code_book()
    print "creating"
    #flann = create_index(codebook)
    print "loading"
    flann = load_index(codebook)

    num_sifts_img = cPickle.load(open('num_sifts_img.txt','rb'))
    print num_sifts_img

    """
    print "encoding"
    f = open(file_name, 'r')
    current_line = 0
    count = 0
    list_image_codes = [None]*len(num_sifts_img)
    for num_lines in num_sifts_img:
        image_descriptors = [None]*num_lines
        for i in range(num_lines):
            image_descriptors[i] = f.readline()

        image_descriptors = np.reshape(np.array([int(i) for line in image_descriptors for i in line.split()]), (num_lines,128))
        if image_descriptors.shape[0] == 0:
            list_image_codes[count] = {}
        else:
            indexes = image_encode(image_descriptors, flann, codebook, mean_distnace)
        list_image_codes[count] = indexes
        print count
        count += 1
    cPickle.dump(list_image_codes, open('image_codes.txt','wb'))
    """
    image_codes = cPickle.load(open('image_codes.txt','rb'))
    #print image_codes[1]
    inverted_index = cPickle.load(open('inverted_index.txt','rb'))
    """
    inverted_index = {}
    for image_index in range(len(image_codes)):
        for key in image_codes[image_index].keys():
            inverted_index.setdefault(key, []).append(image_index)

    cPickle.dump(inverted_index, open('inverted_index.txt','wb'))
    """
    #print inverted_index[1]


    """
    file_name = "./sift_output.txt"
    sequence = range(5973294)
    random.shuffle(sequence)
    random_seeds = sequence[:1000000]
    #num_lines = sum(1 for line in open('sift_output.txt'))
    #print num_lines
    f = open(file_name)
    for sift_values in f:
        sift_values = [int(i) for i in sift_values]

    """
