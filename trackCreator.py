"""


    
"""

import pygame
import math
import colours
import json
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Car Track Designer")
done = False
mousePos = [0,0]

def saveTrack():
##    for line in track["mainTrack"]:
##        print(line)
##        if line[0][0] > line[1][0]:
##            leftPoint = line[1]
##            line[1] = line[0]
##            line[0] = leftPoint
##    for line in track["checkpoints"]:
##        if line[0][0] > line[1][0]:
##            leftPoint = line[1]
##            line[1] = line[0]
##            line[0] = leftPoint

    print("Track saved as: " + str(track))
    trackFile = open("track.txt", "w")
    json.dump(track, trackFile)
    trackFile.close()

def loadTrack():
    trackFile = open("track.txt", "r")
    track = json.load(trackFile)
    trackFile.close()
    return track

def mouseInCircle(pos, r):
    xDist = pos[0] - mousePos[0]
    yDist = pos[1] - mousePos[1]
    if math.hypot(xDist, yDist) < r:
        return True



track = loadTrack()

placeType = "main"
clickPos = None

print("Left Click - Place object")
print("Right Click - Remove line from mouse")
print("1 - Draw main track")
print("2 - Draw progress line")
print("8 - Clear main track")
print("9 - Clear progress line")
print("0 - Save track")

# -------- Main Program Loop -----------
while not done:
    mousePos = pygame.mouse.get_pos()
    for event in pygame.event.get():    # User did something
        if event.type == pygame.QUIT:   # If user clicked close
            print("User tried to quit")
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                print("Clicked at " + str(mousePos))

                if placeType == "main":
                    for line in track["mainTrack"]:
                        if mouseInCircle(line[0], 8):
                            mousePos = line[0]
                            break
                        if mouseInCircle(line[1], 8):
                            mousePos = line[1]
                            break
                    if clickPos != None:
                        track["mainTrack"].append([clickPos, mousePos])
                    clickPos = mousePos
                elif placeType == "check":   # Placing checkpoints
                    if clickPos != None:
                        if len(track["checkpoints"]) > 0 and mouseInCircle(track["checkpoints"][0][0], 8):
                            track["checkpoints"].append([clickPos, track["checkpoints"][0][0]])
                            clickPos = None
                        else:
                            track["checkpoints"].append([clickPos, mousePos])
                            clickPos = mousePos
                    else:
                        track["checkpoints"] = []
                        clickPos = mousePos
                        
            if event.button == 3:
                if placeType == "main":
                    clickPos = None
                elif placeType == "check":
                    if len(track["checkpoints"]) > 1 and track["checkpoints"][-1][1] != track["checkpoints"][0][0]:
                        track["checkpoints"].append([track["checkpoints"][0][0], track["checkpoints"][-1][1]])
                    clickPos = None
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                placeType = "main"
                clickPos = None
                print("Switch to Main Track")
            elif event.key == pygame.K_2:
                placeType = "check"
                print("Switch to Progress Track")
                clickPos = None
            elif event.key == pygame.K_8:
                track["mainTrack"] = []
                clickPos = None
                print("Cleared Main Track")
            elif event.key == pygame.K_9:
                track["checkpoints"] = []
                clickPos = None
                print("Cleared Progress Track")
            elif event.key == pygame.K_0:
                saveTrack()
                print("Saved Track")
    
    ### === Render === ###
    screen.fill(colours.LIGHT_PAPER)

    
    # Checkpoint lines
    for line in track["checkpoints"]:
        pygame.draw.line(screen, colours.LIGHT_RED, line[0], line[1], 8)

    # Main Track Lines
    for line in track["mainTrack"]:
        pygame.draw.line(screen, colours.LIGHT_BLUE, line[0], line[1], 10)

    # Lines to mouse
    if clickPos != None:
        if placeType == "main":
            pygame.draw.line(screen, colours.LIGHT_BLUE, clickPos, mousePos, 8)
        elif placeType == "check":
            pygame.draw.line(screen, colours.LIGHT_RED, clickPos, mousePos, 8)

    # Main track intercection dots
    for line in track["mainTrack"]:
        pygame.draw.circle(screen, colours.BLUE, line[0], 8)
        pygame.draw.circle(screen, colours.BLUE, line[1], 8)

    # Progress track intercection dots
    for line in track["checkpoints"]:
        pygame.draw.circle(screen, colours.RED, line[0], 8)
        pygame.draw.circle(screen, colours.RED, line[1], 8)

    # Player mouse dots
    if clickPos != None:
        if placeType == "main":
            pygame.draw.circle(screen, colours.BLUE, clickPos, 8)
        elif placeType == "check":
            pygame.draw.circle(screen, colours.RED, clickPos, 8)

    if placeType == "main":
        pygame.draw.circle(screen, colours.BLUE, mousePos, 7)
    elif placeType == "check":
        pygame.draw.circle(screen, colours.RED, mousePos, 7)
      
    pygame.display.update()
    
    
pygame.quit()
print("User Quit")
































