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
WALL='@'

PLAT=curses.initscr()

SCR=curses.newwin(HEIGHT+1,WIDTH+1,5,5)
LOG=curses.newwin(10,30,30,20)

def make_border():
    for i in xrange(1,WIDTH):
        SCR.addch(0,i,WALL)
        SCR.addch(HEIGHT,i,WALL)
    for i in xrange(1,HEIGHT):
        SCR.addch(i,0,WALL)
        SCR.addch(i,WIDTH,WALL)


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

def log(message):
    with open("log.txt",'a') as fp:
        fp.write(message)
        fp.write("\n")

r'''
Judge if the dot is in range of map
'''
def valid_pos(pos):
    if pos[0]>=WIDTH or pos[0]<=0:
        return False
    if pos[1]>=HEIGHT or pos[1]<=0:
        return False
    return True




r'''
Add food to specified position
'''
def add_food(x,y):
    FOOD_P.append((x,y))

r'''
Randomly create food
'''
def create_food():
    isfree=False
    x=0;y=0
    while not isfree:
        flag=False
        x=random.randint(1,WIDTH-1)
        y=random.randint(1,HEIGHT-1)
        if (x,y) in FOOD_P:
            flag=True
        for i in SNAKES:
            if i.taken((x,y)):
                flag=True
                
        if flag is True:
            continue
        break
    add_food(x,y)
    
r'''
Remove food on specified position
'''
def remove_food((x,y)):
    try:
        FOOD_P.remove((x,y))
    except:
        return False

    create_food()
    return True


r'''
{n:p}   n is the next move of p
up:1
down:2
left:3
right:4
'''
def move_method(p,n):
    #up
    if n[1]-p[1]== -1 and n[0]==p[0]:
        return 1
    #down
    if n[1]-p[1]== 1 and n[0]==p[0]:
        return 2
    #left
    if n[0]-p[0]== -1 and n[1]==p[1]:
        return 3
    #right
    if n[0]-p[0]== 1 and n[1]==p[1]:
        return 4
    return Fplse


class Snake(object):
    #(x,y)
    __head=tuple()

    #body(-1) is the first body
    __body=[]

    __eat=False
    
    __direct=None

    def __init__(self,x,y,body):
        self.__head=(x,y)
        self.BODY=body

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
            #game over
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
        if not valid_pos(self.__head):
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
        make_border()
        for i in self.__body:
            SCR.addch(i[1],i[0],self.BODY)
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

    r'''
    Given the previous dot,  get next possible moves
    '''
    def get_next(self,pos,prev=()):
        rtn=[]
        tmprtn=[]
        tmprtn.append((pos[0]-1,pos[1]))
        tmprtn.append((pos[0]+1,pos[1]))
        tmprtn.append((pos[0],pos[1]-1))
        tmprtn.append((pos[0],pos[1]+1))
        try:
            tmprtn.remove(prev)
        except:
            pass

        for i in tmprtn:
            if not valid_pos(i):
                #log("not valid : %s\n"% unicode(i))
                continue
                tmprtn.remove(i)
            if i in self.__body:
                #log("in body: %s\n"% unicode(i))
                continue
            
            rtn.append(i)
            
        
        return rtn



    def DFS_tree(self):
        #tree of relationship
        relations={}
        #queue of undiscovered positions
        queue=[]
        if len(FOOD_P)==0:
            return {}
        
        start=self.__head
        preadd=[]

        if len(self.__body)==0:
            #import pdb;pdb.set_trace()
            preadd=self.get_next(start)
        else:
            preadd=self.get_next(start,self.__body[-1])
        
        for i in preadd:
            relations.update({i:start})
            queue.append(i)
            if i in FOOD_P:
                return relations
        
        while len(queue) !=0:
            tmp=queue.pop(0)
            preadd=self.get_next(tmp)
            for i in preadd:
                if i not in relations:
                    relations.update({i:tmp})
                    queue.append(i)
                    if i in FOOD_P:
                        return relations
            log("loop: %s\n"%unicode(queue))

        
        log("end of tree\n")
        return {}
    def tree2direct(self,tree={}):
        r'''

            end: one position
            last: the position before end
            start: start position

        '''
        if len(tree)==0:
            return []
        end=()
        operation=[]
        for i in FOOD_P:
            if i in tree:
                end=i
        start=self.__head

        last=tree.get(end)
        while last!=start and last !=():
            method=move_method(last,end)
            if method!=False:
                operation.append(method)
            end=last
            last=tree.get(last,())

        if last==start:
            method=move_method(last,end)
            if method!=False:
                operation.append(method)
            
        return operation
        
    def route(self):
        #thei=0
        while 1:
            #log("the %d try\n"%thei)
            #thei+=1
            tree={}
            #log("body: %s"% unicode(self.__body))
            tree=self.DFS_tree()
            #log("tree: %s"% unicode(tree))

            
            if len(tree)==0:
                return
            ops=self.tree2direct(tree)
            if len(ops) !=0:
                for i in ops[::-1]:
                    self.set_direct(i)
                    self.run()


            
            r'''
            '''

        return 
            
        
            
            
        
            

            
            


    


r'''
for i in xrange(WIDTH-1):
    for j in xrange(HEIGHT-1):
        SCR.clear()
        SCR.border(1)
        add_food(j,i)
        SCR.refresh()
        time.sleep(0.1)
'''

s=Snake(4,5,'*')
SNAKES.append(s)



create_food()
s.route()
s.run()
k=SCR.getch()
while k!=27:
    k=SCR.getch()
    s.set_direct_by_key(k)
    s.run()
    #SCR.addstr(0,0,"k=%d" % k)




curses.endwin()

