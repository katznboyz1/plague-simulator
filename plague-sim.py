#TODO: make it so that the game only blits sprites that are visible

'''
KEYS:
    W - Move map up
    S - Move map down
    A - Move map left
    D - Move map right
'''

#imports
import pygame, json, random, PIL.Image, time, os

#the main class for the simulator
class simulator:
    #a function that gets the data from ./manifest.json and returns it in a dict
    def getManifestData() -> dict:
        return json.loads(str(open('./manifest.json').read()))
    #a function that makes text that you can blit to the screen using pygame
    def text(fontFace, size, text, color) -> pygame.font.Font:
        font = pygame.font.Font(fontFace, size)
        text = font.render(text, 1, color)
        return text
    #a function to generate the people on the map, where chance = [minRandomChoice, maxRandomChoice, match]
    def generateRandomPeople(chance = [0, 100, 5], worldSize = [600, 600]):
        people = []
        #generate the actual people
        for each_x in range(worldSize[0]):
            for each_y in range(worldSize[1]):
                if (random.randint(chance[0], chance[1]) == chance[2]):
                    people.append({
                            'x':[each_x, worldSize[0]], #the x coordinate out of the total size of the world, so it can be calculated to a percentage
                            'y':[each_y, worldSize[1]], #the y coordinate out of the total size of the world, so it can be calculated to a percentage
                            'status':'healthy', #the health status of the person
                            'pathfinder':{
                                'destination':[int(worldSize[0] / 2), int(worldSize[1] / 2)]
                            }
                        })
        return people
    #a function to generate the rats on the map, chance = [minRandomChoice, maxRandomChoice, match]
    def generateRandomRats(chance = [0, 100, 5], worldSize = [600, 600]):
        rats = []
        #generate the actual people
        for each_x in range(worldSize[0]):
            for each_y in range(worldSize[1]):
                if (random.randint(chance[0], chance[1]) == chance[2]):
                    rats.append({
                            'x':[each_x, worldSize[0]], #the x coordinate out of the total size of the world, so it can be calculated to a percentage
                            'y':[each_y, worldSize[1]], #the y coordinate out of the total size of the world, so it can be calculated to a percentage
                            'pathfinder':{
                                'destination':[int(worldSize[0] / 2), int(worldSize[1] / 2)]
                            },
                            'alive':1, #whether or not the rat is alive (determines whether or not to blit to screen)
                        })
        return rats
    #the clock that helps set the game's fps
    clock = pygame.time.Clock()
    #the wanted frames per second
    wantedFPS = 40
    #the last FPS count
    lastFPS = 0
    #the data that shows that statuses of the people on the map
    humanData = []
    #the data that shows that statuses of the rats on the map
    ratData = []
    #the actual screen that everything is blitted to
    screen = None
    #a boolean that makes sure that the game is still running
    running = True
    #the amount of times the main while loop has ran
    runs = 0
    #the data for the world
    worldData = {
        'position':[0, 0], #the offset of the map
        'scale':1, #the scale of the map
    }
    #the last fps count
    lastFPS = 0
    #the sprite dimensions
    spriteSize = [20, 20]

#initialize the map for the characters
worldMap = PIL.Image.open(simulator.getManifestData()['data']['main-map-image-path'])
worldMap = worldMap.convert('RGB')

#initialize the beings on the map
print ('Generating the humans...')
simulator.humanData = simulator.generateRandomPeople(chance = [0, int(worldMap.size[0] * 15), int(worldMap.size[0] / 2)], worldSize = worldMap.size)
print ('Generating the rats...')
simulator.ratData = simulator.generateRandomRats(chance = [0, int(worldMap.size[0] * 10), int(worldMap.size[0] / 2)], worldSize = worldMap.size)

#initialize the screen display
pygame.display.init()
pygame.font.init()
pygame.mouse.set_visible(True)

#make the screen half of the parent display's size
screenDimensions = [int(pygame.display.Info().current_w // 2), int(pygame.display.Info().current_h // 2)]
simulator.screen = pygame.display.set_mode(screenDimensions, pygame.RESIZABLE)

#set the window title
pygame.display.set_caption('Harrison\'s Plague Simulator')

#the main event loop
while (simulator.running):
    #get the measure for the fps count
    start = time.time()
    #fill the screen white
    simulator.screen.fill((255, 255, 255))
    #load the manifest file
    manifestData = simulator.getManifestData()
    #go through all the events
    events = pygame.event.get()
    for event in events:
        #check if the X button has been pushed
        if (event.type == pygame.QUIT):
            simulator.running = False
        #check if the screen has been resized
        elif (event.type == pygame.VIDEORESIZE):
            simulator.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        #check if a key has been pressed
        elif (event.type == pygame.KEYDOWN):
            #moveAmount = the amount that the screen will move in pixels
            moveAmount = 20
            if (event.key == pygame.K_w):
                simulator.worldData['position'][1] += moveAmount
            if (event.key == pygame.K_s):
                simulator.worldData['position'][1] -= moveAmount
            if (event.key == pygame.K_a):
                simulator.worldData['position'][0] += moveAmount
            if (event.key == pygame.K_d):
                simulator.worldData['position'][0] -= moveAmount
    #blit the map to the screen
    mapSprite = pygame.image.load(manifestData['data']['main-map-image-path'])
    simulator.screen.blit(mapSprite, simulator.worldData['position'])
    #calculate how far the sprites should move
    try:
        delta = int(simulator.wantedFPS / simulator.lastFPS) / 10
        actualDelta = int(simulator.wantedFPS / simulator.lastFPS)
    except:
        delta = 0.1
        actualDelta = 1
    #blit the humans to the screen
    deadCount = 0
    for each_int in range(len(simulator.humanData)):
        #blit the humans
        each = simulator.humanData[each_int]
        humanSprite = pygame.image.load(manifestData['data']['human-sprites'][each['status']])
        humanSpritePos = [0, 0]
        humanSpritePos[0] = int(worldMap.size[0] * (each['x'][0] / each['x'][1])) + simulator.worldData['position'][0]
        humanSpritePos[1] = int(worldMap.size[1] * (each['y'][0] / each['y'][1])) + simulator.worldData['position'][1]
        humanSprite = pygame.transform.scale(humanSprite, simulator.spriteSize)
        simulator.screen.blit(humanSprite, humanSpritePos)
        humanPositionOnMap = [int(worldMap.size[0] * (each['x'][0] / each['x'][1])), int(worldMap.size[1] * (each['y'][0] / each['y'][1]))]
        humanDestinationOnMap = each['pathfinder']['destination']
        mapScale = [float(simulator.humanData[each_int]['x'][1] / worldMap.size[0]), float(simulator.humanData[each_int]['y'][1] / worldMap.size[1])]
        #if the player is in good health then they can walk around
        if (each['status'] in ['healthy', 'immune']):
            #check if the humans have arrived at their desitinations
            isAtDestination = [False, False]
            if (int(abs(abs(humanPositionOnMap[0]) - abs(each['pathfinder']['destination'][0]))) <= int(simulator.spriteSize[0] * 3)):
                simulator.humanData[each_int]['pathfinder']['destination'][0] = humanPositionOnMap[0]
                isAtDestination[0] = True
            if (int(abs(abs(humanPositionOnMap[1]) - abs(each['pathfinder']['destination'][1]))) <= int(simulator.spriteSize[1] * 3)):
                simulator.humanData[each_int]['pathfinder']['destination'][1] = humanPositionOnMap[1]
                isAtDestination[1] = True
            if (isAtDestination == [True, True]):
                simulator.humanData[each_int]['pathfinder']['destination'] = [int(random.randint(0, worldMap.size[0])), int(random.randint(0, worldMap.size[1]))]
            #make the humans move towards their desinations
            if (humanPositionOnMap[0] < humanDestinationOnMap[0]):
                simulator.humanData[each_int]['x'][0] += (int(simulator.spriteSize[0] * delta) * mapScale[0])
            elif (humanPositionOnMap[0] > humanDestinationOnMap[0]):
                simulator.humanData[each_int]['x'][0] -= (int(simulator.spriteSize[0] * delta) * mapScale[0])
            if (humanPositionOnMap[1] < humanDestinationOnMap[1]):
                simulator.humanData[each_int]['y'][0] += (int(simulator.spriteSize[1] * delta) * mapScale[1])
            elif (humanPositionOnMap[1] > humanDestinationOnMap[1]):
                simulator.humanData[each_int]['y'][0] -= (int(simulator.spriteSize[1] * delta) * mapScale[1])
        elif (each['status'] == 'infected'):
            chanceForStateChange = random.randint(1, 10)
            if (chanceForStateChange == 1):
                simulator.humanData[each_int]['status'] = 'dead'
            if (chanceForStateChange == 2):
                simulator.humanData[each_int]['status'] = 'immune'
        elif (each['status'] == 'dead'):
            deadCount += 1
        #check if the player is close to a rat
        for rats in simulator.ratData:
            if (bool(rats['alive'])):
                distance = [0, 0]
                ratPositionOnMap = [int(worldMap.size[0] * (rats['x'][0] / rats['x'][1])), int(worldMap.size[1] * (rats['y'][0] / rats['y'][1]))]
                distance[0] = int(abs(abs(ratPositionOnMap[0]) - abs(humanPositionOnMap[0])))
                distance[1] = int(abs(abs(ratPositionOnMap[1]) - abs(humanPositionOnMap[1])))
                if (distance[0] <= int(simulator.spriteSize[0] * 1.5) and distance[1] <= int(simulator.spriteSize[1] * 1.5)):
                    if (random.randint(0, 10) == 5):
                        statusForHuman = random.choice(['healthy', 'infected', 'infected', 'infected'])
                        if (each['status'] == 'healthy'):
                            simulator.humanData[each_int]['status'] = statusForHuman
    #blit the rats to the screen
    for each_int in range(len(simulator.ratData)):
        each = simulator.ratData[each_int]
        if (bool(each['alive'])):
            ratSprite = pygame.image.load(manifestData['data']['rat-sprite-path'])
            ratPos = [0, 0]
            ratPos[0] = int(worldMap.size[0] * (each['x'][0] / each['x'][1])) + simulator.worldData['position'][0]
            ratPos[1] = int(worldMap.size[1] * (each['y'][0] / each['y'][1])) + simulator.worldData['position'][1]
            ratSprite = pygame.transform.scale(ratSprite, simulator.spriteSize)
            simulator.screen.blit(ratSprite, ratPos)
            willRatDie = random.randint(0, int(actualDelta * 200)) == 1
            if (willRatDie):
                simulator.ratData[each_int]['alive'] = 0
    #blit the fps count to the screen
    textLine1 = simulator.text(manifestData['data']['default-font-path'], int(simulator.screen.get_size()[1] / 15), 'FPS: ' + str(int(simulator.lastFPS)), (0, 0, 0))
    simulator.screen.blit(textLine1, (0, 0))
    textLine2 = simulator.text(manifestData['data']['default-font-path'], int(simulator.screen.get_size()[1] / 15), ('{}/{} Dead'.format(deadCount, len(simulator.humanData))), (0, 0, 0))
    simulator.screen.blit(textLine2, (0, textLine1.get_size()[1]))
    #update the screen
    pygame.display.update()
    #tick the clock
    simulator.clock.tick(simulator.wantedFPS)
    #update the run count
    simulator.runs += 1
    #update the fps count
    end = time.time()
    simulator.lastFPS = float(1 / (end - start))

#quit pygame
pygame.quit()