#!/usr/bin/env python
# coding: utf-8

# ### Python Stack Frames and Tail-Call Optimization

# #### Reza Bagheri

# In[1]:


import inspect
import dis
import sys
import timeit
from tailrec import tail_recursion


# In[2]:


inspect.stack()[0][0]


# In[3]:


inspect.currentframe()


# In[4]:


# Listing 2
a = 1
print(inspect.stack()[0], "\n")
def f(x):
    b=2
    print(inspect.stack()[0:2], "\n")
    return x+b
y = f(a)
print(inspect.stack(3)[0])
print(y)


# In[5]:


# Listing 3
a = 1
def f(x):
    b=2
    print(inspect.currentframe().f_code, "\n")
    print(inspect.currentframe().f_back, "\n")
    print(inspect.currentframe().f_locals)
    return x+b
y = f(a)


# In[6]:


def print_frames(frame_list):
    module_frame_index = [i for i, f in enumerate(frame_list) if f.function == '<module>'][0]
    for i in range(module_frame_index):
        d = frame_list[i][0].f_locals
        local_vars = {x: d[x] for x in d}
        print("  [Frame {} '{}': {}]".format(module_frame_index - i, frame_list[i].function, local_vars))
    print("  [Frame '<module>']\n")


# In[7]:


# Listing 4
a = 1
def f(x):
    b=2
    print_frames(inspect.stack())
    return b*x
def g(x):
    return 2*f(x)
y = g(a)


# In[8]:


# Listing 5
def f(x):
    def g(y):
        def h(z):
            print_frames(inspect.stack())
            return x+z
        print_frames(inspect.stack())
        return h
    print_frames(inspect.stack())
    return g


# In[9]:


f(1)(2)(3)


# In[10]:


# Listing 6
import sys
a = 1
def f(x):
    b=2
    print(sys._getframe().f_code, "\n")
    print(sys._getframe().f_back, "\n")
    print(sys._getframe().f_locals)
    return x+b
y = f(a)


# In[11]:


# Listing 7
def fact(n):
    if n==0:
        return 1
    else:
        return n*fact(n-1)


# In[12]:


# Listing 8
def fact(n):
    if n==0:
        print("fact({}) called:".format(n))
        print_frames(inspect.stack())
        print("fact({}) returned {}".format(n, 1))
        return 1
    else:
        print("fact({}) called:".format(n))
        print_frames(inspect.stack())
        result = n*fact(n-1)
        print_frames(inspect.stack())
        print("fact({}) returned {}".format(n, result))
        return result


# In[13]:


fact(3)


# In[14]:


# This will not run:
def fact(n):
    if n==0:
        return 1
    else:
        return n*fact(n-1)
print(fact(3000))


# #### Tail recursion

# In[15]:


# Listing 10
def fact1(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact1(n-1, n*acc) 
fact1(4, 1)


# In[16]:


# Listing 11
def fact1(n, acc=1):
    if n == 0:
        print("fact1({},{}) called:".format(n, acc))
        print_frames(inspect.stack())
        print("fact1({0},{1}) returned {1}".format(n, acc))
        return acc
    else:
        print("fact1({},{}) called:".format(n, acc))
        print_frames(inspect.stack())
        result = fact1(n-1, n*acc) 
        print_frames(inspect.stack())
        print("fact1({},{}) returned {}".format(n, acc, result))
        return result


# In[17]:


fact1(3,1)


# #### Tail-call optimization

# In[18]:


# Listing 13
def fact2(n, acc=1):
    while True:
        if n == 0:
            return acc
        else:
            acc = n * acc
            n = n - 1
print(fact(4))


# #### Tail-call optimization using stack frames

# In[19]:


# Listing 14
def tail_rec(func):
    rec_flag = False
    targs = []
    tkwargs = []
    def helper(*args, **kwargs):
        nonlocal rec_flag
        nonlocal targs
        nonlocal tkwargs 
        f = inspect.currentframe()
        
        if  f.f_code == f.f_back.f_back.f_code:
            rec_flag = True
            targs = args
            tkwargs = kwargs
            return 
        else:           
            while True:
                try:
                    result = func(*args, **kwargs)
                except TypeError as e:
                    raise Exception("It is possible that the decorated function is not tail recursive")
                if rec_flag:
                    rec_flag = False
                    args = targs
                    kwargs = tkwargs
                else:
                    return result 
    return helper


# In[20]:


@tail_rec
def fact1(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact1(n-1, n*acc)
        
fact1(4)


# In[21]:


# You can have you can have some statements after the recursive call
# as long as there is no computation on the returned value of the recursive call.
@tail_rec
def fact2(n, acc=1):
    if n == 0:
        return acc
    else:
        result = fact2(n-1, n*acc)
        return result
fact1(4)


# In[22]:


# This does not work
@tail_rec
def fact(n):
    if n==0:
        return 1
    else:
        return n*fact(n-1)
print(fact(4))


# #### Tail-call optimization using bytecode injection

# tail_resursion decorator has been defiend in tailrec module

# In[23]:


def fact1(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact1(n-1, n*acc)
dis.dis(fact1)


# In[24]:


@tail_recursion
def fact1(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact1(n-1, n*acc)
        
fact1(4)


# In[25]:


# This does not work:
@tail_recursion
def fact(n):
    if n==0:
        return 1
    else:
        return n*fact(n-1)
print(fact(3))


# In[26]:


# Here no instructions are allowed after the recursive call
# So this does not work too
@tail_recursion
def fact2(n, acc=1):
    if n == 0:
        return acc
    else:
        result = fact2(n-1, n*acc)
        return result
fact1(4)


# In[27]:


@tail_rec
def fact_1(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact_1(n-1, n*acc)
    
@tail_recursion
def fact_2(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact_2(n-1, n*acc)
        

def s1():
    return fact_1(15)

def s2():
    return fact_2(15)


# In[30]:


t1 = timeit.timeit(s1, number=100000)
t2 = timeit.timeit(s2, number=100000)
print("Running time (tail-call optimization using stack frames)=", round(t1, 3))
print("Running time (tail-call optimization using bytecode injection)=", round(t2, 3))


# In[ ]:




