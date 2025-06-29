# COLORS FROM https://en.wikipedia.org/wiki/Web_colors#CSS_colors
import math
import pygame
import bioagents

def cv(x, a = 0, b = 1, c = 0, d = 255):
    return c + (d - c) * float(x - a) / (b - a)

R2D = 180.0 / math.pi

def deg(rad):
    return rad * R2D

COLOR = {
    'white':        (255, 255, 255),
    'black':        (  0,   0,   0),
    'spring_green': (  0, 255, 127),    # SPRING -> SPRING GREEN
    'forest_green': ( 34, 139,  34),    # SUMMER -> FORENST GREEN
    'goldenrod':    (218, 165,  32),    # FALL -> GOLDENROD
    'light_blue':   (173, 216, 230),    # WINTER -> LIGHT BLUE

    'orange':       (255, 165,   0),      # DAWN -> ORANGE
    'cornsilk':     (255, 248, 220),    # DAY -> CORNSILK
    'indigo':       ( 75,   0, 130),   # TWILIGHT -> INDIGO
    'twilight':     (199, 157, 215),
    'midnight_blue':( 25,  25, 112),  # NIGHT -> MIDNIGHT_BLUE
}

MIDGE_COLORS = [
    (231, 162, 122),
    (226, 129, 111),
    (97, 70, 95),
    (97, 153, 179),
    (96, 119, 150)
]

class Visual:
    def __init__(self, env, width = 640, height = 480, fps = 10):
        pygame.init()
        self.size = (self.width, self.height) = (width, height)

        self.surface = pygame.display.set_mode(self.size)
        self.surface.set_alpha(0)

        self.ground = list()
        self.biome = list()
        self.atmosphere = list()
        self.controls = list()

        self.fps = fps
        self.clock = pygame.time.Clock()
        self.env = env
        self.paused = True

    def update(self, events):
        if any(e.type == pygame.QUIT for e in events):
            return False
        if any(e.type == pygame.KEYUP and e.key == pygame.K_SPACE for e in events):
            self.paused = not self.paused
        if not self.paused:
            self.env.step()
        return True

    def draw_default(self, ag):

        color = (50 * (1 + ag.lifecycle.current_stage), 50 * (1 + ag.lifecycle.current_stage), 64)
        s = int(2 * ag.radius)
        image = pygame.Surface( (s, s),  pygame.SRCALPHA)
        image.fill((255, 255, 255,0))
        pygame.draw.polygon(image, color, [(0, 0.5 * s), (0.5*s, s), (s, 0.5 * s),  (0.5*s, 0)])
        d = deg(ag.heading)
        image = pygame.transform.rotate(image, d)
        self.biome.append( (image, (ag.x - ag.radius, ag.y - ag.radius) ) )

    def draw_mite(self, ag):

        color = (128, 64, 64)
        s = int(2 * ag.radius)
        image = pygame.Surface( (s, s),  pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        pygame.draw.polygon(image, color, [(0, 0.25 * s), (0, 0.75 * s),  (s, 0.5 * s)])
        d = deg(ag.heading)
        image = pygame.transform.rotate(image, d)
        self.biome.append( (image, (ag.x - ag.radius, ag.y - ag.radius) ) )

        s = int(2 * ag.sensor_range)
        image = pygame.Surface( (s, s),  pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        pygame.draw.circle(image, (0, 0, 0, 128), 
            (ag.sensor_range, ag.sensor_range), ag.sensor_range)
        pygame.draw.circle(image, (0, 0, 0, 255), 
            (ag.sensor_range, ag.sensor_range), ag.sensor_range, 2)
        self.ground.append( (image, (ag.x - ag.sensor_range, ag.y - ag.sensor_range)) )


    def draw_midge(self, ag):
        stage = ag.lifecycle.current_stage
        d = deg(ag.heading)
        
        color = MIDGE_COLORS[stage]
        s = int(2 * ag.radius)
        image = pygame.Surface( (s, s),  pygame.SRCALPHA)
        image.fill((0,0,0,0))
        pygame.draw.polygon(image, color, [(0, 0), (0, s),  (0.5 * s, s), (s, 0.5 * s), (0.5*s, 0)])
        image = pygame.transform.rotate(image, d)
        self.biome.append( (image, (ag.x - ag.radius, ag.y - ag.radius) ) )

        s = int(2 * ag.sensor_range)
        image = pygame.Surface( (s, s),  pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        pygame.draw.circle(image, (0, 0, 0, 128), 
            (ag.sensor_range, ag.sensor_range), ag.sensor_range)
        pygame.draw.circle(image, (0, 0, 0, 255), 
            (ag.sensor_range, ag.sensor_range), ag.sensor_range, 2)
        self.ground.append( (image, (ag.x - ag.sensor_range, ag.y - ag.sensor_range)) )



    def draw_tree(self, ag):
        stage = ag.lifecycle.current_stage
        color = (64, cv(stage, 0.0, 1, 255, 128), 64)
        s = int(2 * ag.radius)
        image = pygame.Surface( (s, s),  pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        pygame.draw.circle(image, color, (0.5 * s, 0.5 * s), 0.5 * s)
        self.biome.append((image, (ag.x - ag.radius, ag.y - ag.radius)))

    def draw_cycle(self, surface, cycle, colors, y = 0, height = 16):
        last_pos = 0
        for i,t in enumerate(cycle.change_stage):
            pos = int(self.width * t / cycle.total_duration())
            color = COLOR[colors[i]]
            rect = (last_pos, y, pos, height)
            pygame.draw.rect(surface, color, rect)
            last_pos = pos
        p = int(self.width * cycle.cycle_age() / cycle.total_duration())
        pygame.draw.rect(surface, COLOR['black'], (0, y, p, height))


    def draw_ground(self):
        self.surface.blits(self.ground)

    def draw_atmosphere(self):
        self.surface.blits(self.atmosphere)

    def draw_controls(self):
        DAY_COLORS = [
            'orange',
            'cornsilk',
            'twilight',
            'midnight_blue'
        ]
        YEAR_COLORS = [
            'spring_green',
            'forest_green',
            'goldenrod',
            'light_blue' ]
            
        self.draw_cycle(self.surface, self.env.year.lifecycle, YEAR_COLORS, y = 0)
        self.draw_cycle(self.surface, self.env.day.lifecycle, DAY_COLORS, y = 16)

    def draw(self):
 
        self.ground = list()
        self.biome = list()
        self.atmosphere = list()
        self.controls = list()
        self.surface.fill((255, 255, 255, 255))
        for ag in self.env.agents.values():

            if isinstance(ag, bioagents.Midge):
                self.draw_midge(ag)

            elif isinstance(ag, bioagents.Mite):
                self.draw_mite(ag)

            elif isinstance(ag, bioagents.Tree):
                self.draw_tree(ag)

            elif isinstance(ag, bioagents.Year) or isinstance(ag, bioagents.Day):
                pass

            else:
                self.draw_default(ag)

        self.surface.blits(self.ground)
        self.surface.blits(self.biome)
        self.surface.blits(self.atmosphere)
        self.draw_controls()
        
        pygame.display.flip()
        pygame.display.set_caption('Ecosystem')

    def go(self):
        loop = True
        while loop:
            events = [e for e in pygame.event.get()]
            loop = self.update(events)
            self.draw()

            self.clock.tick(self.fps)


