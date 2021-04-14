# -------- Imports --------

from tkinter import Tk, Frame, Canvas
from time import sleep

# -------- Tkinter Setup --------

root = Tk()
root.geometry('1000x1000+0+0')
root.resizable(False,False)
root.title('Cubex')
root.iconbitmap('icon.ico')

# -------- Input Setup --------

def bind():
    root.bind('<Up>',press)
    root.bind('<Down>',press)
    root.bind('<Left>',press)
    root.bind('<Right>',press)
    root.bind('<Return>',press)
    root.bind('<Escape>',press)

# -------- Canvas Setup --------

canvas = Canvas(root,width=1004, height=1004,bg='#ccc')
canvas.configure(scrollregion=(-2, -2, 1002, 1002))
canvas.pack(fill='both', expand=True)

# -------- Menu Functions --------

def UIMove(dire):
    global menuPointer, menuCurrent, menuList
    
    menuPointer += dire
    if menuPointer in (len(menuList[menuCurrent]),-1):
        UIMove(-dire)
    elif menuList[menuCurrent][menuPointer][1] == None:
        UIMove(dire)
    else:
        UIDraw()


def UIEnter():
    global menuPointer, menuCurrent, menuList

    newMenu = menuList[menuCurrent][menuPointer][1]
    if isinstance(newMenu,str):
        menuCurrent = newMenu
        menuPointer = 1
        UIMove(-1)
    else:
        newMenu()


def UIDraw():
    global menuPointer, menuCurrent, menuActive, menuList, menuLevel

    canvas.delete('all')

    count = len(menuList[menuCurrent])
    dist = -120 if count < 8 else -90
    
    for index, line in enumerate(menuList[menuCurrent]):
        size = 70 if menuCurrent != '@dog' else 40
        if line[0] == 'Cubex':
            size = 120

        color = '#000' if menuPointer != index else '#f00'
        yAxis = dist*((len(menuList[menuCurrent])/2-index)-0.5)
        
        canvas.create_text(500,yAxis+500,fill=color,\
        font=('Courier',size), text=line[0].format(menuLevel))

# -------- Game Functions --------

def createLevel():
    global menuLevel, levelArray, file, blockSize, bS, menuActive, playerPos, blockReplace
    levelArray = []
    pointer = file.find('\n',file.find('#Level {}'.format(menuLevel)))

    while file[pointer] != '#':
        if file[pointer] == '\n':
            levelArray.append([])
            pointer -= 1

        else:
            levelArray[-1].append([])
            if file[pointer] in blockTexture:
                levelArray[-1][-1].append(file[pointer])
                
            if file[pointer] in blockReplace:
                for block in blockReplace[file[pointer]]:
                        levelArray[-1][-1].append(block)


            if file[pointer] == 'P':
                playerPos = [len(levelArray[-1]) - 1, len(levelArray) - 1]
        
            if file[pointer+1] != file[pointer]:
                if file[pointer+1] in blockTexture:
                    levelArray[-1][-1].append(file[pointer+1])
                
                if file[pointer+1] in blockReplace:
                    for block in blockReplace[file[pointer+1]]:
                        levelArray[-1][-1].append(block)

        pointer += 2
        

    for y, line in enumerate(levelArray):
        for x, square in enumerate(line):
            for dire in ('8','6','2','4'):
                if dire in square:
                    pos = addTuples((x,y),convert(dire))
                    
                    if 'D' not in levelArray[pos[1]][pos[0]]:
                        if 'O' not in levelArray[pos[1]][pos[0]]:
                            
                            if len(levelArray) > pos[0] >= 0 or len(levelArray[-1]) > pos[1] >= 0:
                                levelArray[pos[1]][pos[0]].append(str(int(dire) + 1))
                

    menuActive = False
    bS = 1000/len(levelArray)
    draw()

def move(block,pos,dire):
    global levelArray, playerPos

    new = addTuples(pos,dire)
    
    levelArray[pos[1]][pos[0]].remove(block)
    levelArray[new[1]][new[0]].append(block)

    if block == 'P':
        playerPos = addTuples(playerPos,dire)

    draw()
    
def update(block,pos,dire):
    global levelArray, menuActive, menuCurrent, menuLevel
    
    new = addTuples(pos,dire)
    newNew = addTuples(new,dire)

    if block == 'P':    
        if 'W' in levelArray[new[1]][new[0]]:
            return False

        if 'G' in levelArray[new[1]][new[0]]:
            if 'C' not in levelArray[new[1]][new[0]]:
                menuActive = True
                menuCurrent = '@win'
                menuLevel += 1
                UIMove(-1)
                UIDraw()
                return 'Win'

        if 'D' in levelArray[new[1]][new[0]]:
            return False
        
        if 'C' in levelArray[new[1]][new[0]]:
            for i in ['C','W']:
                if i in levelArray[newNew[1]][newNew[0]]:
                    return False

            if 'D' in levelArray[newNew[1]][newNew[0]]:
                if 'O' not in levelArray[newNew[1]][newNew[0]]:
                    return False
                
            move('C',new,dire)
            move('P',pos,dire)

            if 'B' in levelArray[newNew[1]][newNew[0]]:
                update('R',newNew,(1,1))

            if 'B' in levelArray[new[1]][new[0]]:
                update('R',new,(0,0))

        else:
            move('P',pos,dire)

    elif block == 'R':
        for i in levelArray[pos[1]][pos[0]]:
            if i in ['8','6','2','4']:
                
                nex = convert(i)
                new = addTuples(pos,nex)

                for j in ['D','O']:
                    if j in levelArray[new[1]][new[0]]:
                        update('D',new,dire)
                        break

                else:
                    update('R',new,dire)

    elif block == 'D':
        if dire[0] == 1:
            levelArray[pos[1]][pos[0]].append('O')
            
            if 'D' in levelArray[pos[1]][pos[0]]:
                levelArray[pos[1]][pos[0]].remove('D')
                
            draw()
            pass

        else:
            if 'O' in levelArray[pos[1]][pos[0]]:
                levelArray[pos[1]][pos[0]].remove('O')
                
            if 'O' not in levelArray[pos[1]][pos[0]]:
                levelArray[pos[1]][pos[0]].append('D')
            draw()
    
    
def draw():
    global levelArray, blockSize, bS

    canvas.delete('all')

    for y, line in enumerate(levelArray):
        for x, square in enumerate(line):
            for block in square:
                for inst in blockTexture[block]:
                    canvas.create_rectangle((x+inst[0]/8)*bS,(y+inst[1]/8)*bS,(x+inst[2]/8)*bS,(y+inst[3]/8)*bS,fill=inst[4],width=0)

# -------- Secondary Functions --------

def press(event):
    global menuActive, menuCurrent, menuPointer, menuLevel, playerPos

    if menuActive:
        if event.keysym == 'Up':
            if menuLevel > 1 and menuCurrent == '@level': menuLevel -= 1
            UIMove(-1)
            
        elif event.keysym == 'Down':
            if menuLevel < levelCount and menuCurrent == '@level': menuLevel += 1
            UIMove(1)
            
        elif event.keysym == 'Return':
            UIEnter()
            
        elif event.keysym == 'Escape':
            menuCurrent = '@main'
            menuPointer = 2
            UIDraw()

    else:
        if event.keysym == 'Up':
            update('P',playerPos,(0,-1))

        elif event.keysym == 'Right':
            update('P',playerPos,(1,0))

        elif event.keysym == 'Down':
            update('P',playerPos,(0,1))

        elif event.keysym == 'Left':
            update('P',playerPos,(-1,0))

        elif event.keysym == 'Escape':
            menuCurrent = '@level'
            menuPointer = 1
            menuActive = True
            UIDraw()

def convert(dire):
    offsets = [(0,-1),(1,0),(0,1),(-1,0),'8','6','2','4']
    directions = ['8','6','2','4',(0,-1),(1,0),(0,1),(-1,0)]
    return directions[offsets.index(dire)]

def addTuples(T1,T2):
    return (T1[0] + T2[0], T1[1] + T2[1])

# -------- Global menu variables --------

menuPointer = 2
menuLevel = 1
menuCurrent = '@main'
menuActive = True
menuList = {
    '@main':(
        ('Cubex',None),
        ('',None),
        ('Play','@level'),
        ('Help','@help'),
        ('Dog','@dog'),
        ('Exit',root.destroy,None)),
    '@level':(
        ('▲',None),
        ('Level {}',createLevel),
        ('▼',None)),
    '@help':(
        ('Move: Arrow Keys',None),
        ('Confirm: Enter',None),
        ('Exit: Escape',None),
        ('',None),
        ('Ok','@main')),
    '@dog':(
        ('',None),
        ('',None),
        ('',None),
        ('\
░░░░░░░░░▄░░░░░░░░░░░░░░▄░░░░\n░░░░░░░░▌▒█░░░░░░░░░░░▄▀▒▌░░░\n░░░░░░░░▌▒▒█░░░░░░░░▄▀▒▒▒▐░░░\n\
░░░░░░░▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐░░░\n░░░░░▄▄▀▒░▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐░░░\n░░░▄▀▒▒▒░░░▒▒▒░░░▒▒▒▀██▀▒▌░░░\n\
░░▐▒▒▒▄▄▒▒▒▒░░░▒▒▒▒▒▒▒▀▄▒▒▌░░\n░░▌░░▌█▀▒▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒▐░░\n░▐░░░▒▒▒▒▒▒▒▒▌██▀▒▒░░░▒▒▒▀▄▌░\n\
░▌░▒▄██▄▒▒▒▒▒▒▒▒▒░░░░░░▒▒▒▒▌░\n▐▒▀▐▄█▄█▌▄░▀▒▒░░░░░░░░░░▒▒▒▐░\n▐▒▒▐▀▐▀▒░▄▄▒▄▒▒▒▒▒▒░▒░▒░▒▒▒▒▌\n\
▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒▒▒░▒░▒░▒▒▐░\n░▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒░▒░▒░▒░▒▒▒▌░\n░▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▒▄▒▒▐░░\n\
░░▀▄▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▄▒▒▒▒▌░░\n░░░░▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀░░░\n░░░░░░▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀░░░░░\n\
░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▀▀░░░░░░░░',None),
        ('',None),
        ('',None),
        ('Ok','@main')),
    '@win':(
        ('You win!',None),
        ('',None),
        ('Next Level',createLevel),
        ('Exit','@level'))
    }

# -------- Global game variables --------

playerPos = []
levelArray = []
with open('gameData.txt','r') as F:
    file = F.read()

index = 1
levelCount = 0
while True:
    if file.find('#Level {}'.format(index)) != -1:
        levelCount += 1
        index += 1
    else:
        break

blockReplace = {
    '9':('8','6'),
    '3':('6','2'),
    '1':('2','4'),
    '7':('4','8'),
    'F':('B','C')
    }

blockTexture = { # for every block tuple of instructions
    'W':(
        (0,0,8,8,'#000'),
        (0,1,3,4,'#777'),
        (4,1,8,4,'#777'),
        (0,5,7,8,'#777')),
    'P':(
        (0,0,8,8,'#eb0'),
        (1,1,7,7,'#fc0'),
        (1,2,7,4,'#fff'),
        (2,3,6,4,'#000'),
        (3,2,5,4,'#fc0')),
    'G':(
        (0,0,2,8,'#000'),
        (2,0,8,5,'#7f0')),
    'C':(
        (0,0,8,8,'#b95'),
        (1,1,7,7,'#ca6')),
    'B':(
        (0,0,8,8,'#aaa'),
        (1,1,7,7,'#a00')),
    'D':(
        (0,0,3,8,'#22a'),
        (3,0,5,8,'#77a'),
        (5,0,8,8,'#22a')),
    'O':(
        (0,0,1,8,'#22a'),
        (7,0,8,8,'#22a')),
    '8':(
        (3,0,5,5,'#a00'),
        (3,0,5,2,'#700')),
    '6':(
        (3,3,8,5,'#a00'),
        (6,3,8,5,'#700')),
    '2':(
        (3,3,5,8,'#a00'),
        (3,6,5,8,'#700')),
    '4':(
        (0,3,5,5,'#a00'),
        (0,3,2,5,'#700')),
    '9':(
        (3,3,5,8,'#a00'),),
    '7':(
        (0,3,5,5,'#a00'),),
    '3':(
        (3,0,5,5,'#a00'),),
    '5':(
        (3,3,8,5,'#a00'),)
    }

# -------- Finals --------

bind()
UIDraw()



root.mainloop()
