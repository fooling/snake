#-*- coding:utf-8 -*-
import curses
import time
import random
from abc import ABCMeta, abstractmethod


#screen
WIDTH=9;
HEIGHT=9;

#food
FOOD='$'
FOOD_P=[]
FOOD_NUM=1
SNAKES=[]
WALL='@'

FPS=10.0
GAP=1/FPS
with open("log.txt","w") as flusher:
    pass

PLAT=curses.initscr()

SCR=curses.newwin(HEIGHT+1,WIDTH+1,2,2)
LOG=curses.newwin(10,30,30,60)

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


r'''
Base class for BOTH real and virtual snakes
'''
class BaseSnake(object):
    #(x,y)
    _head=tuple()

    #body(-1) is the first body
    _body=[]

    _direct=None

    _eat=False

    
    def __init__(self):
        pass

    def taken(self,(x,y)):
        if (x,y) in self._body+[self._head]:
            return True
        return False

    def _move(self):
        
        tmphead=self._head

        if self._direct in range(1,5):
            if self._direct==1:
                #up
                self._head=(self._head[0],self._head[1]-1)
            if self._direct==2:
                #down
                self._head=(self._head[0],self._head[1]+1)
            if self._direct==3:
                #left
                self._head=(self._head[0]-1,self._head[1])
            if self._direct==4:
                #left
                self._head=(self._head[0]+1,self._head[1])
        else:
            return False

        if len(self._body)==0:
            if self._eat:
                self._body.append(tmphead)
        else:
            if not self._eat:
                self._body.pop(0)
            self._body.append(tmphead)

                
        if self._eat is True:
            self._eat=False

    @abstractmethod
    def _judge(self):
        pass

    def set_direct(self,direct):
        self._direct=direct

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
            if i in self._body:
                #log("in body: %s\n"% unicode(i))
                if i in self._body[1:]:
                    #log("in body")
                    continue
            
            rtn.append(i)
            
        #randomly choose a direction
        random.shuffle(rtn)
        #log("rtn: %s"%unicode(rtn))
        
        return rtn



    def BFS_tree(self,dsts):
        #tree of relationship
        relations={}
        #queue of undiscovered positions
        queue=[]
        if len(dsts)==0:
            return {}
        
        start=self._head
        preadd=[]

        if len(self._body)==0:
            #import pdb;pdb.set_trace()
            preadd=self.get_next(start)
        else:
            preadd=self.get_next(start,self._body[-1])
        
        for i in preadd:
            relations.update({i:start})
            queue.append(i)
            if i in dsts:
                return relations
        
        while len(queue) !=0:
            tmp=queue.pop(0)
            preadd=self.get_next(tmp)
            for i in preadd:
                if i not in relations:
                    relations.update({i:tmp})
                    queue.append(i)
                    if i in dsts:
                        return relations
            log("loop: %s\n"%unicode(queue))

        
        log("end of tree\n")
        return {}
    def tree2direct(self,dsts,tree={}):
        r'''

            end: one position
            last: the position before end
            start: start position

        '''
        if len(tree)==0:
            return []
        end=()
        operation=[]
        for i in dsts:
            if i in tree:
                end=i
        start=self._head

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

class VirtualSnake(BaseSnake):
    
    def __init__(self,head,body):
        #Init virtual snake by real snake
        BaseSnake.__init__(self)
        self._head=head[:]
        self._body=body[:]
        self.__real_head=head
        self.__real_body=body
        #Auto get direction by relation of head and body
        if len(body) !=0:
            self._direct=move_method(body[-1],head)
        else:
            self._direct=None

        self.__real_direct=self._direct

    def __reset(self):
        self._head=self.__real_head[:]
        self._body=self.__real_body[:]
        self._direct=self.__real_direct


    def _judge(self):
        if not valid_pos(self._head):
            return False
        if self._head in self._body:
            #import pdb;pdb.set_trace()
            return False
        if self._head in FOOD_P:
            self._eat=True
        return True


    def run(self):
        self._move()
        #self._judge()

    def __to_food(self):
        tree={}
        ops=[]   #operation

        tree=self.BFS_tree(FOOD_P)

        
        #log("tree: %s"% unicode(tree))
        if len(tree)!=0:
            ops=self.tree2direct(FOOD_P,tree)
            if len(ops)!=0:
                for i in ops[::-1]:
                    self.set_direct(i)
                    self.run()
            else:
                log("Unexpected error")

            #operations to get to food
            return ops

        #can not see any food
        return []
    
    def last_move(self):
        #Go one setp back
        self._head=self.tmphead
        self._body=self.tmpbody
        self._direct=self.tmpdirect

    def try_move(self):
        #Return possible move routes
        routes=[]
        moves=self.get_next(self._head,self._body[-1])
        if len(moves)==0:
            #Dead
            return []

        self.tmphead=self._head[:]
        self.tmpbody=self._body[:]
        self.tmpdirect=self._direct
        for i in moves:
            self.direct=move_method(i,self._head)
            self.run()
            if self._judge() is True:
                routes.append(self.direct)
            self.last_move()
        
        log("routes :  %s"%unicode(routes))
        return routes
                
        

    #Always return operation list
    def route(self):

        tree={}
        ops=[]


        r'''
        If length of ops is not 0 , virtual snake is already gone to food
        '''
        ops=self.__to_food()
        
        tofood=False
        
        operations=list()
        
        if len(ops)!=0:
            tofood=True
            #Moved
            if len(self._body)==0:
                return ops
            log("body tree\n %s\n"% unicode(self._body[0]))
            tree=self.BFS_tree([self._body[0]])
            log("body bfs_tree: %s"%unicode(tree))
            if len(tree)!=0:
                return ops
            else:
                operations.append(ops)
                log("virtual snake  head:%s,body%s"%(unicode(self._head),unicode(self._body)))
                #No way to tail, back to origin
                self.__reset()
                log("virtual snake  head:%s,body%s"%(unicode(self._head),unicode(self._body)))
                for i in xrange(5):
                    #try some times
                    ops=self.__to_food()
                    if ops in operations:
                        self.__reset()
                        break
                    tree=self.BFS_tree([self._body[0]])
                    if len(tree)!=0:
                        return ops
                    else: 
                        operations.append(ops)
                        self.__reset()
                    

        r'''
        Now back at origin place
        And cannot run for food directly
        '''
            
        tree=self.BFS_tree([self._body[0]])
        if len(tree)==0:
            r'''
            No food and no tail !! no !!
            '''
            moves=self.try_move()
            if len(moves)==0:
                log("no move")
                return []
            #TODO
            random.shuffle(moves)
            return [moves[0]]
            
        else:
            r'''
            Move one step to tail
            '''
            ops=self.tree2direct([self._body[0]],tree)
            log("step to tail")
            if len(ops)!=0:
                return [ops[-1]]
            else:
                log("Unexpected error")
            
                    
        return []
                
            
        
            

        



class Snake(BaseSnake):


    _head=tuple()
    _body=list()

    def __init__(self,x,y,body):
        BaseSnake.__init__(self)
        self._head=(x,y)
        self.BODY=body

 
    def run(self):
        self._move()
        if self._judge() is True:
            self.__frame()
        else:
            #game over
            pass
            #import pdb;pdb.set_trace()
            #curses.endwin()

    r'''
    def dump(self):
        print self._head
        print self._body
    r'''


    def _judge(self):
        if not valid_pos(self._head):
            return False
        if self._head in self._body:
            #import pdb;pdb.set_trace()
            return False
        if self._head in FOOD_P:
            self._eat=True
            remove_food(self._head)
        return True

    def __frame(self):
        SCR.clear()
        make_border()
        for i in self._body:
            SCR.addch(i[1],i[0],self.BODY)
        SCR.addch(self._head[1],self._head[0],HEAD_MAP.get(self._direct,'+'))
        for i in FOOD_P:
            try:
                SCR.addch(i[1],i[0],'$')
            except:
                import pdb;pdb.set_trace()
            
            
        SCR.refresh()

        LOG.clear()
        LOG.addstr(0,0,"head: (%d,%d)"%self._head)
        LOG.refresh()

        time.sleep(GAP)

    def set_direct_by_key(self,key):
        if k in DIRECT_MAP:
            direct=DIRECT_MAP.get(k) 
            if len(self._body)==0:
                #can turn every direction
                self._direct=direct
                return True
            if self._direct==1 and direct ==2:
                return False
            if self._direct==2 and direct ==1:
                return False
            if self._direct==3 and direct ==4:
                return False
            if self._direct==4 and direct ==3:
                return False
            
            self._direct=direct

        
    def route(self):
        #thei=0
        while 1:
            ops=[]
            vs=VirtualSnake(self._head,self._body)
            ops=vs.route()
            del vs
            if len(ops)==0:
                return
            log("head: %s\n body: %s \n food: %s \nops  %s \n length:%s\n"%(unicode(self._head),unicode(self._body),unicode(FOOD_P),unicode(ops),unicode(len(self._body))))

            for i in ops[::-1]:
                self.set_direct(i)
                self.run()



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



for i in range(FOOD_NUM):
    create_food()
#create_food()
s.route()
#s.run()
k=SCR.getch()
while k!=27:
    k=SCR.getch()
    s.set_direct_by_key(k)
    s.run()
    #SCR.addstr(0,0,"k=%d" % k)




curses.endwin()

