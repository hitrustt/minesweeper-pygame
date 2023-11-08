from random import randrange
import pygame
from settings import *

lost = 0
won = 0


class Cell:
    mine = False
    clicked = False
    marked = False
    flagged = False
    neighbor_mines = 0


class Minesweeper:
    width = 10
    height = 10
    mineCount = 10
    flagCount = 10
    uncoveredCells = 0
    safeTiles = 0
    incorrectFlag = 0
    best_time = 0
    firstClick = True
    gameOver = False
    gameWon = False
    field = []

    def __init__(self, width, height, mineCount):
        self.width = width
        self.height = height
        self.mineCount = min(mineCount, width * height - 9)
        self.flagCount = self.mineCount
        for x in range(width):
            self.field.append([])
            for y in range(height):
                self.field[x].append([])
                self.field[x][y] = Cell()

    # Updates a given cell with the count of neighboring mines
    def updateCellNeighborCount(self, x, y):
        self.field[x][y].neighbor_mines = self.getCellNeighborMineCount(x, y)

    def find_safe_tiles(ms):
        safe_tiles = set()
        for x in range(ms.width):
            for y in range(ms.height):
                if ms.field[x][y].clicked and ms.field[x][y].neighbor_mines > 0:
                    marked_neighbors = sum(1 for nx, ny in ms.field[x][y].neighborIndices if ms.field[nx][ny].marked)
                    if marked_neighbors == ms.field[x][y].neighbor_mines:
                        for nx, ny in ms.field[x][y].neighborIndices:
                            if not ms.field[nx][ny].clicked and not ms.field[nx][ny].marked:
                                safe_tiles.add((nx, ny))
        return safe_tiles

    def getNeighboringIndices(self, x, y):
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
            if y > 0:
                neighbors.append((x - 1, y - 1))
            if y < ms.height - 1:
                neighbors.append((x - 1, y + 1))
        if y < ms.height - 1:
            neighbors.append((x, y + 1))
        if y > 0:
            neighbors.append((x, y - 1))
        if x < ms.width - 1:
            neighbors.append((x + 1, y))
            if y > 0:
                neighbors.append((x + 1, y - 1))
            if y < ms.height - 1:
                neighbors.append((x + 1, y + 1))
        return neighbors

    # Counts the number of surrounding mines
    def getCellNeighborMineCount(self, x, y):
        mines = 0
        if x > 0:
            if (self.field[x - 1][y].mine):
                mines += 1
            if y > 0:
                if (self.field[x - 1][y - 1].mine):
                    mines += 1
            if y < self.height - 1:
                if (self.field[x - 1][y + 1].mine):
                    mines += 1
        if y < self.height - 1:
            if (self.field[x][y + 1].mine):
                mines += 1
        if y > 0:
            if (self.field[x][y - 1].mine):
                mines += 1
        if x < self.width - 1:
            if (self.field[x + 1][y].mine):
                mines += 1
            if y > 0:
                if (self.field[x + 1][y - 1].mine):
                    mines += 1
            if y < self.height - 1:
                if (self.field[x + 1][y + 1].mine):
                    mines += 1
        return mines

    def getCellFromTuple(self, t):
        return self.field[t[0]][t[1]]

    # Resets the game state
    def resetField(self):
        self.flagCount = self.mineCount
        self.uncoveredCells = 0
        self.incorrectFlag = 0
        self.safeTiles = 0
        self.start_time = None
        self.gameOver = False
        self.gameWon = False
        self.firstClick = True
        for x in range(self.width):
            for y in range(self.height):
                self.field[x][y].mine = False
                self.field[x][y].clicked = False
                self.field[x][y].marked = False
                self.field[x][y].neighbor_mines = 0
                self.field[x][y].neighborIndices = self.getNeighboringIndices(x, y)
                self.field[x][y].mineProbability = 0

    # Generates the minefield, with no mine on safeX and safeY and one block radius surrounding it
    def generateField(self, safeX, safeY):
        minesToGenerate = self.mineCount
        while (minesToGenerate):
            x = randrange(self.width)
            y = randrange(self.height)
            if ((x != safeX) or (y != safeY)) and ((x != safeX - 1) or (y != safeY)) and (
                    (x != safeX - 1) or (y != safeY - 1)) and ((x != safeX - 1) or (y != safeY + 1)) and (
                    (x != safeX) or (y != safeY + 1)) and ((x != safeX) or (y != safeY - 1)) and (
                    (x != safeX + 1) or (y != safeY + 1)) and ((x != safeX + 1) or (y != safeY)) and (
                    (x != safeX + 1) or (y != safeY - 1)) and self.field[x][y].mine == False:
                # if ((x != safeX) or (y != safeY)) and self.field[x][y].mine == False:
                self.field[x][y].mine = True
                minesToGenerate -= 1
        for x in range(self.width):
            for y in range(self.height):
                self.field[x][y].neighbor_mines = self.getCellNeighborMineCount(x, y)
                self.field[x][y].neighborIndices = self.getNeighboringIndices(x, y)

    # Sets a flag at the select location
    def setFlag(self, x, y):
        if (self.field[x][y].clicked) or (self.gameOver) or (self.gameWon):
            return
        if (not self.field[x][y].mine):

            if (not self.field[x][y].marked):
                self.incorrectFlag += 1
            else:
                self.incorrectFlag -= 1
        if (not self.field[x][y].marked) and (self.flagCount > 0):
            self.field[x][y].marked = True

            safe_tiles = ms.find_safe_tiles()
            self.safeTiles = len(safe_tiles)

            self.flagCount -= 1
        elif (self.field[x][y].marked):
            self.field[x][y].marked = False

            safe_tiles = ms.find_safe_tiles()
            self.safeTiles = len(safe_tiles)

            self.flagCount += 1

    # Uncovers all surrounding fields that do not contain a mine
    # This is done via recursive calls of the click-method
    def uncoverNeighbors(self, x, y):
        if x > 0:
            if (not self.field[x - 1][y].mine):
                self.click(x - 1, y)
            if y > 0:
                if (not self.field[x - 1][y - 1].mine):
                    self.click(x - 1, y - 1)
            if y < self.height - 1:
                if (not self.field[x - 1][y + 1].mine):
                    self.click(x - 1, y + 1)
        if y < self.height - 1:
            if (not self.field[x][y + 1].mine):
                self.click(x, y + 1)
        if y > 0:
            if (not self.field[x][y - 1].mine):
                self.click(x, y - 1)
        if x < self.width - 1:
            if (not self.field[x + 1][y].mine):
                self.click(x + 1, y)
            if y > 0:
                if (not self.field[x + 1][y - 1].mine):
                    self.click(x + 1, y - 1)
            if y < self.height - 1:
                if (not self.field[x + 1][y + 1].mine):
                    self.click(x + 1, y + 1)

    # Clicks a field and updates the game state accordingly (explodes a mine if one is present, uncovers neighbors if
    # there are no surrounding mines, etc)
    def click(self, x, y):
        if (self.gameOver) or (self.gameWon):
            return
        # Generate field after first click, to avoid starting with mine
        if (self.firstClick):
            self.generateField(x, y)
            self.firstClick = False
            self.click(x, y)
            self.start_time = pygame.time.get_ticks()
        elif (not self.field[x][y].clicked):
            if self.field[x][y].marked:  # Check if the cell is marked
                return  # If marked, return without doing anything
            self.field[x][y].clicked = True
            self.uncoveredCells += 1
            if self.field[x][y].mine:
                self.gameOver = True

            else:
                if (self.field[x][y].marked == True):
                    self.field[x][y].marked = False
                    self.flagCount += 1
                if (self.uncoveredCells == self.width * self.height - self.mineCount):
                    self.gameWon = True
                    self.end_time = pygame.time.get_ticks()
                    elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
                    if elapsed_time < self.best_time or self.best_time == 0:
                        self.best_time = elapsed_time
                if (self.field[x][y].neighbor_mines == 0):
                    self.uncoverNeighbors(x, y)


# Takes a screen, font, and minesweeper instance and draws it. The font is needed for the number of surrounding mines
def drawMS(screen, font, ms):
    for x in range(ms.width):
        for y in range(ms.height):

            if (x + y) % 2 == 0:
                color = (178, 214, 99)
            else:
                color = (170, 207, 92)

            if (x + y) % 2 == 0 and ms.field[x][y].clicked:
                color_clicked = (224, 196, 162)
            else:
                color_clicked = (210, 185, 156)

            if ((ms.field[x][y].clicked) or (ms.gameOver)) and (ms.field[x][y].mine):
                pygame.draw.rect(screen, red, (
                    borderWH + (cellPixelWH + borderWH) * x, borderWH + (cellPixelWH + borderWH) * y, cellPixelWH,
                    cellPixelWH), 0)
                if (ms.field[x][y].marked):
                    srf = font.render("!", True, white)
                    screen.blit(srf, ((borderWH + (cellPixelWH + borderWH) * x + cellPixelWH // 2.5,
                                       borderWH + (cellPixelWH + borderWH) * y + cellPixelWH // 4)))
            elif (ms.field[x][y].clicked) and (not ms.field[x][y].mine):
                pygame.draw.rect(screen, color_clicked, (
                    borderWH + (cellPixelWH + borderWH) * x, borderWH + (cellPixelWH + borderWH) * y, cellPixelWH,
                    cellPixelWH), 0)
                font.render(str(ms.field[x][y].neighbor_mines), True, white)

                if ms.field[x][y].neighbor_mines > 0:
                    srf = font.render(str(ms.field[x][y].neighbor_mines), True,
                                      number_colors.get(ms.field[x][y].neighbor_mines))
                    screen.blit(srf, ((borderWH + (cellPixelWH + borderWH) * x + cellPixelWH // 2.5,
                                       borderWH + (cellPixelWH + borderWH) * y + cellPixelWH // 4)))
            else:
                pygame.draw.rect(screen, color, (
                    borderWH + (cellPixelWH + borderWH) * x, borderWH + (cellPixelWH + borderWH) * y, cellPixelWH,
                    cellPixelWH), 0)
                if (ms.field[x][y].marked):
                    srf = font.render("!", True, red)
                    screen.blit(srf, ((borderWH + (cellPixelWH + borderWH) * x + cellPixelWH // 2.5,
                                       borderWH + (cellPixelWH + borderWH) * y + cellPixelWH // 4)))


# Converts mouse coordinates to cell coordinates within the minefield
def mouseToField(x, y):
    fieldX = int(x / (cellPixelWH + borderWH))
    fieldY = int(y / (cellPixelWH + borderWH))
    return [fieldX, fieldY]


def printText(ms, font, screen):
    srf = font_text.render("Flags: " + str(ms.flagCount), True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 0)))

    srf = font_text.render("STATS", True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 90)))
    srf = font_text.render("Games: " + str(won + lost), True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 110)))
    if (won + lost > 0):
        percentage = round((won / (won + lost)) * 100, 2)
    else:
        percentage = "-"
    srf = font_text.render("Wins: " + str(won) + ", " + str(percentage) + "%", True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 130)))
    srf = font_text.render("Losses: " + str(lost), True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 150)))
    srf = font_text.render("Incorrect Flags: " + str(ms.incorrectFlag), True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 170)))
    srf = font_text.render("Safe Tiles: " + str(ms.safeTiles), True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 190)))
    srf = font_text.render("Best Time: " + str(ms.best_time), True, white)
    screen.blit(srf, ((ms.width * (cellPixelWH + borderWH) + borderWH + 10, 210)))

    srf = font.render(str(fieldCoord[0]) + ", " + str(fieldCoord[1]), True, white)
    screen.blit(srf, (
        (ms.width * (cellPixelWH + borderWH) + borderWH + 10, ms.height * (cellPixelWH + borderWH) + borderWH - 60)))


pygame.init()
ms = Minesweeper(width, height, mineCount)
font = pygame.font.SysFont("segoeuisemibold", 20)
font_text = pygame.font.SysFont("segoeuisemibold", 20)
screen = pygame.display.set_mode(
    (ms.width * (cellPixelWH + borderWH) + borderWH + 250, ms.height * (cellPixelWH + borderWH) + borderWH))

running = True
waitForNG = False
first_random_click = None

while running:
    fieldCoord = mouseToField(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Space bar to reset the game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                first_random_click = None
                ms.resetField()
                waitForNG = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if (fieldCoord[0] < ms.width) and (fieldCoord[1] < ms.height):
                    ms.click(fieldCoord[0], fieldCoord[1])

            # Right click to flag a spot
            if pygame.mouse.get_pressed()[2]:
                if (fieldCoord[0] < ms.width) and (fieldCoord[1] < ms.height):
                    ms.setFlag(fieldCoord[0], fieldCoord[1])

        if not first_random_click:
            first_random_click = [randrange(width), randrange(height)]
            ms.click(first_random_click[0], first_random_click[1])
    screen.fill(green)
    drawMS(screen, font, ms)
    if ms.gameOver or ms.gameWon:
        if not waitForNG:
            if ms.gameOver:
                first_random_click = None
                lost += 1
            if ms.gameWon:
                first_random_click = None
                won += 1
            ms.resetField()
            waitForNG = False
    printText(ms, font_text, screen)
    pygame.display.update()

pygame.quit()
