import random
import math

from numpy.core.fromnumeric import choose

from core import Agent, MobileAgent, BasicLifeCycle
from ga import GA

WEIGHT, SENSOR, SEX = CHROMOSSOME = range(3)

LOW, MEDIUM, HIGH = GENE_RANGE  = SENSATION  = range(3)

MALE, FEMALE = GENDER  = range(2)

ENERGY_THRESHOLD = 409

TREES_COUNT, TREES_MX, TREES_MY, \
MITES_COUNT, MITES_MX, MITES_MY, \
MIDGES_COUNT, MIDGES_MX, MIDGES_MY, \
ENERGY_SENSATION, TREE_SENTATION, SEXUAL_SENSATION = PERCEPTIONS = range(12)

THRESHOLD = 370
HALF = 2

# DAY_PARTS = 24
# 1 STEP = 8 HOURS


# DAWN, DAY, TWILIGHT, NIGHT
DAY_LIFECYCLE = (
    4,  # DAWN
    8,  # DAY
    4,  # TWILIGHT
    8   # NIGHT
)

DAY_STEPS = sum(DAY_LIFECYCLE)
class Day(Agent):
    def __init__(self, env, lifecycle = DAY_LIFECYCLE):
        Agent.__init__(self, env, lifecycle = BasicLifeCycle(*lifecycle))

YEAR_LIFECYCLE = (
    240 * DAY_STEPS,  # Rainy Season
    120 * DAY_STEPS # Dry Season
)

class Year(Agent):
    def __init__(self, env, lifecycle=YEAR_LIFECYCLE):
        Agent.__init__(self, env, lifecycle=BasicLifeCycle(*lifecycle))

# EGG, LARVAE, PUPAE, ADULT
MIDGE_LIFECYCLE = (
    3 * DAY_STEPS,  # EGG
    15 * DAY_STEPS, # LARVAE   
    3 * DAY_STEPS,  # PUPAE 
    20 * DAY_STEPS   # ADULT
)


class Bug(MobileAgent):
    def __init__(   self, env, 
                    lifecycle = None,
                    xy = None, 
                    radius = 8, 
                    energy = 0,
                    max_vel = None):
        MobileAgent.__init__(self, env, lifecycle=lifecycle, xy=None, radius=8, energy=energy, max_vel=None)
        self.initial_energy = energy        
        self.alive = True

    # override mobileagent's metabolism
    def metabolism(self):
        MobileAgent.metabolism(self)
        if self.age >= self.lifecycle.cycle_duration or self.energy <= 0:
            self.alive = False

    def step(self):
        MobileAgent.step(self)
        if not self.alive:
            self.env.kill_agent(self.id)

class Midge(Bug):
    def __init__(   self,
                    env, 
                    lifecycle = MIDGE_LIFECYCLE,
                    gene = None, 
                    xy = None, 
                    radius = 8, 
                    max_vel = None):
        Bug.__init__(self, env, lifecycle=BasicLifeCycle(*lifecycle), xy=None, radius=8, max_vel=None)

        self.detected = []

        self.detected_trees = []
        self.detected_mites = []
        self.detected_midges = []

        ## GENES VECTOR
        if gene is None:
            self.gene = list()
            for gene in CHROMOSSOME:

                if gene != SEX:
                    self.gene.append(random.choice(GENE_RANGE))

                else: 
                    self.gene.append(random.choice(GENDER))
        else:
            self.gene = gene

        ## EFFECT OF GENES ON MIDGE'S ATTRIBUTES

        #WEIGHT
        if self.gene[0] == HIGH:
            self.weight=random.randrange(90, 100, 1)

        elif self.gene[0] == MEDIUM:
            self.weight = random.randrange(79, 89, 1)

        else:
            self.weight = random.randrange(70, 78, 1)
    
        ## SENSOR
        if self.gene[1] == HIGH:
            self.sensor_range = 3 * self.radius

        elif self.gene[1] == MEDIUM:
            self.sensor_range = 2 * self.radius

        else:
            self.sensor_range = self.radius

        ##SEX
        if self.gene[2] == 0:
            self.gender = "M"
        else:
            self.gender = "F"


        self.energy = (ENERGY_THRESHOLD * self.weight) / 100

        self.initial_energy = self.energy

        self.tired_of_trees = 0
        
    def update_perception_egg(self):
        ## ENERGY SENSATION
        self.per[ENERGY_SENSATION] = LOW

        ## TREE SENSATION
        self.per[TREE_SENTATION] = HIGH

        ## SEXUAL SENSATION
        self.per[SEXUAL_SENSATION] = LOW


    def update_perception_larvae(self):
        ## ENERGY SENSATION
        if self.energy < self.initial_energy / HALF:
            self.per[ENERGY_SENSATION] = HIGH

        elif self.initial_energy / HALF <= self.energy <= THRESHOLD:
            self.per[ENERGY_SENSATION] = MEDIUM
            
        else:
            self.per[ENERGY_SENSATION] = LOW


        ## TREE SENSATION
        self.per[TREE_SENTATION] = HIGH

        self.per[SEXUAL_SENSATION] = LOW

    def update_perception_pupae(self):
        ## ENERGY SENSATION
        self.per[ENERGY_SENSATION] = LOW

        ## TREE SENSATION
        self.per[TREE_SENTATION] = HIGH

        ## SEXUAL SENSATION
        self.per[SEXUAL_SENSATION] = LOW


    def update_perception_adult(self):
        ## ADULT STAGE
        ## ENERGY SENSATION
        if self.energy < self.initial_energy / HALF:
            self.per[ENERGY_SENSATION] = HIGH

        elif self.initial_energy / HALF <= self.energy <= THRESHOLD:
            self.per[ENERGY_SENSATION] = MEDIUM
            
        else:
            self.per[ENERGY_SENSATION] = LOW

    
        ## TREE SENSATION
        ##Count the time that a midge is near trees
        if self.per[TREES_COUNT] > 0:
            self.tired_of_trees += 1
        else:
            self.tired_of_trees = 0
          

        if self.tired_of_trees < 2:
            self.per[TREE_SENTATION] = HIGH

        elif   2 <= self.tired_of_trees < 4:
            self.per[TREE_SENTATION] = MEDIUM

        else:
            self.per[TREE_SENTATION] = LOW

        ## SEXUAL SENSATION
        p_mate = random.random()
    
        if p_mate >= 0.50:
            self.per[SEXUAL_SENSATION] = HIGH

        elif 0.10 < p_mate < 0.50:
            self.per[SEXUAL_SENSATION] = MEDIUM

        else:
            self.per[SEXUAL_SENSATION] = LOW
        


    def update_perception(self):
        Agent.update_perception(self)

        self.per = len(PERCEPTIONS) * [0]

        self.detected = self.env.scan_at(self.x, self.y, self.sensor_range) - {self.id}

        self.detected_trees = self.env.filter(self.detected, lambda ag: isinstance(ag, Tree))
        self.detected_mites = self.env.filter(self.detected, lambda ag: isinstance(ag, Mite))
        self.detected_midges = self.env.filter(self.detected, lambda ag: isinstance(ag, Midge))

        #TREES_COUNT
        self.per[TREES_COUNT] = len(self.detected_trees)

        ## TREES MX AND MY
        if self.per[TREES_COUNT] != 0:
            self.per[TREES_MX] = sum(self.env.map(self.detected_trees, lambda ag: ag.x)) / self.per[TREES_COUNT]
            self.per[TREES_MY] = sum(self.env.map(self.detected_trees, lambda ag: ag.y)) / self.per[TREES_COUNT]

        else:
            self.per[TREES_MX] = 0
            self.per[TREES_MY] = 0

        ## MITES COUNT
        self.per[MITES_COUNT] = len(self.detected_mites)

        ## MITES MX AND MY
        if self.per[MITES_COUNT] != 0:
            self.per[MITES_MX] = sum(self.env.map(self.detected_mites, lambda ag: ag.x)) / self.per[MITES_COUNT]
            self.per[MITES_MY] = sum(self.env.map(self.detected_mites, lambda ag: ag.y)) / self.per[MITES_COUNT]

        else: 
            self.per[MITES_MX] = 0
            self.per[MITES_MY] = 0

        ##MIDGES COUNT
        self.per[MIDGES_COUNT] = len(self.detected_midges)

        ## MIDGES MX AND MY
        if self.per[MIDGES_COUNT] != 0:
            self.per[MIDGES_MX] = sum(self.env.map(self.detected_midges, lambda ag: ag.x)) / self.per[MIDGES_COUNT]
            self.per[MIDGES_MY] = sum(self.env.map(self.detected_midges, lambda ag: ag.y)) / self.per[MIDGES_COUNT]

        else: 
            self.per[MIDGES_MX] = 0
            self.per[MIDGES_MY] = 0

        if self.lifecycle.current_stage == 0: 
            self.update_perception_egg()
            
        elif self.lifecycle.current_stage == 1:
            self.update_perception_larvae()

        elif self.lifecycle.current_stage == 2:
            self.update_perception_pupae()
            
        elif self.lifecycle.current_stage == 3:
            self.update_perception_adult()

        else:
            pass


    ## ACTIONS
    def feed(self):
        self.energy += 10
        

    def mate(self, gene1, gene2):
        self.energy -= 5
        crossover_point = random.randrange(4)
        off1, off2 = GA.crossover(gene1, gene2)
        GA.mutation(off1)
        GA.mutation(off2)

        return off1, off2
    

    def flee(self, x, y):
        self.head_to(x, y)
        self.heading += math.pi
        #self.energy -= 0.5            

    def approach(self, x, y):
        self.head_to(x, y)

    ## CONNECTION BETWEEN PERCEPTIONS AND ACTIONS: THE BEHAVIOR
    def behave(self):
        MobileAgent.behave(self)

        if self.lifecycle.current_stage == 0:
            self.behave_egg()

        elif self.lifecycle.current_stage == 1:
            self.behave_larvae()

        elif  self.lifecycle.current_stage == 2:
            self.behave_pupae()

        elif  self.lifecycle.current_stage == 3:
            self.behave_adult()
        
        else:
            pass
        

    def behave_egg(self):
        pass


    def behave_larvae(self):
        #limit max_vel
        self.acc = 1.0

        if self.per[TREES_COUNT] > 0:

            if self.per[ENERGY_SENSATION] == HIGH:
                self.approach(self.per[TREES_MX], self.per[TREES_MY])
                self.feed()
            else:
                d = random.gauss(0, math.pi )
                self.heading += 0.125 * d

        else:
            d = random.gauss(0, math.pi )
            self.heading += 0.125 * d

    def behave_pupae(self):
        if self.lifecycle.stage_changed:
            self.acc = -self._vel
        

    def behave_adult(self):
        self.acc = 1.0
        

        ## BEHAVIOR WHEN FINDING A MITE
        if self.per[MITES_COUNT] > 0:

            self.flee(self.per[MITES_MX], self.per[MITES_MY])
            self.acc = 2.0

        ## BEHAVIOR WHEN FINDING A TREE
        elif self.per[TREES_COUNT] > 0:

            if self.per[ENERGY_SENSATION] == HIGH:
                self.approach(self.per[TREES_MX], self.per[TREES_MY])
                self.feed()

            elif self.per[TREE_SENTATION] == HIGH:
                self.approach(self.per[TREES_MX], self.per[TREES_MY])

            else:
                d = random.gauss(0, math.pi )
                self.heading += 0.125 * d

        
        ## BEHAVIOR WHEN FINDING ANOTHER MIDGE
        elif self.per[MIDGES_COUNT] > 0:

            if self.per[SEXUAL_SENSATION] == HIGH:
                self.approach(self.per[MIDGES_MX], self.per[MIDGES_MY])
                #self.mate(self.gene, other_Gene)
            
            else:
                d = random.gauss(0, math.pi )
                self.heading += 0.125 * d
        
        else:
            d = random.gauss(0, math.pi )
            self.heading += 0.125 * d

    def get_agent(self):

        info = [self.id, self.gene]

        for i in self.info_agents:
            if info != i:
                self.info_agents.append(info)
            else:
                pass

MITE_LIFECYCLE = (
    360 * DAY_STEPS,
)

ENERGY_SENSATION,  MITES_COUNT, MITES_MX, MITES_MY, \
MIDGES_COUNT, MIDGES_MX, MIDGES_MY, \
SEXUAL_SENSATION = PERCEPTIONS_MITE = range(8)

class Mite(Bug):
    def __init__(self, env,
                 lifecycle=MITE_LIFECYCLE, 
                 energy=600.0,
                 radius=8):
        Bug.__init__(self, env, lifecycle=BasicLifeCycle(*lifecycle), energy=energy, radius=radius)

        self.sensor_range = 4 * self.radius
        self.initial_energy = energy

    def update_perception(self):
        Agent.update_perception(self)

        self.per = len(PERCEPTIONS_MITE) * [0]

        detected = self.env.scan_at(self.x, self.y, self.sensor_range) - {self.id}

        detected_mites = self.env.filter(detected, lambda ag: isinstance(ag, Mite))
        detected_midges = self.env.filter(detected, lambda ag: isinstance(ag, Midge))


        ## ENERGY SENSATION
        if self.energy < self.initial_energy / HALF:
            self.per[ENERGY_SENSATION] = HIGH

        elif self.initial_energy / HALF <= self.energy <= THRESHOLD:
            self.per[ENERGY_SENSATION] = MEDIUM

        else:
            self.per[ENERGY_SENSATION] = LOW


        ## MITES COUNT
        self.per[MITES_COUNT] = len(detected_mites)

        ## MITES MX AND MY
        if self.per[MITES_COUNT] != 0:
            self.per[MITES_MX] = sum(self.env.map(detected_mites, lambda ag: ag.x)) / self.per[MITES_COUNT]
            self.per[MITES_MY] = sum(self.env.map(detected_mites, lambda ag: ag.y)) / self.per[MITES_COUNT]

        else: 
            self.per[MITES_MX] = 0
            self.per[MITES_MY] = 0

        ##MIDGES COUNT
        self.per[MIDGES_COUNT] = len(detected_midges)

        ## MIDGES MX AND MY
        if self.per[MIDGES_COUNT] != 0:
            self.per[MIDGES_MX] = sum(self.env.map(detected_midges, lambda ag: ag.x)) / self.per[MIDGES_COUNT]
            self.per[MIDGES_MY] = sum(self.env.map(detected_midges, lambda ag: ag.y)) / self.per[MIDGES_COUNT]

        else: 
            self.per[MIDGES_MX] = 0
            self.per[MIDGES_MY] = 0


        ## SEXUAL SENSATION
        p_mate = random.random()
    
        if p_mate >= 0.40:
            self.per[SEXUAL_SENSATION] = HIGH

        elif 0.10 < p_mate < 0.40:
            self.per[SEXUAL_SENSATION] = MEDIUM

        else:
            self.per[SEXUAL_SENSATION] = LOW


    def mate(self):
        self.energy -= 5
        #pass

    def feed(self):
        self.energy += 10


    def behave(self):
        MobileAgent.behave(self)
        self.acc = 1.0

        if self.per[MIDGES_COUNT] > 0:

            if self.per[ENERGY_SENSATION] != LOW:
                self.head_to(self.per[MIDGES_MX], self.per[MIDGES_MY])
                self.feed()
            else:
                d = random.gauss(0, math.pi )
                self.heading += 0.125 * d

        elif self.per[MITES_COUNT] > 0:
            if self.per[SEXUAL_SENSATION] == HIGH:
                self.head_to(self.per[MITES_MX], self.per[MITES_MY])
                self.mate()

            else:
                d = random.gauss(0, math.pi )
                self.heading += 0.125 * d
        else:
            d = random.gauss(0, math.pi )
            self.heading += 0.125 * d


# BLOOMING, NOT_BLOOMING
TREE_LIFECYCLE = YEAR_LIFECYCLE

class Tree(Agent):
    def __init__(self, env, lifecycle=TREE_LIFECYCLE, xy=None, radius=16):
        self.radius = radius
        if xy is None:
            self.x, self.y = env.get_random_position(radius)
        else:
            self.x, self.y = xy

        Agent.__init__(self, env, lifecycle=BasicLifeCycle(*lifecycle))        

    # def step(self):
    #     Agent.step(self)
    #     c = self.lifecycle
        #print(f"id:{self.id:3} age:{self.age:5} cycle age:{c.age:5} stage:{c.current_stage:2} loop age:{c.cycle_age():4}---")