import sys
from PIL import Image
import copy

from Queue import PriorityQueue
import time 

class ReversePriorityQueue(PriorityQueue):

	def put(self, tup):
		newtup = tup[0] * -1, tup[1], tup[2]
		PriorityQueue.put(self, newtup)
	
	def get(self):
		tup = PriorityQueue.get(self)
		newtup = tup[0] * -1, tup[1], tup[2]
		return newtup

'''
These variables are determined at runtime and should not be changed or mutated by you
'''
start = (0, 0)  # a single (x,y) tuple, representing the start position of the search algorithm
end = (0, 0)    # a single (x,y) tuple, representing the end position of the search algorithm
difficulty = "" # a string reference to the original import file

'''
These variables determine display color, and can be changed by you, I guess
'''

PURPLE = (85, 26, 139)
LIGHT_GRAY = (50, 50, 50)
DARK_GRAY = (100, 100, 100)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

G = 1e15
E = 1e15

'''
These variables are determined and filled algorithmically, and are expected (and required) be mutated by you
'''
path = []       # an ordered list of (x,y) tuples, representing the path to traverse from start-->goal
expanded = {}   # a dictionary of (x,y) tuples, representing nodes that have been expanded
frontier = {}   # a dictionary of (x,y) tuples, representing nodes to expand to in the future

def heuristic(a, b):
	(x1, y1) = a
	(x2, y2) = b
	h = abs(x2 - x1) + abs(y2 - y1) # Manhattan Distance
	return h

def compute_e(G, g, h):
	e = (G - g)/(h + 1e-15)
	return e

def expand_nodes(map, size, node):
	x = node[0]
	y = node[1]
	results = []

	x_max = size[0]
	y_max = size[1]

	if (x+1 < x_max) and (map[x+1,y] != 1):   # '!=0' for 'map_1' and 'crazy' &  '!=1' for 'medium, hard & very hard gifs'
		results.append((x+1,y)) 

	if (y+1 < y_max) and (map[x,y+1] != 1): 
		results.append((x,y+1))

	if (y>=1) and (map[x,y-1] != 1): 
		results.append((x,y-1))

	if (x>=1) and (map[x-1,y] != 1): 
		results.append((x-1,y))

	return results

 
def prune(front, G, goal):
	update_front = ReversePriorityQueue(0)

	while not front.empty():
		node = front.get()
		e_s = node[0]
		g_s = node[1]
		state = node[2]

		h_s = heuristic(state, goal)

		if g_s + h_s < G:
			new_e_s = compute_e(G, g_s, h_s)
			update_front.put((new_e_s, g_s, state))
		
	return update_front

def print_stats(time_taken, G, E, sub_opt_count):
	
	print ""
	print "Sub-optimal Count: " + str(sub_opt_count)
	print "Cost G           : " + str(G) + ' units'
	print "Sub-optimality   : " + str(E) + ' units'
	print "Time Taken       : " + str (time_taken) + ' sec'
	
	return time_taken

def ANA_star(map, size, start, goal):
	global G, E

	sub_opt_count = 0
	
	h_start = heuristic(start, goal)
	e = compute_e(G, 0, h_start)

	front = ReversePriorityQueue(0) 
	front.put((e, 0, start))

	parent_linked = {}
	explored = {}

	parent_linked[start] = None
	explored[start] = 0
	
	time_prev = 0
	
	while not front.empty():
		sub_opt_count += 1
		start_time = time.time()
		parent_linked, explored, front, G, E = improve_solution(parent_linked, explored, front, G, E, map, size, start, goal)
		end_time = time.time()
		time_diff = end_time - start_time
		
		time_prev = print_stats(time_diff + time_prev, G, E, sub_opt_count)
		front = prune(front, G, goal)
		
	path = []
	current_node = goal
	while current_node != start:
		path.append(current_node)
		current_node = parent_linked[current_node]
	path.append(start)
	path.reverse()	

	frontier = {}
	for f in front.queue:
		frontier[f[2]] = f[1]

	return path, explored, frontier, sub_opt_count

def improve_solution(parent_linked, explored, front, G, E, map, size, start, goal):
	
	while not front.empty():
		current_node = front.get()
		e_s = current_node[0]
		g_s = current_node[1]
		state = current_node[2]
		
		if e_s < E:
			E = e_s

		if state == goal:
			G = g_s
			break

		for child_node in expand_nodes(map, size, state):
			new_cost = explored[state] + 1
			if child_node not in explored or new_cost < explored[child_node] :
				explored[child_node] = new_cost
				h_child = heuristic(goal, child_node)
				total_cost = new_cost + h_child
				if total_cost < G:
					e_child_node = compute_e(G, new_cost, h_child)
					front.put((e_child_node, new_cost, child_node))
				parent_linked[child_node] = state

	return parent_linked, explored, front, G, E

def search(map, size):

	global path, start, end, path, expanded, frontier
	
	"""
	This function is meant to use the global variables [start, end, path, expanded, frontier] to search through the
	provided map.
	:param map: A '1-concept' PIL PixelAccess object to be searched. (basically a 2d boolean array)
	"""
	print ""
	print "Start Point: " + str(start)
	print "End   Point: " + str(end)

	# O is unoccupied (white); 1 is occupied (black)
	print ""
	print "pixel value at start point ", map[start[0], start[1]]
	print "pixel value at end point ", map[end[0], end[1]]

	path, expanded, frontier, sub_opt_count = ANA_star(map, size, start, end)
	
	visualize_search("out.png") # see what your search has wrought (and maybe save your results)

def visualize_search(save_file="algo_img.png"):
	"""
	:param save_file: (optional) filename to save image to (no filename given means no save file)
	"""
	im = Image.open(difficulty).convert("RGB")
	pixel_access = im.load()

	# draw start and end pixels
	pixel_access[start[0], start[1]] = GREEN
	pixel_access[end[0], end[1]] = GREEN

	# draw expanded pixels
	for pixel in expanded.keys():
		pixel_access[pixel[0], pixel[1]] = LIGHT_GRAY

	# draw path pixels
	for pixel in path:
		pixel_access[pixel[0], pixel[1]] = GREEN

	 # draw frontier pixels
	for pixel in frontier.keys():
		pixel_access[pixel[0], pixel[1]] = RED
	
	# display and (maybe) save results
	im.show()
	if(save_file != "do_not_save.png"):
		im.save(save_file)
	im.close()

if __name__ == "__main__":
	# Throw Errors && Such
	assert sys.version_info[0] == 2                                 # require python 2 (instead of python 3)
	assert len(sys.argv) == 2, "Incorrect Number of arguments"      # require difficulty input

	# Parse input arguments
	function_name = str(sys.argv[0])
	difficulty = str(sys.argv[1])
	print ""
	print ("ANA* Implementation")
	print "running " + function_name + " with " + difficulty + " difficulty."

	# Hard code start and end positions of search for each difficulty level
	if difficulty == "trivial.gif":
		start = (8, 1)
		end = (20, 1)
		im = Image.open(difficulty)
		search(im.load(), im.size)

	elif difficulty == "medium.gif":
		start = (8, 201)
		end = (110, 1)
		im = Image.open(difficulty)
		search(im.load(), im.size)

	elif difficulty == "hard.gif":
		start = (10, 1)
		end = (401, 220)
		im = Image.open(difficulty)
		search(im.load(), im.size)

	elif difficulty == "very_hard.gif":
		start = (1, 324)
		end = (580, 1)
		im = Image.open(difficulty)
		search(im.load(), im.size)

	elif difficulty == "crazy.jpg":
		start = (605, 741)
		end = (749, 13)
		im = Image.open(difficulty)
		im = im.convert('1')
		search(im.load(), im.size)

	elif difficulty == 'map_1.png':	
		start = (5,5)
		end = (1150, 640)
		im = Image.open(difficulty)
		im = im.convert('1')
		search(im.load(), im.size)

	else:
		assert False, "Incorrect difficulty level provided"