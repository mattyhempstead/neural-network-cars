"""

    Car has center and a rotation where 0 rotation is facing to the right

    Each frame the center is moved and rotation is too
    Then each individual point is found again
    
"""

import pygame
import math
import random
import colours
import neural_net
import lines
import json
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Cars Learn to Drive")

class Main:
    def __init__(self):
        self.statsFont = pygame.font.Font(None, 36)
        self.brainFont = pygame.font.Font(None, 24)

        self.track = json.load(open("track.txt", "r"))

        self.trackLength = 0
        for line in self.track["checkpoints"]:
            self.trackLength += lines.distFromPoints(line[0],line[1])
        print("Track has a length of " + str(round(self.trackLength,2)))

        self.genNum = 0
        self.genLength = 15
        self.genSize = 20
        self.genTimer = 0
        
        self.carList = []
        self.oneDown = False
        self.twoDown = False

        self.bestBrain = None

        self.toggleSpeed = False
        
    def mainLoop(self):
        for event in pygame.event.get():    # User did something
            if event.type == pygame.QUIT:   # If user clicked close
                print("User tried to quit")
                global done
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #print("Clicked")
                True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.toggleSpeed = not self.toggleSpeed
                elif event.key == pygame.K_1:
                    self.oneDown = True
                elif event.key == pygame.K_2:
                    self.twoDown = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    self.oneDown = False
                elif event.key == pygame.K_2:
                    self.twoDown = False
                
        # MAIN UPDATE CODE
        carLeft = False
        
        for car in self.carList:
            if car.hitWall == False:
                carLeft = True
                if self.oneDown:
                    car.rotation -= deltaTime
                if self.twoDown:
                    car.rotation += deltaTime

                car.update()

        self.render()   # Render whole game

        self.genTimer += deltaTime

        if carLeft == False or self.genTimer >= self.genLength:
            self.newGen()

    def render(self):
        screen.fill(colours.GREY(230))

        for checkpoint in self.track["checkpoints"]:
            pygame.draw.line(screen, colours.GREY(210), checkpoint[0], checkpoint[1], 6)
        
        for car in self.carList:
            car.render()

        for line in self.track["mainTrack"]:
            pygame.draw.line(screen, colours.BLACK, line[0], line[1], 6)

        fpsText = self.statsFont.render("FPS: " + str(round(clock.get_fps(),2)), 0,  colours.RED)
        screen.blit(fpsText, [10,10])

        genNumText = self.statsFont.render("Gen No. " + str(self.genNum), 0,  colours.RED)
        screen.blit(genNumText, [10,45])

        genTimerText = self.statsFont.render("Gen Timer: " + str(round(self.genLength-self.genTimer, 2)), 0,  colours.RED)
        screen.blit(genTimerText, [10,80])

        if self.bestBrain != None:
            self.drawBrain()

    def drawBrain(self):
        drawRect = [20,440,300,250]
        pygame.draw.rect(screen, colours.GREY(200), drawRect, 3)

        title = self.brainFont.render("Brain of best car", 0, colours.BLACK)
        titleRect = title.get_rect()
        titleRect.center = ((drawRect[0]+drawRect[2])/2, drawRect[1]+drawRect[3]+10)
        screen.blit(title, titleRect.topleft)

        brainLayout = []

        for layerNum in range(len(self.bestBrain.layers)):
            layer = self.bestBrain.layers[layerNum]
            layerLength = len(layer)
            if layerNum != len(self.bestBrain.layers)-1:
                layerLength -= 1

            neuronX = int(drawRect[0] + (layerNum+0.5)*(drawRect[2]/len(self.bestBrain.layers)))
            brainLayout.append([])
            
            for neuronNum in range(layerLength):
                neuronY = int(drawRect[1] + (neuronNum+0.5)*(drawRect[3]/layerLength))
                brainLayout[-1].append([neuronX, neuronY])



        for layerNum in range(len(brainLayout)-1):
            for neuronNum in range(len(brainLayout[layerNum])):
                for weight in range(len(self.bestBrain.layers[layerNum][neuronNum])):   # draw connecting lines
                    lineColour = colours.BLUE
                    if self.bestBrain.layers[layerNum][neuronNum][weight] < 0:
                        lineColour = colours.RED
                    lineWidth = int(4*(self.bestBrain.layers[layerNum][neuronNum][weight]+2) + 1)
                    pygame.draw.line(screen, lineColour, brainLayout[layerNum][neuronNum], brainLayout[layerNum+1][weight], lineWidth)


        for layerNum in range(len(brainLayout)):
            for neuronNum in range(len(brainLayout[layerNum])):
                neuronColour = colours.DARK_GREEN
                if layerNum > 0:
                    neuronColour = math.floor(256*(self.bestBrain.layers[layerNum-1][-1][neuronNum] + 2)/4)
                    if neuronColour == 256:
                        neuronColour = colours.GREY(255)
                    else:
                        neuronColour = colours.GREY(neuronColour)
                pygame.draw.circle(screen, neuronColour, brainLayout[layerNum][neuronNum], 25)
                pygame.draw.circle(screen, colours.BLACK, brainLayout[layerNum][neuronNum], 25, 2)

                if layerNum > 0:
                    neuronWeight = self.brainFont.render(str(round(self.bestBrain.layers[layerNum-1][-1][neuronNum],2)), 0,  colours.DARK_GREEN)
                    neuronRect = neuronWeight.get_rect()
                    neuronRect.center = brainLayout[layerNum][neuronNum]
                    screen.blit(neuronWeight, neuronRect.topleft)
                    

            

                        
                        
            

    def newGen(self):
        self.genNum += 1
        self.genTimer = 0

        #print("Calculating score of cars")
        for car in self.carList:
            #print("Car reached checkpoint " + str(car.currentCheckpoint ))
            progressDist = lines.pointAlongLine(car.basePoint, self.track["checkpoints"][car.currentCheckpoint])
            #print("Along the cars checkpoint it was " + str(progressDist))
            for line in range(car.currentCheckpoint):
                progressDist += lines.distFromPoints(self.track["checkpoints"][line][0],self.track["checkpoints"][line][1])

            progressDist += car.trackLoops * self.trackLength
            car.score = progressDist
            #print("Car got a score of " + str(car.score))

        # Print stats
        genAverage = 0
        bestScore = 0
        for car in self.carList:
            genAverage += car.score
            if bestScore < car.score:
                bestScore = car.score
                self.bestBrain = car.brain
        
        genAverage /= len(self.carList)
        topHalf = 0
        for car in range(int(len(self.carList) /2)):
            topHalf += self.carList[car].score
        topHalf /= len(self.carList)/2
        print("Gen " + str(self.genNum) + " complete, Average:  " + str(round(genAverage, 2)) + " - Top Half Average: " + str(round(topHalf,2)) + " - Best Score: " + str(round(bestScore,2)))
        # ====
        
        for i in range(int(len(self.carList)/2)):
            worstCar = 0
            for car in range(1, len(self.carList)):
                if self.carList[car].score < self.carList[worstCar].score:
                    worstCar = car
            self.carList.pop(worstCar)
            
        for car in range(len(self.carList)):
            self.carList[car].resetStats()
            self.carList.append(Car(self.carList[car]))

        #global done
        #done = True

class Car:  # MAKE CAR HAVE ACCELERATION/DECELERATION ETC. (MAYBE ACCEL/DECEL FOR EACH WHEEL THEN REMOVE ROTATION ENTIRELY?)
    def __init__(self, parent=None):
        self.basePoint = [main.track["checkpoints"][0][0][0], main.track["checkpoints"][0][0][1]]
        self.rotation = 0
        self.size = 30     # width/height of isoceles triangle car (1:1 height to base)

        self.vertexPoints = []
        self.speed = 300

        if parent == None:
            self.brain = neural_net.Neural_Network([3,4,3,2])
        else:
            self.brain = parent.brain.childBrain()

        self.collisionPoints = []

        self.score = 0
        self.currentCheckpoint = 0
        self.trackLoops = 0

        self.hitWall = False

        self.sightLength = 400
        self.sightLines = []
        
    def render(self):
        #vertexPointsRender = []
        for vertex in self.vertexPoints:
            vertex[0] = int(vertex[0])
            vertex[1] = int(vertex[1])

        if self.hitWall != True and main.toggleSpeed == False:
            for sightLine in self.sightLines:
                pygame.draw.line(screen, (132, 163, 131), [int(sightLine[0][0]), int(sightLine[0][1])], [int(sightLine[1][0]), int(sightLine[1][1])], int(self.size/10))

        pygame.draw.polygon(screen, colours.GREEN, self.vertexPoints)
        pygame.draw.polygon(screen, colours.RED, self.vertexPoints, int(self.size/10))

        for vertex in self.vertexPoints:
            pygame.draw.circle(screen, colours.ORANGE, vertex, int(self.size/6))

        for colPoint in self.collisionPoints:
            pygame.draw.circle(screen, colours.BLUE, [int(colPoint[0]), int(colPoint[1])], int(self.size/7))

    def update(self):
        brainInput = [] 
        for sightLine in self.sightLines:
            sightLength = lines.distFromPoints(sightLine[0], sightLine[1])
            brainInput.append(2*sightLength/self.sightLength - 1)  # Alter value to make it good for brain
        if len(brainInput) == 0:
            brainInput = [0,0,0]
        
        brainOutput = self.brain.giveOutput(brainInput)
        
        self.rotation += brainOutput[0] * deltaTime
        self.moveForward(self.speed * ((brainOutput[1]+1)/2))
        
        self.vertexPoints = self.giveVertexPoints()

        # THIS IS CURRENTLY WHAT'S MAKING IT LAG, AVOID TESTING SIGHT WITH LINES NOT NEEDED
        # MAYBE ONLY TEST FOR LINES THAT LIE WITHING THE SIGHT'S QUADRANT???
        self.sightLines = []
        for eye in range(-1,2): # Find collisions with any sight lines and set the new coord of each sight line
            sightLineX = self.vertexPoints[0][0] + math.cos(self.rotation + -eye*(math.pi/3)) * self.sightLength
            sightLineY = self.vertexPoints[0][1] + math.sin(self.rotation + -eye*(math.pi/3)) * self.sightLength
            self.sightLines.append([self.vertexPoints[0], [sightLineX, sightLineY]])
            for line in main.track["mainTrack"]:
                sightCollision = lines.lineToLineIntersect(self.sightLines[-1], line)
                if sightCollision != False:
                    self.sightLines[-1][1] = sightCollision

        self.collisionPoints = []
        for line in main.track["mainTrack"]:
            for edge1 in range(3):
                edge2 = edge1 + 1
                if edge2 == 3:
                    edge2 = 0
                #print("Testing collision with wall of line " + str([self.vertexPoints[edge1],self.vertexPoints[edge2]]))
                edgeCollision = lines.lineToLineIntersect(line, [self.vertexPoints[edge1],self.vertexPoints[edge2]])
                if edgeCollision != False:
                    self.collisionPoints.append(edgeCollision)
                    self.hitWall = True

        # Progress Track Calculations
        currentCheckpointDist = lines.distPointToLine(self.basePoint, main.track["checkpoints"][self.currentCheckpoint])
        #print(str(currentCheckpointDist) + " away from checkpoint " + str(self.currentCheckpoint))
        
        nextCheckpoint = self.currentCheckpoint + 1
        if nextCheckpoint == len(main.track["checkpoints"]):
            nextCheckpoint = 0
        nextCheckpointDist = lines.distPointToLine(self.basePoint, main.track["checkpoints"][nextCheckpoint])
        #print(str(nextCheckpointDist) + " away from next checkpoint " + str(nextCheckpoint))
        
        prevCheckpoint = self.currentCheckpoint - 1
        if prevCheckpoint == -1:
            prevCheckpoint = len(main.track["checkpoints"]) - 1
        prevCheckpointDist = lines.distPointToLine(self.basePoint, main.track["checkpoints"][prevCheckpoint])
        

        if nextCheckpointDist < currentCheckpointDist:
            self.currentCheckpoint = nextCheckpoint
            if self.currentCheckpoint == 0:
                self.trackLoops += 1
            #print("Moved onto checkpoint " + str(self.currentCheckpoint))

        if prevCheckpointDist < currentCheckpointDist:
            self.currentCheckpoint = prevCheckpoint
            if self.currentCheckpoint == len(main.track["checkpoints"]) - 1:
                self.trackLoops -= 1
            #print("Moved back to checkpoint " + str(self.currentCheckpoint))


    def resetStats(self):
        self.basePoint = [main.track["checkpoints"][0][0][0], main.track["checkpoints"][0][0][1]]
        self.rotation = 0
        self.score = 0
        self.currentCheckpoint = 0
        self.trackLoops = 0
        self.hitWall = False

    def moveForward(self, amount):
        moveX = amount * math.cos(self.rotation) * deltaTime
        moveY = amount * math.sin(self.rotation) * deltaTime
        self.basePoint[0] += moveX
        self.basePoint[1] += moveY

    def giveVertexPoints(self):
        vertexPoints = []
        for i in range(3):
            baseAngle = self.rotation
            baseDist = self.size
            if i > 0:
                baseDist /= 2
                if i == 1:
                    baseAngle -= math.pi/2
                else:
                    baseAngle += math.pi/2
            posX = self.basePoint[0] + baseDist * math.cos(baseAngle)
            posY = self.basePoint[1] + baseDist * math.sin(baseAngle)
            vertexPoints.append([posX, posY])

        return vertexPoints


screenRect = pygame.Rect(0,0,size[0],size[1])
screenCenter = screenRect.center

font36 = pygame.font.Font(None, 36)
font24 = pygame.font.Font(None, 24)

print("Car Learning's Sim Started...\n")

clock = pygame.time.Clock()
FPS = 60
deltaTime = 1 / FPS
done = False
main = Main()

for i in range(main.genSize):
    main.carList.append(Car())

 
# -------- Main Program Loop -----------
while not done:
    mousePos = pygame.mouse.get_pos()

    main.mainLoop()
    
    pygame.display.update()

    if main.toggleSpeed:
        clock.tick()
    else:
        clock.tick(FPS)
    
pygame.quit()
print("User Quit")
























