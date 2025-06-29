#! /usr/bin/env python3
import random

import core
import bioagents
import visual

def run():
    env = core.Environment()

    env.year = bioagents.Year(env)
    env.day = bioagents.Day(env)
    
    for _ in range(20):
        bioagents.Midge(env)   
    
    for _ in range(20):
        bioagents.Mite(env)
    
    for _ in range(30):
        bioagents.Tree(env)
            

    vis = visual.Visual(env, env.width, env.height, fps = 10)
    vis.paused = True
    vis.go()


if __name__ == "__main__":
    random.seed()
    run()
