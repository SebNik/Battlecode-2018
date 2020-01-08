import battlecode as bc
import random
import sys
import traceback
import time
import os
print("Starting Bot")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print(directions)

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()

count_workers=0
count_knights=0
count_factories=0
count_rockets=0

while True:

    #data overview
    count_all_robots=count_knights+count_workers
    nedeed_rockets=int((count_all_robots/8)/2)-count_rockets
    nedeed_knights=int(count_workers*0.5-count_knights)
    nedeed_factories=int(count_workers/3)-count_factories
    if gc.round()>500:
        nedeed_workers=gc.karbonite()-(nedeed_factories*200)-(nedeed_knights*40)-(nedeed_rockets*150)
    else:
        nedeed_workers=(gc.karbonite()-(nedeed_factories*200)-(nedeed_knights*40))/60

    print('We need: ', nedeed_knights, 'knights in round: ', gc.karbonite(), count_knights)
    print('We need: ', nedeed_workers, 'workers in round: ', gc.round(), count_workers)
    print('We need: ', nedeed_factories, 'factories in round: ', gc.round(), count_factories)

    count_workers=0
    count_knights=0
    count_factories=0
    count_rockets=0

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():

            # pick a random direction:
            d = random.choice(directions)

            if unit.unit_type== bc.UnitType.Worker:
                count_workers+=1
            if unit.unit_type== bc.UnitType.Knight:
                count_knights+=1
            if unit.unit_type== bc.UnitType.Factory:
                count_factories+=1
            if unit.unit_type== bc.UnitType.Rocket:
                count_rockets+=1

            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                print('kasdjflkasdjkfjl', gc.can_produce_robot(unit.id, bc.UnitType.Knight))
                gc.produce_robot(unit.id, bc.UnitType.Knight)
                if (gc.can_produce_robot(unit.id, bc.UnitType.Knight) and nedeed_knights>0):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('produced a knight!')
                    continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Worker) and nedeed_workers>0:
                    gc.produce_robot(unit.id, bc.UnitType.Worker)
                    print('produced a workers!')
                    continue


            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if unit.unit_type == bc.UnitType.Rocket:
                        garrison=unit.structure_garrison()
                        print(len(garrison))
                        if len(garrison)>-1 and len(garrison)<8:
                            if gc.can_load(unit.id, other.id):
                                gc.load(unit.id, other.id)
                                continue
                        if len(garrison)>7:
                            mapp = gc.starting_map(bc.Planet(1))
                            for y in range(0,mapp.height):
                                for x in range(0,mapp.width):
                                    if (mapp.is_passable_terrain_at(x,y)):
                                        if(gc.can_launch_rocket(unit.id,bc.MapLocation(bc.Planet(1),x,y))):
                                            gc.launch_rocket(unit.id,bc.MapLocation(bc.Planet(1),x,y))
                    if unit.unit_type == bc.UnitType.Worker:
                        for a in directions:
                            if gc.can_harvest(unit.id , a):
                                gc.harvest(unit.id, a)
                                #print(gc.karbonite(),'added karbonite')
                        if other.unit_type == bc.UnitType.Factory and gc.can_build(unit.id, other.id) and nedeed_factories>0:
                            gc.build(unit.id, other.id)
                            continue
                        if other.unit_type == bc.UnitType.Rocket and gc.can_build(unit.id, other.id) and nedeed_rockets>0:
                            gc.build(unit.id, other.id)
                            continue
                        if gc.can_replicate(unit.id, d) and nedeed_workers>0 and gc.round()<20:
                            gc.replicate(unit.id, d)
                            continue
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        # print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue

            # okay, there weren't any dudes around

            # or, try to build a factory:
            if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d) and nedeed_factories>0 and gc.round()<749:
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
            # or, try to build a rocket
            if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d) and gc.round()>350 and nedeed_rockets>0:
                gc.blueprint(unit.id, bc.UnitType.Rocket, d) 
            # and if that fails, try to move
            elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
            #print(d)
            #print(gc.karbonite())

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
