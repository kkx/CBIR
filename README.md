A CBIR system
Background:  Images retrieval

based on SIFT keypoints,  bag of words approach and test retrieval system.
2 dataset used to get the performance of this approach. Oxford-5000, 1 million douban
book cover images.

No test performance metric is used here, simply test each case manually, so neither performace rate reported here.
The results are not satisfactory for large dataset(douban). I've tried to solve semantic gap by adding spatial
information. More researches have to be done to deal with large dataset.

I think this system can be used for near-duplicated image detection which is what i wanted in the first instant :)

NOTE:  Don't ever try to use my codes, They are dirty, bad organized and coupling. Uploaded here just for backup purpose.
----------------

The whole system construction process is:
*   collect image data and extract feature vectors(crawler.py, descriptor_extractor.py)
*   Using a subset of collected images to create a BOW codebook(create_bag_words.py),
    Here i've used 100,000 images to create a 1M words by random sampling(An Efficient Key Point Quantization Algorithm for Large Scale Image Retrieval)
    (I haven't used ranged search for simplicity, so each keypoint is classified into only un cluster)
*   Qualificate sift vectores of rest of images. And index all of them like a test search engine to create a inverted index.
*   You can query most similar images for a test image  by using query.py

Firstly i built the inverted index through python dict, luckly the whole inverted index can fit into ram memory for the Oxford-5000
problem. But in the 1-million douban images dataset, i had to put the whole index into a database(using inverted-index on fields) which prolonged the query time.

Some works followed here:
*   Indexing in Large Scale Image Collections- Scaling Properties and Benchmark
*   Efficient clustering and matching for object class recognition
*   Object retrieval with large vocabularies and fast spatial matching
*   An Effient Key Point Quantization Algorithm for Large Scale Image Retrieval
*   Large-scale near-duplicate image retrieval by kernel density estimation

Most of these work used Mikolajczyk's Harris-Affine and Hessian Affine detector
Its public available, but it's in binary. Here i just used opencv's SIFT for detection and description
for simplicity and so it is pure python based :).

Some third party libraries used here:
*   numpy, scipy, opencv, the basic ones.
*   flann: pyflann is the best choice, since the opencv.flann libraries didn't work like i had expected
*   twisted: a simply web service is implemented to upload images and get ranked results.

An advice: Don't use sqlite for a dataset with more then 100 millions records.


