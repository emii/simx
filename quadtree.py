	
# quadtree.py
# Implements a Node and QuadTree class that can be used as 
# base classes for more sophisticated implementations.
# Malcolm Kesson Dec 19 2012
# http://www.fundza.com/algorithmic/quadtree/index.html
# http://www.pygame.org/wiki/QuadTree <-not good
class Node():
    ROOT = 0
    BRANCH = 1
    LEAF = 2
    minsize = 1  
    def __init__(self, parent, rect):
        self.parent = parent
        self.children = [None,None,None,None]
        if parent == None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
        self.rect = rect
        x0,z0,x1,z1 = rect
        if self.parent == None:
            self.type = Node.ROOT
            self.particle = None
        elif ((x1 - x0) <= Node.minsize or (z1 - z0) <= Node.minsize) :
            self.type = Node.LEAF
        else:
            self.type = Node.BRANCH
            self.particle = None

    def subdivide(self, particles):
        if self.type == Node.LEAF:
            return
        x0,z0,x1,z1 = self.rect
        h = (x1 - x0)/2
        l = (z1 - z0)/2 
        rects = []
        rects.append( (x0, z0, x0 + h, z0 + l) )
        rects.append( (x0, z0 + l, x0 + h, z1) )
        rects.append( (x0 + h, z0 + l, x1, z1) )
        rects.append( (x0 + h, z0, x1, z0 + l) )
        for i, r in enumerate(rects):
            span = self.spans_feature(r, particles)
            if span == True:
                child = Node(self,r)
                child.subdivide(particles)# << recursion
                self.children[i] = child

    def contains(self, x, z):
        x0,z0,x1,z1 = self.rect
        if x >= x0 and x < x1 and z >= z0 and z < z1:
            return True
        return False
    
    def spans_feature(self, rect, particles):
        x0,z0,x1,z1 = rect
        for particle in particles:
            x = particle.x
            z = particle.y
            if x >= x0 and x < x1 and z >= z0 and z < z1:
                self.particle = particle
                return True
        return False
  

class QuadTree():

    def __init__(self, rootnode, minrect, particles):
        self.leaves = []
        self.allnodes = []
        Node.minsize = minrect
        rootnode.subdivide(particles) # constructs the network of nodes based on particle positions
        self.maxdepth = 0
        self.prune(rootnode)
        self.traverse(rootnode)

    def prune(self, node):
        if node.type == Node.LEAF:
            return 1
        leafcount = 0
        removals = []
        for child in node.children:
            if child != None:
                leafcount += self.prune(child)
                if leafcount == 0:
                    removals.append(child)
        for item in removals:
            n = node.children.index(item)
            node.children[n] = None        
        return leafcount

    def traverse(self, node):
        self.allnodes.append(node)
        if node.type == Node.LEAF:
            self.leaves.append(node)
            if node.depth > self.maxdepth:
                self.maxdepth = node.depth
        for child in node.children:
            if child != None:
                self.traverse(child) # << recursion
                