from tabnanny import check
from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import json
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import random

# randomly initialize dataset


app = Flask(__name__)

def generateData():
    newarr = np.c_[np.random.uniform(-10, 10, 100), np.random.uniform(-10, 10, 100)]
    return newarr

def generateCentroids(init_t, k):
    global oldarr
    if init_t=="Random":
        idx = np.random.choice(len(oldarr), k, replace=False)
        #Randomly choosing Centroids 
        ncentroids = oldarr[idx, :]
    elif init_t=="Farthest First":
        ncentroids = []
        random_index = np.random.randint(0, len(oldarr) - 1)  # Start with one random centroid
        ncentroids.append(oldarr[random_index])

        while len(ncentroids) < k:
            max_dist = -1
            farthest_point = None
            for point in oldarr:
                ddist = [(c[0]-point[0])**2+(c[1]-point[1])**2 for c in ncentroids]
                print("ddist")
                print(ddist)
                min_dist_to_centroid = min(ddist)
                if min_dist_to_centroid > max_dist:
                    max_dist = min_dist_to_centroid
                    farthest_point = point
            ncentroids.append(farthest_point)
        ncentroids = np.reshape(ncentroids, (k, 2))
    elif init_t=="KMeans++":
        ncentroids = []
        # Pick the first centroid randomly
        random_index = np.random.randint(0, len(oldarr) - 1)
        ncentroids.append(oldarr[random_index])

        # Select remaining centroids with a probability proportional to their distance from existing centroids
        while len(ncentroids) < k:
            distances = [min([(c[0]-point[0])**2+(c[1]-point[1])**2 for c in ncentroids]) for point in oldarr]
            sum_distances = sum(distances)
            probs = [d / sum_distances for d in distances]
            cumulative_probs = np.cumsum(probs)
            print("cumulative_probs")
            print(cumulative_probs)
            rand = random.random()
            nxt = next(i for i, p in enumerate(cumulative_probs) if p >= rand)
            ncentroids.append(oldarr[nxt])

        ncentroids = np.reshape(ncentroids, (k, 2))
    global chex
    chex = np.arange(0, 1, 1/k)
    return ncentroids


   
oldarr = generateData()
centroids = np.array([])
colors = np.full(100, 1)
arr = np.c_[oldarr, colors]
chex = np.array([])

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/getdata")
def getdata():
    global arr
    return jsonify(arr.tolist())


@app.route("/getcentroids")
def getcentroids():
    global centroids
    global chex
    print("chex")
    print(chex)
    return jsonify(np.c_[centroids, chex].tolist())

@app.route("/reset", methods=['POST'])
def reset():
    global centroids
    global chex
    centroids = np.array([])
    chex = np.array([])
    return render_template('index.html')

@app.route("/gennew", methods=['POST'])
def gennew():
    global arr
    global oldarr
    oldarr = generateData()
    colors = np.full(100, 1)
    arr = np.c_[oldarr, colors]
    return render_template('index.html')


@app.route('/converge', methods=['POST'])
def converge():
    n_clust = int(request.form['n_clust'])
    init_type = request.form['init_type']
    lk1 = request.form['lk1']
    global oldarr 
    global centroids
    global chex
    if len(centroids) != n_clust:
        if init_type=="Manual":
            mcent = np.asarray(json.loads(request.form['mcentroids']))
            print("mcent")
            print(mcent)
            centroids = []
            for m in mcent:
                centroids.append((m[0]-260)/26)
                centroids.append((m[1]-260)/24)
            centroids = np.reshape(centroids, (n_clust, 2))
            chex = np.arange(0, 1, 1/n_clust)
            print(centroids)
        else:
            centroids = generateCentroids(init_type, n_clust)
    
    pastcent = np.zeros((np.shape(centroids)))
    while checkconverge(pastcent, centroids)==False:
        pastcent = centroids
        labels = kmeans(oldarr, n_clust, centroids, 100)


    labels = np.divide(labels, n_clust)

    chex = np.arange(0, 1, 1/n_clust)
    global arr
    arr = np.c_[oldarr, labels]
    return render_template('index.html')
   
@app.route('/kmplus', methods=['POST'])   
def kmplus():
    n_clust = int(request.form['n_clust'])
    init_type = request.form['init_type']
    lk1 = request.form['lk1']
    global oldarr 
    global centroids
    global chex
    if len(centroids) != n_clust:
        if init_type=="Manual":
            mcent = np.asarray(json.loads(request.form['mcentroids']))
            print("mcent")
            print(mcent)
            centroids = []
            for m in mcent:
                centroids.append((m[0]-260)/26)
                centroids.append((m[1]-260)/24)
            centroids = np.reshape(centroids, (n_clust, 2))
            print(centroids)
            chex = np.arange(0, 1, 1/n_clust)
        else:
            centroids = generateCentroids(init_type, n_clust)

    labels = kmeans(oldarr, n_clust, centroids, 1)
    labels = np.divide(labels, n_clust)

    # Take colors at regular intervals spanning the colormap.
    #cmap = colormaps['Spectral']
    #colors = cmap(np.linspace(0, 1, n_clust))
    #chex = ['#%02x%02x%02x' % (int(255 * i[0]), int(255 * i[1]), int(255 * i[2])) for i in colors]
    chex = np.arange(0, 1, 1/n_clust)
    #global clab
    #clab = [chex[i] for i in labels]
    global arr
    arr = np.c_[oldarr, labels]

    return render_template('index.html')

def checkconverge(oldc, newc, tol=1e-4):
    cpoints = [(a[0]-b[0])**2+(a[1]-b[1])**2 for (a, b) in zip(oldc, newc)]
    print(cpoints)
    if sum(cpoints) > tol:
        return False
    return True

def kmeans(df, k, cent, iter):
    print("kmeans cent")
    print(cent)
    distances = cdist(df, cent ,'euclidean')
    points = np.array([np.argmin(i) for i in distances]) 
    oldcent = cent
    for _ in range(iter): 
        newcent = []
        for idx in range(k):
            #Updating Centroids by taking mean of Cluster it belongs to
            temp_cent = df[points==idx].mean(axis=0) 
            newcent.append(temp_cent)
 
        newcent = np.vstack(newcent) #Updated Centroids 
         
        distances = cdist(df, newcent ,'euclidean')
        points = np.array([np.argmin(i) for i in distances])
        #if checkconverge(oldcent, newcent):
        #    break
        oldcent = newcent

    global centroids
    centroids = newcent
    return points


if __name__ == '__main__':
    app.run(port=3000, debug=True)