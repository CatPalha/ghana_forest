import math
import random


class LifeCycle:

    def __init__(self):
        self.age = 0

    def current(self):
        return None

    def step(self):
        self.age += 1


class BasicLifeCycle(LifeCycle):
    def __init__(self, *durations):
        LifeCycle.__init__(self)
        self.repeating = True
        self.durations = durations
        self.change_stage = list()
        self.count_cycles = 0
        self.stage_changed = True

        # Allows to know, starting on zero when changes its stage
        # By accumulating the duration in each stage, this values are appended to the list

        sum = 0
        # self.change_stage.append(0)
        for i, d in enumerate(self.durations):
            sum += d
            self.change_stage.append(sum)

        self.cycle_duration = self.change_stage[-1]
        self.current_stage = 0

    def count_stages(self):
        return len(self.durations)

    def total_duration(self):
        return self.cycle_duration

    def cycle_age(self):
        return self.age % self.cycle_duration

    def step(self):
        LifeCycle.step(self)
        self.stage_changed = False
        cycle_age = self.cycle_age()
        if cycle_age == 0 and self.repeating:
            self.current_stage = 0
            self.count_cycles += 1
            self.stage_changed = True
        elif cycle_age == self.change_stage[ self.current_stage ]:
            self.current_stage += 1
            self.stage_changed = True
        else:
            pass

    def __repr__(self):
        return f"age: {self.age:3} cycle age: {self.cycle_age()} # cycles: {self.count_cycles} cur stage: {self.current_stage} ds: {self.durations} ts: {self.change_stage}"

class Agent:
    def __init__(self, env, lifecycle=None, energy=100.0):
        self.age = 0
        self.energy = energy
        self.lifecycle = lifecycle
        self.per = list()

        self.env = env
        self.id = env.add_agent(self)

    def set_per(self, sense, value):
        self.per[sense] = value

    def get_per(self, sense):
        return self.per[sense]

    def physics(self):
        pass

    def metabolism(self):
        self.age += 1
        self.lifecycle.step()

    def set_lifecycle(self, lf):
        self.lifecycle = lf
    #Para que é que é isto?
    def do(self, action, parameters):
        action(*parameters)
    #e isto?
    def sense(self, sensor, parameters):
        pass

    def behave(self):
        pass

    def update_perception(self):
        self.per = list()

    def step(self):
        if self.energy > 0 and self.env is not None and self.lifecycle is not None:
            self.metabolism()
            self.update_perception()
            self.behave()
            self.physics()

    def __repr__(self):
        return f"[id: {self.id} age: {self.age} stage: {self.lifecycle.current_stage} ]"


EAST = (1, 0)
WEST = (-1, 0)
NORTH = (0, -1)
SOUTH = (0, 1)
DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

class MobileAgent(Agent):
    def __init__(self, env, lifecycle=None, xy=None, radius=8, weight=0.0, energy=0.0, max_vel=None):
        if xy is None:
            x, y = env.get_random_position(radius)
        else:
            x, y = xy
        self.x = x
        self.y = y

        self.heading = 0

        self._vel = 0
        self.acc = 0

        self.radius = radius

        self.weight = weight

        if max_vel is None:
            self.max_vel = self.radius
        else:
            self.max_vel = max_vel

        self.energy = energy

        Agent.__init__(self, env, lifecycle, energy)

    #Não entendo.
    def physics(self):
        self._vel += self.acc
        self._vel = clip(self._vel, 0, self.max_vel)
        self.acc = 0
        d = (math.cos(self.heading) * self._vel,
             -math.sin(self.heading) * self._vel)

        dest = (self.x + d[0], self.y + d[1])

        within_bounds = self.radius <= dest[0] <= self.env.width - self.radius and \
            self.radius <= dest[1] <= self.env.height - self.radius
        if within_bounds and len(self.env.scan_at(dest[0], dest[1], self.radius) - {self.id}) == 0:
            self.x += d[0]
            self.y += d[1]

    def behave(self):
        pass

    def head_to(self, x, y):
        self.heading = math.atan2(y, x)



class RandomWalker(MobileAgent):
    def behave(self):
        Agent.behave(self)
        d = 0.125 * random.gauss(0, math.pi)
        self.heading += d
        self.acc = (self.lifecycle.current_stage + 1)


class Environment:
    """The environment can identidy agents, filter based on some condition,
        add agents to itself, look within agents radius, and get random position on the environment
        in each iteration age is increased by 1. (step function)"""

    def __init__(self, width = 1000, height = 600):
        self.age = 0
        self.width = width
        self.height = height
        self.agents = dict()
        self._next_id = -1
        self._kill_list = list()

    def map(self, ag_ids, func):
        ags = [self.agents[i] for i in ag_ids if i in self.agents.keys()]

        return [func(ag) for ag in ags]

    def filter(self, ag_ids, pred):
        ags = [self.agents[i] for i in ag_ids if i in self.agents.keys()]
        return [ag.id for ag in ags if pred(ag)]

    def add_agent(self, agent):
        self._next_id += 1
        agent_id = self._next_id
        self.agents[agent_id] = agent
        return agent_id

    def kill_agent(self, ag):
        if ag in self.agents.keys():
            self._kill_list.append(ag)

    def step(self):
        self._kill_list = list()
        
        self.age += 1
        for ag in self.agents.values():
            ag.step()
        
        for ag_id in self._kill_list:
            del self.agents[ag_id]
        
    def scan_at(self, x, y, r):
        return set(ag.id for ag in self.agents.values() if
                   hasattr(ag, 'x') and
                   math.hypot(ag.x - x, ag.y - y) < ag.radius + r)

    def get_random_position(self, radius, retries=100):

        x = random.randrange(radius, self.width - radius)
        y = random.randrange(radius, self.height - radius)

        while retries > 0 and len(self.scan_at(x, y, radius)) > 0:
            x = random.randrange(radius, self.width - radius)
            y = random.randrange(radius, self.height - radius)
            retries -= 1

        return (x, y)

    def __repr__(self):
        split = "\n\t"
        return f"[{self.age}]{split.join(str(ag) for ag in self.agents.values())}"


def clip(x, a, b):
    '''bounds the value of x to [a, b]'''
    if x < a:
        return a
    elif b < x:
        return b
    return x
