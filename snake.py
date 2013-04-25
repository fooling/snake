#-*- coding:utf-8 -*-
import curses
import time
import random


#screen
WIDTH=10;
HEIGHT=10;

#food
FOOD='$'
FOOD_P=[]
SNAKES=[]

PLAT=curses.initscr()

SCR=curses.newwin(HEIGHT,WIDTH,5,5)
LOG=curses.newwin(10,30,30,20)

PLAT.border(0)

HEAD_MAP={
    1:'^',
    2:'v',
    3:"<",
    4:">",
}
DIRECT_MAP={
    119:1,
    115:2,
    97:3,
    100:4  
}


def add_food(x,y):
    FOOD_P.append((x,y))

def create_food():
    isfree=False
    x=0;y=0
    while not isfree:
        flag=False
        x=random.randint(0,WIDTH-1)
        y=random.randint(0,HEIGHT-1)
        if (x,y) in FOOD_P:
            flag=True
        for i in SNAKES:
            if i.taken((x,y)):
                flag=True
                
        if flag is True:
            continue
        break
    add_food(x,y)
    
def remove_food((x,y)):
    try:
        FOOD_P.remove((x,y))
    except:
        return False

    create_food()
    return True

class Snake(object):
    #(x,y)
    __head=tuple()

    #body(-1) is the first body
    __body=[]

    __eat=False
    
    __direct=None

    def __init__(self,x,y):
        self.__head=(x,y)

        pass
    def taken(self,(x,y)):
        if (x,y) in self.__body+[self.__head]:
            return True
        return False
    
    def run(self):
        self.__move()
        if self.__judge() is True:
            self.__frame()
        else:
            pass
            #import pdb;pdb.set_trace()
            #curses.endwin()
        
    def __move(self):
        
        tmphead=self.__head

        if self.__direct in range(1,5):
            if self.__direct==1:
                #up
                self.__head=(self.__head[0],self.__head[1]-1)
            if self.__direct==2:
                #down
                self.__head=(self.__head[0],self.__head[1]+1)
            if self.__direct==3:
                #left
                self.__head=(self.__head[0]-1,self.__head[1])
            if self.__direct==4:
                #left
                self.__head=(self.__head[0]+1,self.__head[1])
        else:
            return False

        if len(self.__body)==0:
            if self.__eat:
                self.__body.append(tmphead)
        else:
            if not self.__eat:
                self.__body.pop(0)
            self.__body.append(tmphead)

                
        if self.__eat is True:
            self.__eat=False


    def dump(self):
        print self.__head
        print self.__body

    def __judge(self):
        if self.__head[0]<0 or self.__head[0]>=WIDTH:
            return False
        if self.__head[1]<0 or self.__head[1]>=HEIGHT:
            return False
        if self.__head in self.__body:
            #import pdb;pdb.set_trace()
            return False
        if self.__head in FOOD_P:
            self.__eat=True
            remove_food(self.__head)
        return True

    def __frame(self):
        SCR.clear()
        SCR.border(1)
        for i in self.__body:
            SCR.addch(i[1],i[0],'*')
        SCR.addch(self.__head[1],self.__head[0],HEAD_MAP.get(self.__direct,'+'))
        for i in FOOD_P:
            try:
                SCR.addch(i[1],i[0],'$')
            except:
                import pdb;pdb.set_trace()
            
            
        SCR.refresh()

        LOG.clear()
        LOG.addstr(0,0,"head: (%d,%d)"%self.__head)
        LOG.refresh()

        time.sleep(0.1)

    def set_direct_by_key(self,key):
        if k in DIRECT_MAP:
            direct=DIRECT_MAP.get(k) 
            if len(self.__body)==0:
                #can turn every direction
                self.__direct=direct
                return True
            if self.__direct==1 and direct ==2:
                return False
            if self.__direct==2 and direct ==1:
                return False
            if self.__direct==3 and direct ==4:
                return False
            if self.__direct==4 and direct ==3:
                return False
            
            self.__direct=direct

    def set_direct(self,direct):
        self.__direct=direct

    def route(self):
        routes=[]
        queue=[]
        
        

            
            


    


r'''
for i in xrange(WIDTH-1):
    for j in xrange(HEIGHT-1):
        SCR.clear()
        SCR.border(1)
        add_food(j,i)
        SCR.refresh()
        time.sleep(0.1)
'''

s=Snake(4,5)
SNAKES.append(s)



create_food()
s.run()
k=SCR.getch()
while k!=27:
    k=SCR.getch()
    s.set_direct_by_key(k)
    s.run()
    #SCR.addstr(0,0,"k=%d" % k)




curses.endwin()

