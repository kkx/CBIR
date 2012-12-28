import descriptor_extractor
import create_bag_words
import cPickle
import time
import numpy as np
import operator
import os
import sqlite3
import MySQLdb
import cv2
import math
import scipy.ndimage


conn=MySQLdb.connect(host="localhost",user="root",passwd="xxxxx",db="book_cover",charset="utf8")
cur = conn.cursor()
codebook = create_bag_words.generate_code_book()
flann = create_bag_words.load_index(codebook)

def query(image_path):
    #"""
    indexes = create_bag_words.describe_image(image_path, flann, codebook)
    image_scores = create_bag_words.query_images_in_database(indexes, cur)
    print image_scores
    return image_scores
    """

    img = cv2.imread(image_path)
    if len(img.shape)>2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    keypoints, descriptors = descriptor_extractor.get_key_points_from_img(img)
    #indexes = image_encode(descriptors, flann, codebook, 1)
    descriptors = np.array(descriptors, dtype=np.int)
    indexes, dists = flann.nn_index(descriptors, 1);
    #indexes = create_bag_words.describe_image(image_path, flann, codebook)
    #image_scores = create_bag_words.query_images_in_database(indexes, cur)
    image_scores = {}
    image_maps = {}


    votes = {}
    #print len(keypoints), len(descriptors), len(indexes)
    for i in range(len(indexes)):
        cur.execute("select image_id,dx,dy from word_record where code_id = %d"%(indexes[i]))
        rows = cur.fetchall()
        print rows
        for r in rows:
            votes.setdefault(r[0],[]).append([r[1],r[2]])

    for image_id in votes.keys():
        if len(votes[image_id]) < 5:
            continue
        image_map = np.zeros(img.shape)
        for vote in votes[image_id]:
            scale = keypoints[i].size
            gradient = math.radians(keypoints[i].angle)

            d_x = vote[0]*scale
            d_y = vote[1]*scale
            #print d_y, d_x
            tx = math.cos(-gradient) * d_x - math.sin(-gradient) * d_y
            ty = math.sin(-gradient) * d_x + math.cos(-gradient) * d_y
            #print tx, ty
            predicted_center_x = int(round(keypoints[i].pt[0]+tx))
            predicted_center_y = int(round(keypoints[i].pt[1]+ty))
            #print attributes[i][0], attributes[i][1]
            #print attributes[i][0], attributes[i][1],
            #print predicted_center_x, predicted_center_y
            if (predicted_center_x>=0) and (predicted_center_y>=0) and (predicted_center_x<img.shape[1]) and (predicted_center_y<img.shape[0]):
                image_map[predicted_center_y][predicted_center_x] += 1.0
        #image_scores[image_id] = scipy.ndimage.gaussian_filter(image_map, sigma=10).max()
        image_scores[image_id] = scipy.ndimage.uniform_filter(image_map, size=30).max()
        print image_scores[image_id]
    return image_scores
    """
    print image_scores
    return image_scores


if __name__ == "__main__":
    create_bag_words.add_image_to_database(9114855, cur, flann, codebook)
    exit(1)
    #image_path = "./data/oxford5000/all_souls_000006.jpg"
    image_path = "./oxford02.jpg"
    image_path = "./oxford_street_.jpg"
    image_path = "./Curso-de-ingles-en-Oxford-Inglaterra__0000000003000000000093002.gif"
    image_path = "./Oxford_Balloon_1.jpg"
    image_path = "./s9114855.jpg"

    codebook = create_bag_words.generate_code_book()
    flann = create_bag_words.load_index(codebook)
    image_codes = cPickle.load(open('image_codes.txt','rb'))
    inverted_index = cPickle.load(open('inverted_index.txt','rb'))


    files = os.listdir("./data/oxford5000/")

    print "start query"
    start = time.time()
    indexes = create_bag_words.describe_image(image_path, flann, codebook)
    image_scores = create_bag_words.query_images(indexes, inverted_index, image_codes)

    print indexes.values()
    print len(indexes.keys())

    """
    image_scores = {}
    for key in indexes.keys():
        for image_index in inverted_index[key]:
            image_scores[image_index] = image_scores.setdefault(image_index, 0) +\
            float(min(indexes[key], image_codes[image_index][key])) / max(indexes[key], image_codes[image_index][key])
    """

    sorted_image_scores = sorted(image_scores.iteritems(), key=operator.itemgetter(1))
    print sorted_image_scores
    print len(sorted_image_scores)
    print time.time()-start
    for i in sorted_image_scores[-40:]:
        print files[i[0]], i[1]


    image_path = "./IMG_20121224_124839.jpg"
    indexes2 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes2.keys())
    image_scores = 0
    for key in indexes2.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes2[key])) / max(indexes[key], indexes2[key])
    print image_scores

    image_path = "./IMG_20121224_124851.jpg"
    indexes3 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes3.keys())
    image_scores = 0
    for key in indexes3.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes3[key])) / max(indexes[key], indexes3[key])
    print image_scores

    image_path = "./IMG_20121224_145333.jpg"
    indexes4 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes4.keys())
    image_scores = 0
    for key in indexes4.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes4[key])) / max(indexes[key], indexes4[key])
    print image_scores

    image_path = "./IMG_20121224_151142.jpg"
    indexes4 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes4.keys())
    image_scores = 0
    for key in indexes4.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes4[key])) / max(indexes[key], indexes4[key])
    print image_scores

    image_path = "./IMG_20121224_151154_1.jpg"
    indexes4 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes4.keys())
    image_scores = 0
    for key in indexes4.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes4[key])) / max(indexes[key], indexes4[key])
    print image_scores

    image_path = "./IMG_20121224_152932.jpg"
    indexes4 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes4.keys())
    image_scores = 0
    for key in indexes4.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes4[key])) / max(indexes[key], indexes4[key])
    print image_scores

    image_path = "./IMG_20121224_152939.jpg"
    indexes4 = create_bag_words.describe_image(image_path, flann, codebook)
    print len(indexes4.keys())
    image_scores = 0
    for key in indexes4.keys():
        if key in indexes:
            image_scores += float(min(indexes[key], indexes4[key])) / max(indexes[key], indexes4[key])
    print image_scores

    image_scores = 0
    for key in indexes2.keys():
        if key in indexes3:
            image_scores += float(min(indexes2[key], indexes3[key])) / max(indexes2[key], indexes3[key])
    print image_scores
