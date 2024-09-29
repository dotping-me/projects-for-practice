# To graph
import matplotlib.pyplot as plt

# To generate random dataset
from random import randint, choice

def gen_rnd_colour() :
	rnd_rgb = '#'

	for _ in range(6) :
		rnd_rgb += choice('0123456789abcd')

	return	rnd_rgb

def calc_euclidean_dist(xy_1, xy_2) :

	# Pythagoras theorum
	x_side = pow(abs(xy_1[0] - xy_2[0]), 2)
	y_side = pow(abs(xy_1[1] - xy_2[1]), 2)

	return pow(x_side + y_side, 0.5)

def make_clusters(dataset, init_clusters) :
	points_in_clusters = [[] for _ in range(len(init_clusters))]

	# For each point in the dataset
	for i in dataset :

		# Finds nearest cluster
		dist_for_this_point = [calc_euclidean_dist(i, j) for j in init_clusters]
		nearest_cluster     = dist_for_this_point.index(min(dist_for_this_point))

		points_in_clusters[nearest_cluster].append(i)

	return points_in_clusters

def k_means(dataset, k = 3) :
	
	# Step 1
	# Choose k unique points to become initial clusters

	init_clusters = []

	while len(init_clusters) < k :
		centroid = choice(dataset)

		if centroid not in init_clusters :
			init_clusters.append(centroid)

	# Step 2
	# Assign each point to the nearest cluster

	points_in_clusters = make_clusters(dataset, init_clusters)

	# Step 3
	# Calculate means (midpoints) of each cluster

	means_for_each_cluster = []

	for i in range(k) :
		x_points = [j[0] for j in points_in_clusters[i]]
		y_points = [j[1] for j in points_in_clusters[i]]

		length   = len(points_in_clusters[i])
		midpoint = (sum(x_points) / length, sum(y_points) / length)
		
		means_for_each_cluster.append(midpoint)

	# Step 4
	# Re-iterate but by using means of each clusters as initial centroids

	points_in_clusters = make_clusters(dataset, means_for_each_cluster)

	return points_in_clusters, means_for_each_cluster

def plot_graph(xy_coords) :
	x_points = [i[0] for i in xy_coords]
	y_points = [i[1] for i in xy_coords]

	plt.scatter(x_points, y_points, c = 'green', label = 'Cluster 1')
	plt.show()

def plot_clusters(points_in_clusters, init_clusters) :
	colours = ['red', 'yellow', 'blue']

	# Plotting centroids
	for i, centroid in enumerate(init_clusters) :
		plt.scatter(centroid[0], centroid[1], c = colours[i], label = f'Centroid {i + 1}', marker = 'o')

	# Plotting clusters
	for i, points in enumerate(points_in_clusters) :
		x_points = [j[0] for j in points]
		y_points = [j[1] for j in points]

		plt.scatter(x_points, y_points, c = colours[i], label = f'Cluster {i + 1}', marker = '.')
	
	plt.xlabel('# Of Purchases')	
	plt.ylabel('Customer Age')
	plt.legend()

	plt.show()

if __name__ == '__main__' :
	dataset_2_axis = [(randint(0, 1001), randint(1, 101)) for _ in range(100)]

	# Plots initial points
	plot_graph(dataset_2_axis)

	# K Means Clustering

	# 1st iteration
	points_in_clusters, centroid = k_means(dataset_2_axis)
	plot_clusters(points_in_clusters, centroid)