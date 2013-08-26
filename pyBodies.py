import math, random, pygame, gradients
from itertools import count
#from quadtree import Node, QuadTree
import kdtree

def addVectors((angle1, length1), (angle2, length2)):
	""" Returns the sum of two vectors """

	x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
	y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
	angle = 0.5 * math.pi - math.atan2(y, x)
	length  = math.hypot(x, y)

	return (angle, length)

class Particle:
    """ A circular object with a velocity, size and mass """
    _ids = count(0)
    _env = None
    def __init__(self, (x, y), size = 15, mass=1):
        self.x = x
        self.y = y
        self.size = size
        self.color = (0, 43, 54)
        self.thickness = 0
        self.speed = 0
        self.gravicenter = (0,0)
        self.angle = 0.5 * math.pi - math.atan2(self.y - self.gravicenter[1], self.gravicenter[0] - self.x)
        self.mass= mass
        self.drag = 1
        self.gravity = 0
        self.elasticity = 1
        self.graviangle = math.pi
        self.id = self._ids.next()
        self.charge = 0
    
    def __getitem__(self,key):
        if key == 0:
            return self.x
        elif key== 1:
            return self.y
        else:
            return None
        
    def __len__(self):
        return 2
        
    def accelerate(self, vector):
        (self.angle, self.speed) = addVectors((self.angle, self.speed), vector)

    def move(self):
        """ Update position based on speed, angle Update speed based on drag """
        self.x += math.sin(self.angle) * (self.speed + random.gauss(0, 1))
        self.y -= math.cos(self.angle) * (self.speed + random.gauss(0, 1))
        self.speed *= self.drag

        if self.gravicenter != (0,0):
            self.graviangle = 0.5 * math.pi - math.atan2(self.y - self.gravicenter[1], self.gravicenter[0] - self.x)

    def mouseMove(self, x, y):
        """ Change angle and speed to move towards a given point """

        dx = x - self.x
        dy = y - self.y
        self.angle = 0.5*math.pi + math.atan2(dy, dx)
        self.speed = math.hypot(dx, dy) * 0.1

    def attract(self, other):
        '''gravitational like attraction opossite to coulomb law, same sign attract opposite repel'''
        dx = (self.x - other.x)
        dy = (self.y - other.y)
        dist = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        force = 0.1 * self.mass * other.mass / dist**2
        self.accelerate((-0.5*math.pi* other.charge * self.charge + theta , force/self.mass))
        other.accelerate((0.5*math.pi* other.charge * self.charge + theta , force/other.mass))
        
    def attract2(self, other):
        '''makes two particles obey Coulomb law'''
        dx = (self.x - other.x)
        dy = (self.y - other.y)
        dist = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        force = 0.005 * abs(self.charge * other.charge) / dist**2
        self.accelerate((0.5*math.pi + theta , force * other.charge * self.charge/self.mass))
        other.accelerate((-0.5*math.pi + theta, force * other.charge * self.charge/other.mass))
        
    def collide(self, p2):
        """ Tests whether two particles overlap If they do, make them bounce i.e. update their angle, speed and position """
        
        dx = self.x - p2.x
        dy = self.y - p2.y
        
        dist = math.hypot(dx, dy)
        if dist < self.size + p2.size:
            angle = math.atan2(dy, dx) + 0.5 * math.pi
            total_mass = self.mass + p2.mass

            (self.angle, self.speed) = addVectors((self.angle, self.speed*(self.mass-p2.mass)/total_mass), (angle, 2*p2.speed*p2.mass/total_mass))
            (p2.angle, p2.speed) = addVectors((p2.angle, p2.speed*(p2.mass-self.mass)/total_mass), (angle+math.pi, 2*self.speed*self.mass/total_mass))
            elasticity = self.elasticity * p2.elasticity
            self.speed *= elasticity
            p2.speed *= elasticity

            overlap = 0.5*(self.size + p2.size - dist + 1)
            self.x += math.sin(angle)*overlap
            self.y -= math.cos(angle)*overlap
            p2.x -= math.sin(angle)*overlap
            p2.y += math.cos(angle)*overlap

            dx = self.x - p2.x
            dy = self.y - p2.y

            dist = math.hypot(dx, dy)

            length = self.size + p2.size + 4

            if dist < 1.1*(self.size + p2.size):
               self._env.addSpring(self, p2, length=length, strength=8)

class Cell(Particle):
    
    def __init__(self, (x, y), size = 15, mass=1):
        Particle.__init__(self,(x, y), size, mass)
        self.divide = False
        self.die = False
        self.growth_rate = 0
        self.age = 0
    
    def grow(self):
        self.size += self.size * self.growth_rate
        self.age += 1			
        if self.size >= 15:
            self.divide = True

class Spring:
    def __init__(self, p1, p2, length=50, strength=0.5):
        self.p1 = p1
        self.p2 = p2
        self.length = length
        self.strength = strength
    
    def update(self):
        
        dx = self.p1.x - self.p2.x
        dy = self.p1.y - self.p2.y
        dist = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        force = (self.length - dist) * self.strength

        self.p1.accelerate((theta + 0.5 * math.pi, force/self.p1.mass))
        self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))
        #self.p1.accelerate((-0.5*math.pi + theta, force/self.p1.mass))
        #self.p2.accelerate((0.5*math.pi + theta, force/self.p2.mass))

        if dist > 1.3 * self.length:
            self.remove=(self.p1.id,self.p2.id)
##            self.p1.accelerate((-theta + 0.5 * math.pi, force/self.p1.mass))
##            self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))
##            #self.p1.accelerate((0.5*math.pi + theta, force/self.p1.mass))
##            #self.p2.accelerate((0.5*math.pi + theta, force/self.p2.mass))
   
class Environment:
    
    def __init__(self, (width, height),**kargs):
        
        self.width = width
        self.height = height
        self.particles = []
        self.springs = {}
        self.color = (238,232,213)
        self.viscosity = kargs.get('viscosity', 0)
        self.elasticity = kargs.get('elasticity', 1)
        self.gravity = kargs.get('gravity', 0)
        self.gravicenter = kargs.get('gravicenter', (0,0))
        #self.maxdist=sqrt(((width/2)^2) + ((height/2)^2))
        self.acceleration = None
        self.growth_rate = kargs.get('growth_rate', 0)
        self.fps = 50
        Particle._env = self

    def addParticle(self, n=1, **kargs):
        
        for i in range(n):
            size = kargs.get('size', random.randint(5,10))
            mass = kargs.get('mass', random.randint(100, 10000))
            x = kargs.get('x', random.uniform(size, self.width - size))
            y = kargs.get('y', random.uniform(size, self.height - size))

            particle = Cell((x, y), size, mass)#changed Particle to Cell

            particle.speed = kargs.get('speed', random.random())
            particle.angle = kargs.get('angle', random.uniform(0, math.pi*2))
            particle.color = kargs.get('color', (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)))
            particle.charge = kargs.get('charge', 0)
            particle.drag = (particle.mass/(particle.mass + self.viscosity)) ** particle.size
            particle.gravicenter = kargs.get('gravicenter', self.gravicenter)
            particle.gravity = kargs.get('gravity', self.gravity)
            particle.elasticity = kargs.get('elasticity', self.elasticity)
            particle.growth_rate=kargs.get('growth_rate', self.growth_rate)
            particle.age = kargs.get('age', 0)
            self.particles.append(particle)

    def addSpring(self, p1, p2, length=50, strength=0.5):
        """ Add a spring between particles p1 and p2 """
        
        spring = Spring(p1, p2, length, strength)
        self.springs[(p1.id,p2.id)] = spring

    def update(self):
        """  Moves particles and tests for collisions with the walls and each other """
        particles_to_remove = []
        new_particles = []
        #self.quadtree = None
        #rootnode = Node(None, [0, 0, self.width, self.height])
        #self.quadtree = QuadTree(rootnode, 15, self.particles)

        for i, particle in enumerate(self.particles):
            
            if particle.growth_rate > 0:
                
                particle.grow()
                if particle.divide == True:
                    particle.divide = False

                    (newx,newy)=(particle.x+(particle.size)*math.sin(particle.graviangle),particle.y+(particle.size)*math.cos(particle.graviangle))
                    new_particle=Cell((newx,newy),particle.size/2,particle.mass)#changed particle to Cell
                    new_particle.gravicenter = self.gravicenter
                    new_particle.angle = 0.5 * math.pi - math.atan2(newy - self.gravicenter[1], self.gravicenter[0] - newx)
                    new_particle.drag = (new_particle.mass/(new_particle.mass + self.viscosity)) ** new_particle.size
                    new_particle.color = particle.color
                    new_particle.gravity = self.gravity
                    new_particle.elasticity = self.elasticity
                    new_particle.growth_rate =  self.growth_rate*0.5
                    new_particles.append(new_particle)
                    new_particle.charge = particle.charge
                    particle.size = particle.size/2
                    particle.growth_rate = self.growth_rate
                    
            particle.move()
            
            
            #dist_to_gr_center = math.hypot(self.x - self.gravity_center[0], self.y - self.gravity_center[1]) 
            #drag = friction * ((dist_to_gr_center+0.1)/max_dist)
            if particle.gravity > 0:
                particle.accelerate((particle.graviangle,particle.gravity))

            self.bounce(particle)

            
                
            for particle2 in self.particles[i+1:]:
                particle.collide(particle2)
                particle.attract(particle2)
                
##        tree = kdtree.create(self.particles,dimensions=2)
##        for particle in self.particles:
##            tree.search_nn_dist_p(particle,15*4)
        
        self.particles.extend(new_particles)
        springs_to_remove=set()
        for spring in self.springs.values():
            spring.update()
            if 'remove' in spring.__dict__:
                springs_to_remove.add(spring.remove)
        
        for spring in springs_to_remove:
            del self.springs[spring]
        
    def bounce(self, particle):
        """ Tests whether a particle has hit the boundary of the environment """

        if particle.x > self.width - particle.size:
            particle.x = 2*(self.width - particle.size) - particle.x
            particle.angle = - particle.angle
            particle.speed *= self.elasticity

        elif particle.x < particle.size:
            particle.x = 2*particle.size - particle.x
            particle.angle = - particle.angle
            particle.speed *= self.elasticity

        if particle.y > self.height - particle.size:
            particle.y = 2*(self.height - particle.size) - particle.y
            particle.angle = math.pi - particle.angle
            particle.speed *= self.elasticity

        elif particle.y < particle.size:
            particle.y = 2*particle.size - particle.y
            particle.angle = math.pi - particle.angle
            particle.speed *= self.elasticity



    def findParticle(self, x, y):
        """ Returns any particle that occupies position x, y """

        for particle in self.particles:
            if math.hypot(particle.x - x, particle.y - y) <= particle.size:
                return particle
        return None

    def run(self, title='pyBodies'):
        pygame.init()
        screen = pygame.display.set_mode((self.width,self.height), pygame.SRCALPHA)
        clock = pygame.time.Clock()
        selected_particle = None
        ecolor = (133,153,0,255)
        scolor = (133,153,0,1)
        spoint= (0,0)
        epoint = (self.width,self.height)

        grad = gradients.draw_gradient(screen, spoint, epoint, scolor, ecolor, lambda x:x, lambda x:x, lambda x:x, lambda x: x)

        running = True
        paused = False
        tick=0
        while running:
            tick+=1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (mouseX, mouseY) = pygame.mouse.get_pos()
                    selected_particle = self.findParticle(mouseX, mouseY)
                elif event.type == pygame.MOUSEBUTTONUP:
                    selected_particle = None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = (True, False)[paused]

            if selected_particle:
                (mouseX, mouseY) = pygame.mouse.get_pos()
                selected_particle.mouseMove(mouseX, mouseY)
            
            if not paused:
                self.update()
            
            screen.fill(self.color)

            screen.blit(grad[0],grad[1])
            #pygame.draw.line(screen, (7,54,66), spoint, epoint)
            
            for s in self.springs.values():
                pygame.draw.aaline(screen, (0, 43, 54), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)))
            
            
            for p in self.particles:
                pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), int(p.size), p.thickness)

          
            #for node in self.quadtree.allnodes:
            #    rect = (node.rect[0],node.rect[1],node.rect[2] - node.rect[0], node.rect[3] - node.rect[1])
            #   pygame.draw.rect(screen,(0, 0, 0),rect,1)

            pygame.display.flip()
            clock.tick(50)
            pygame.display.set_caption("ticks: " + str(tick) + " fps: " + str(clock.get_fps()))
            #paused=True
        pygame.quit()
         
