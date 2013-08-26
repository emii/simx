#
# bioinformatics 3, wintersemester 89
# all code by Mathias Bader
#


import sys, os, string, random, time
from math import sqrt
# gives tk namespace for graphical output
import Tkinter as tk 

filename = 'dog.dat'

center_distance = 10.0			# the distance from the middle of the screen to each border
scaling_factor = 1.0			# the zoom-factor (the smaller, the more surface is shown)
zooming = 0						# is the application zooming right now?
zoom_in_border = 1.0			# limit between graph and screen-border for zooming in
zooming_out = 0
circle_diameter = 20			# the diameter of the node-circles
timestep = 0
thermal_energie = 0.0			# set this to 0.3 or 0.0 to (de)activate thermal_energie
all_energies = []				# list of all energies sorted by time
highest_energy = 0				# the highest energie occuring
energie_change_limit = 0.000001	# if energie doesn't change more than this, process is stoped
velocity_maximum = 0.05
friction = 0.0005				# is subtracted from the velocity at each timestep for stop oscillations
show_energies_in_background = 1
status_message = ''
grabed_node = ''
grabed_component = ''
dont_finish_calculating = 0
show_energie_in_background = 1
show_textinformation_in_background = 1

#screen properties
c_width = 800
c_height = 600
border = 50


if (len(sys.argv) == 2 and sys.argv[1] != ""):
	filename = sys.argv[1]


# Class for Nodes
class Node:
	def __init__(self, node_id):
		self.id = node_id		# id (as an integer for example)
		self.neighbour_ids = []	# list of the ids of the neighbours
		self.degree = 0			# number of neighbours
		self.coordinate_x = 0
		self.coordinate_y = 0
		self.force_coulomb = 0
		self.force_harmonic = 0
		self.cc_number = 0 		# the number of the connected component (0 if not assigned yet)
		self.cc_centers = []
		self.velocity = [0,0]	# instead of replacing the nodes, change its velocity to produce inertia
		self.movable = 1
	def getNeighbours(self):
		return self.neighbour_ids
	def getDegree(self):
		return self.degree
	def getId(self):
		return self.id
	def setNeighbour(self, node_id):
		self.neighbour_ids.append(node_id)
		self.degree += 1
	def deleteNeighbour(self, node_id):
		self.neighbour_ids.remove(node_id)
		self.degree -= 1

# Class for graph
class Graph:
	def __init__(self):
		# build an empty graph
		self.nodes = [] # list of Node-objects
		self.edges = [] # list of tupels (node1-id, node2-id) where node1-id is always smaller than node2-id
		self.last_added_id = -1
		self.connected_components_count = 0
		self.overall_energie = 0
		self.overall_energie_difference = 1000
		self.calculation_finished = 0
	
	def addNode(self, node_id):
		# adds a node to the graph
		if node_id == self.last_added_id: return	# speed up adding of same ids consecutively
		for x in self.nodes:
			if x.getId() == node_id:
				return
		self.nodes.append(Node(node_id))
		self.last_added_id = node_id
	
	def addEdge(self, node_id_1, node_id_2):
		# adds an edge between two nodes
		if node_id_1 != node_id_2 and node_id_1 >= 0 and node_id_2 >= 0 and not self.isEdge(node_id_1, node_id_2):
			if node_id_1 < node_id_2:
				self.edges.append((node_id_1, node_id_2))
			else:
				self.edges.append((node_id_2, node_id_1))
			# search for the two node-objects with fitting ids
			node1 = self.getNode(node_id_1)
			node2 = self.getNode(node_id_2)
			node1.setNeighbour(node_id_2)
			node2.setNeighbour(node_id_1)
	
	def deleteEdge(self, (node_id_1, node_id_2)):
		# deletes the edge between node_id_1 and node_id_2
		if node_id_1 > node_id_2:
			# switch the two node-ids (edges are always saved with smaller id first)
			tmp = node_id_1
			node_id_1 = node_id_2
			node_id_2 = tmp
		self.edges.remove((node_id_1, node_id_2))
		node1 = self.getNode(node_id_1)
		node1.deleteNeighbour(node_id_2)
		node2 = self.getNode(node_id_2)
		node2.deleteNeighbour(node_id_1)
	
	def nodesList(self):
		# returns the list of ids of nodes
		list_of_ids = []
		for node in self.nodes:
			list_of_ids.append(node.id)
		return list_of_ids
	
	def edgesList(self):
		# returns the list of edges ([(id, id), (id, id), ...]
		return self.edges
	
	def degreeList(self):
		# returns a dictionary with the degree distribution of the graph
		degrees = {}
		for x in self.nodes:
			if degrees.has_key(x.degree):
				degrees[x.degree] += 1
			else:
				degrees[x.degree] = 1
		return degrees
	
	def countNodes(self):
		# prints the number of nodes
		return len(self.nodes)
	
	def countEdges(self):
		# prints the number of nodes
		return len(self.edges)
	
	def printNodes(self):
		# prints the list of nodes
		to_print = '['
		count = 0
		for x in self.nodes:
			to_print = to_print + str(x.getId()) + ','
			count += 1
			if count > 200:
				print to_print, 
				to_print = ''
				count = 1
		if count > 0: to_print = to_print[:-1]
		to_print = to_print + ']'
		print to_print
	
	def printEdges(self):
		# prints the list of edges
		to_print = '['
		count = 0
		for (n1, n2) in self.edges:
			to_print = to_print + '(' + str(n1) + ',' + str(n2) + '), '
			count += 1
			if count > 200:
				print to_print, 
				to_print = ''
				count = 1
		if count > 0: to_print = to_print[:-2]
		to_print = to_print + ']'
		print to_print
	
	def printData(self):
		# prints number of nodes and edges
		print 'graph with', len(self.nodes), 'nodes and', len(self.edges), 'edges'
		print
		for node in self.nodes:
			print 'x coordinate of', node.id, 'is', node.coordinate_x
			print 'y coordinate of', node.id, 'is', node.coordinate_y
			print
	
	def isEdge(self, node_id_1, node_id_2):
		if node_id_1 > node_id_2:
			# switch the two node-ids (edges are always saved with smaller id first)
			tmp = node_id_1
			node_id_1 = node_id_2
			node_id_2 = tmp
		# checks if there is an edge between two nodes
		for x in self.edges:
			if x == (node_id_1, node_id_2): return True
		return False
	
	def getNode(self, node_id):
		# returns the node for a given id
		for x in self.nodes:
			if x.getId() == node_id:
				return x
	
	def getNodes(self):
		return self.nodes
	
	def SetRandomNodePosition(self):
		# sets random positions for all nodes
		for node in self.nodes:
			node.coordinate_x = random.random() * center_distance - (center_distance/2)
			node.coordinate_y = random.random() * center_distance - (center_distance/2)
	
	def paintGraph(self):
		# (re)Paints the graph on the surface of the window
		
		# clear the screen
		for c_item in c.find_all():
			c.delete(c_item)
		
		# plot the energie vs time in the background of the window
		if show_energie_in_background == 1:
			if show_energies_in_background == 1:
				global all_energies
				energies_count = len(all_energies)
				# only show the last 200 energies at maximum
				if energies_count > 200:
					start_point = energies_count - 200
				else:
					start_point = 0
				for i in range(start_point, energies_count):
					c.create_rectangle(border+(c_width)/(energies_count-start_point)*(i-start_point), border+c_height-(c_height/highest_energy*all_energies[i]), border + (c_width)/(energies_count-start_point)+(c_width)/(energies_count-start_point)*(i-start_point), c_height+border, fill="#eee", outline="#ddd")
		
		
		
		
		# draw the coordinate system with the center
		c.create_line (border, c_height/2+border, (c_width+border), c_height/2+border, fill="#EEEEEE")
		c.create_line (c_width/2+border, border, c_width/2+border, c_height+border*2+border, fill="#EEEEEE")
		
		
		# DRAW AlL EDGES OF THE GRAPH
		for node in g.getNodes():
			# calculate position of this node
			x0 = ((node.coordinate_x*scaling_factor + (center_distance/2)) / center_distance * c_width) + border
			y0 = ((node.coordinate_y*scaling_factor + (center_distance/2)) / center_distance * c_height) + border
			# draw all the edges to neighbors of this node
			for neighbor_id in node.neighbour_ids:
				node2 = self.getNode(neighbor_id)
				if (node.id > node2.id):
					x1 = ((node2.coordinate_x*scaling_factor + (center_distance/2)) / center_distance * c_width) + border
					y1 = ((node2.coordinate_y*scaling_factor + (center_distance/2)) / center_distance * c_height) + border
					c.create_line (x0 + circle_diameter*scaling_factor / 2, y0 + circle_diameter*scaling_factor / 2, x1 + circle_diameter*scaling_factor / 2, y1 + circle_diameter*scaling_factor / 2)

		# DRAW AlL NODES OF THE GRAPH
		for node in g.getNodes():
			# calculate position of this node
			x0 = ((node.coordinate_x*scaling_factor + (center_distance/2)) / center_distance * c_width) + border
			y0 = ((node.coordinate_y*scaling_factor + (center_distance/2)) / center_distance * c_height) + border
			# draw this node
			fill_color = "AAA"
			c.create_oval(x0, y0, x0 + circle_diameter*scaling_factor, y0 + circle_diameter*scaling_factor, fill="#" + fill_color) 
		root.protocol("WM_DELETE_WINDOW", root.destroy)
		root.update()
	
	def calculateStep(self):
		new_overall_energie = 0
		
		# calculate the repulsive force for each node
		for node in self.nodes:
			node.force_coulomb = [0,0]
			for node2 in self.nodes:
				if (node.id != node2.id) and (node.cc_number == node2.cc_number):
					distance_x = node.coordinate_x - node2.coordinate_x
					distance_y = node.coordinate_y - node2.coordinate_y
					radius = sqrt(distance_x*distance_x + distance_y*distance_y)
					if radius != 0:
						vector = [distance_x/radius, distance_y/radius]
						node.force_coulomb[0] += 0.01 * vector[0] / radius
						node.force_coulomb[1] += 0.01 * vector[1] / radius
						# add this force to the overall energie
						new_overall_energie += 0.01 / radius
					else:
						# if the nodes lie on each other, randomly replace them a bit
						node.force_coulomb[0] += random.random() - 0.5
						node.force_coulomb[1] += random.random() - 0.5
		
		# calculate the attractive force for each node
		for node in self.nodes:
			node.force_harmonic = [0,0]
			for neighbor_id in node.neighbour_ids:
				node2 = self.getNode(neighbor_id)
				distance_x = node.coordinate_x - node2.coordinate_x
				distance_y = node.coordinate_y - node2.coordinate_y
				radius = sqrt(distance_x*distance_x + distance_y*distance_y)
				if radius != 0:
					vector = [distance_x/radius* -1, distance_y/radius * -1]
					force_harmonic_x = vector[0] *radius*radius/100
					force_harmonic_y = vector[1] *radius*radius/100
				else:
					# if the nodes lie on each other, randomly replace them a bit
					force_harmonic_x = random.random() - 0.5
					force_harmonic_y = random.random() - 0.5
				node.force_harmonic[0] += force_harmonic_x
				node.force_harmonic[1] += force_harmonic_y
				# add this force to the overall energie
				new_overall_energie += radius*radius/100
		
		# calculate the difference between the old and new overall energie
		self.overall_energie_difference = self.overall_energie - new_overall_energie
		self.overall_energie = new_overall_energie
		all_energies.append(self.overall_energie)
		global highest_energy
		if self.overall_energie > highest_energy:
			highest_energy = self.overall_energie
		if not dont_finish_calculating:
			if (self.overall_energie_difference < energie_change_limit and self.overall_energie_difference > -1*energie_change_limit):
				self.calculation_finished = 1
		
		
		# set the new position influenced by the force
		global thermal_energie
		if timestep == 50 and thermal_energie > 0:
			thermal_energie = 0.2
		if timestep == 110 and thermal_energie > 0:
			thermal_energie = 0.1
		if timestep == 150 and thermal_energie > 0:
			thermal_energie = 0.0
		for node in self.nodes:
			(force_coulomb_x, force_coulomb_y) = node.force_coulomb
			(force_harmonic_x, force_harmonic_y) = node.force_harmonic
			# node.coordinate_x += force_coulomb_x + force_harmonic_x
			# node.coordinate_y += force_coulomb_y + force_harmonic_y
			
			node.velocity[0] += (force_coulomb_x + force_harmonic_x)*0.1
			node.velocity[1] += (force_coulomb_y + force_harmonic_y)*0.1
			# ensure maximum velocity
			if (node.velocity[0] > velocity_maximum):
				node.velocity[0] = velocity_maximum
			if (node.velocity[1] > velocity_maximum):
				node.velocity[1] = velocity_maximum
			if (node.velocity[0] < -1*velocity_maximum):
				node.velocity[0] = -1*velocity_maximum
			if (node.velocity[1] < -1*velocity_maximum):
				node.velocity[1] = -1*velocity_maximum
			# get friction into play
			if node.velocity[0] > friction:
				node.velocity[0] -= friction
			if node.velocity[0] < -1*friction:
				node.velocity[0] += friction
			if node.velocity[1] > friction:
				node.velocity[1] -= friction
			if node.velocity[1] < -1*friction:
				node.velocity[1] += friction
			
			# FINALLY SET THE NEW POSITION
			if node.id != grabed_node or node.cc_number == grabed_component:
				if node.movable == 1:
					node.coordinate_x += node.velocity[0]
					node.coordinate_y += node.velocity[1]
			
			if thermal_energie > 0:
				if node.movable == 1:
					node.coordinate_x += random.random()*thermal_energie*2-thermal_energie
					node.coordinate_y += random.random()*thermal_energie*2-thermal_energie
		
		# calculate centers for all connected components
		min_max = []
		center = []
		for i in range(0, self.connected_components_count):
			min_max.append([1000,1000,-1000,-1000])
		for i in range(0, self.connected_components_count):
			for node in self.getNodes():
				if node.cc_number == i+1:
					if node.coordinate_x < min_max[i][0]:
						min_max[i][0] = node.coordinate_x
					if node.coordinate_y < min_max[i][1]:
						min_max[i][1] = node.coordinate_y
					if node.coordinate_x > min_max[i][2]:
						min_max[i][2] = node.coordinate_x
					if node.coordinate_y > min_max[i][3]:
						min_max[i][3] = node.coordinate_y
			center.append([min_max[i][0] + (min_max[i][2] - min_max[i][0])/2, min_max[i][1] + (min_max[i][3] - min_max[i][1])/2])
		
		# if two components lie on each other, increase the distance between those
		for a in range(0, self.connected_components_count):
			for b in range(0, self.connected_components_count):
				# if a != b and center[a][0] > min_max[b][0] and center[a][0] < min_max[b][2] and center[a][1] > min_max[b][1] and center[a][1] < min_max[b][3]:
				if a != b:
					distance = 1
					if ((min_max[a][0]+distance > min_max[b][0] and min_max[a][0]-distance < min_max[b][2]) or (min_max[a][2]+distance > min_max[b][0] and min_max[a][2]-distance < min_max[b][2])) and ((min_max[a][1]+distance > min_max[b][1] and min_max[a][1]-distance < min_max[b][3]) or (min_max[a][3]+distance > min_max[b][1] and min_max[a][3]-distance < min_max[b][3])):
						# calculate replacement with help of the distance vector
						# of the centers
						distance_x = center[a][0] - center[b][0]
						distance_y = center[a][1] - center[b][1]
						radius = sqrt(distance_x*distance_x + distance_y*distance_y)
						replacement = [distance_x/radius* -1, distance_y/radius * -1]
						replacement[0] *= random.random() * -0.1
						replacement[1] *= random.random() * -0.1
						for node in self.nodes:
							if node.cc_number == a+1:
								if node.id != grabed_node:
									if node.movable == 1:
										node.coordinate_x += replacement[0]
										node.coordinate_y += replacement[1]
		
		# calculate the center of the graph and position all nodes new, so that 
		# the center becomes (0,0)
		x_max = -1000
		x_min = 1000
		y_max = -1000
		y_min = 1000
		for node in self.getNodes():
			if node.coordinate_x < x_min:
				x_min = node.coordinate_x
			if node.coordinate_x > x_max:
				x_max = node.coordinate_x
			if node.coordinate_y < y_min:
				y_min = node.coordinate_y
			if node.coordinate_y > y_max:
				y_max = node.coordinate_y
		center_x = x_min + (x_max - x_min)/2
		center_y = y_min + (y_max - y_min)/2
		for node in g.getNodes():
			if node.id != grabed_node:
				node.coordinate_x -= center_x
				node.coordinate_y -= center_y
		
		scale = 0
		# prevent nodes from leaving the screen - ZOOM OUT
		if (x_min < (center_distance/scaling_factor/-2)) or (y_min < (center_distance/scaling_factor/-2)) or (x_max > (center_distance/scaling_factor/2)):
			scale = 1
		# longer if-statement because node-caption is included
		if (y_max > (center_distance/scaling_factor/2)-((circle_diameter+20)*scaling_factor*center_distance/c_height)):
			scale = 1
		# zoom back in if necessary - ZOOM IN
		if (x_min - zoom_in_border > (center_distance/scaling_factor/-2)) and (y_min - zoom_in_border > (center_distance/scaling_factor/-2)) and (x_max + zoom_in_border < (center_distance/scaling_factor/2)) and (y_max + zoom_in_border < (center_distance/scaling_factor/2)-((circle_diameter+10)*scaling_factor*center_distance/c_height)):
			scale = -1
		
		if scale == 1:
			# zoom out
			global scaling_factor
			global zooming
			global zooming_out
			scaling_factor = scaling_factor * 0.99
			zooming = 50
			zooming_out = 1
		else:
			# zoom in
			if scale == -1:
				global scaling_factor
				global zooming
				global zooming_out
				scaling_factor = scaling_factor * 1.01
				zooming = 50
				zooming_out = 0
			else:
				# don't zoom (count down the fading for the zooming message)
				global zooming
				if zooming > 0:
					zooming -= 1
	
	def calculateConnectedComponents(self):
		# calculate the connected components of the graph
		all_node_ids = []
		for node in self.nodes:
			all_node_ids.append(node.id)
		visited_node_ids = []
		node_ids_to_process = []
		connected_component_number = 0
		while len(all_node_ids) > 0:
			# take an anchor node
			node_ids_to_process.append(all_node_ids.pop())
			connected_component_number += 1
			# process all nodes that are reachable from the anchor-node
			while len(node_ids_to_process) > 0:
				anchor_node_id = node_ids_to_process.pop()
				# set the anchors cc_number and add all neighbors to the process 
				# list that haven't been yet
				anchor_node = self.getNode(anchor_node_id)
				anchor_node.cc_number = connected_component_number
				for neighbor_node_id in anchor_node.neighbour_ids:
					if not neighbor_node_id in visited_node_ids:
						node_ids_to_process.append(neighbor_node_id)
						if neighbor_node_id in all_node_ids:
							all_node_ids.remove(neighbor_node_id)
				# this node is finished
				visited_node_ids.append(anchor_node_id)
		self.connected_components_count = connected_component_number
	
	def empty(self):
		self.clear()
	def clear(self):
		# deletes all nodes and edges in the graph
		self.nodes = []
		self.edges = []

	
print 'creating graph ...'
g = Graph()
# find the line where the graph starts
for n1 in range(5):
	for n2 in range(5):
		g.addNode(n1)
		g.addNode(n2)
		if n1%2 == 0:
			g.addEdge(n1,n2)

# calculate the connected components:
g.calculateConnectedComponents()

# set the position of all nodes in the graph randomly to 
# a number between 0 and 10
g.SetRandomNodePosition()

# create the window object for painting the graph on
root = tk.Tk()
root.title("Force directed layout of graphs")
c = tk.Canvas(root, width=c_width+2*border, height=c_height+2*border, bg='white')
c.pack()
c.focus_set()

g.paintGraph()
while (not g.calculation_finished or dont_finish_calculating):
	g.calculateStep()
	timestep += 1
	g.paintGraph()
g.paintGraph()

c.mainloop()













