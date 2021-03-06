#!/usr/bin/env python

'''*-----------------------------------------------------------------------*---
                                                        Author: Jason Ma
                                                        Date  : Jun 14 2016
    File Name  : sonarSim1_4.py
    Description: Places several objects relative to an emitter, then attempts
                 to locate them given processed times received in each 
                 receiver.
---*-----------------------------------------------------------------------*'''

#from __future__ import print_function
#from __future__ import division
import numpy as np
import time
from math import pow

#------------------------------------------------------------------------------
#[RUN VARS]--------------------------------------------------------------------
#------------------------------------------------------------------------------
#TODO new, needs comments
'''
f = open('objects', 'r')
count = 0
for line in f:
  count += 1
'''

#NUM_OBJECTS   = count      #num of objects
NUM_OBJECTS   = 8          #num of objects
SENS_NUM      = 4          #num of sensors
SENS_SAMPLE   = 200000     #sensor sample rate

TOL_DIST      = 3          #ellipse-circle intersection tolerance
TOL_OBJ       = 0.25       #multiple object detection tolerance
SPEED_WAVE    = 1482       #speed of sound in water
EXTRA_FACTOR  = 2          #allocate space in case extra objects are found
sensArr       = np.zeros((SENS_NUM, 3 + NUM_OBJECTS))
objs          = np.zeros((NUM_OBJECTS * EXTRA_FACTOR, 3))

#TODO new, needs comments
'''
for obj in range(0, NUM_OBJECTS):
  location = [float(f) for f in split(f.readline())]
  objs[obj][0] = 
  objs[obj][1] = 
  objs[obj][2] = 

f.close()
'''

  #sensArr[rcvr][0]  -> receiver x
  #sensArr[rcvr][1]  -> receiver y
  #sensArr[rcvr][2]  -> receiver z
  #sensArr[rcvr][3+] -> object times

sensArr[0][0] = 0
sensArr[0][1] = 0
sensArr[0][2] = 0

sensArr[1][0] = -0.15
sensArr[1][1] = 0
sensArr[1][2] = 0

sensArr[2][0] = .25
sensArr[2][1] = 0
sensArr[2][2] = 0

sensArr[3][0] = 0
sensArr[3][1] = 0
sensArr[3][2] = .20


  #objs[object][0] -> object x
  #objs[object][1] -> object y
  #objs[object][2] -> object z

objs[0][0]    = 33
objs[0][1]    = 36
objs[0][2]    = 27

objs[1][0]    = -35
objs[1][1]    = 43
objs[1][2]    = -15

objs[2][0]    = 36
objs[2][1]    = 42
objs[2][2]    = -1

objs[3][0]    = -29
objs[3][1]    = 12
objs[3][2]    = -23

objs[4][0]    = 40
objs[4][1]    = 9
objs[4][2]    = 13

objs[5][0]    = -24
objs[5][1]    = 40
objs[5][2]    = -24

objs[6][0]    = 22
objs[6][1]    = 36
objs[6][2]    = -39

objs[7][0]    = 18
objs[7][1]    = 17
objs[7][2]    = -21


'''
objs[0][0]    = 5
objs[0][1]    = 3
objs[0][2]    = 2

objs[1][0]    = -5
objs[1][1]    = 3
objs[1][2]    = -2
'''
'''
objs[0][0]    = 1
objs[0][1]    = 1
objs[0][2]    = 1

objs[1][0]    = -1
objs[1][1]    = 1
objs[1][2]    = 1

objs[2][0]    = 0
objs[2][1]    = 1
objs[2][2]    = 1

objs[3][0]    = 0
objs[3][1]    = 3
objs[3][2]    = -3

objs[4][0]    = 5
objs[4][1]    = 3
objs[4][2]    = 2

objs[5][0]    = -5
objs[5][1]    = 3
objs[5][2]    = -2

objs[6][0]    = 0
objs[6][1]    = 10
objs[6][2]    = 10

objs[7][0]    = 5
objs[7][1]    = 10
objs[7][2]    = 10

objs[8][0]    = -5
objs[8][1]    = 10
objs[8][2]    = 10

objs[9][0]    = 15
objs[9][1]    = 15
objs[9][2]    = 15

objs[10][0]   = -20
objs[10][1]   = 20
objs[10][2]   = 50

objs[11][0]   = 0
objs[11][1]   = 25
objs[11][2]   = 50
'''
#DEBUG-------------------------------------------------------------------------
INTER_ELL_DEBUG = 1
CALC_TIME_DEBUG = 1

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

'''isInRange-------------------------------------------------------------------
Checks whether a value is in a given range (inclusive on both bounds)

lower    - lower bound of range
upper    - upper bound of range
value    - value to check
[return] - 1 if in range
           0 if not in range
----------------------------------------------------------------------------'''
def isInRange(lower, upper, value):
  if value >= lower and value <= upper:
    return 1
  return 0

'''CEIntersect-----------------------------------------------------------------
Calculates X/Z intersect coordinates

a        - variable
b        - variable
[return] - 2 element array containing possible X/Z locs
----------------------------------------------------------------------------'''
def CEIntersect(a, b, c):
  intersects = np.zeros((2))
  d = pow(a, 2) * c / b

  if d < 0:
    return intersects

  d = b * pow(d, 1/2)
  intersects[0] = (pow(a, 3) - d - a * b) / pow(a, 2)
  intersects[1] = (pow(a, 3) + d - a * b) / pow(a, 2)
  return intersects

'''resolveTArray---------------------------------------------------------------
Calculates object location in 3D using 4 receiver times.

time1    - receiver 1 time
time2    - receiver 2 time
time3    - receiver 3 time
time4    - receiver 4 time
tol      - tolerance for variance in x
[return] - array with 3 elements containing x, y, and z coordinate of object
           will return 0 0 if finds nothing
----------------------------------------------------------------------------'''
def resolveTArray(time1, time2, time3, time4, tol, debug):
  #                  r3
  #                  |
  #             r1---E---r2
  #draw ellipses for r1, r2, and r3 of form: (x+a)^2 / b^2 + y^2 / c^2 = 1
  #draw circle for E
  
  A = 0
  B = 1
  C = 2

  rcvr          = np.zeros((3, 2))
  circY         = np.zeros((2, 2))
  ySqr          = np.zeros((3, 2))
  intersects    = np.zeros((2))
  tempIntersect = np.zeros((6, 2))
  ei            = np.zeros((3, 3))
  result        = np.zeros((3))  
  
  #emitter radius squared
  r2 = pow(time1 * SPEED_WAVE / 2, 2)

  rcvr[0][0] = sensArr[1][0]
  rcvr[1][0] = sensArr[2][0]
  rcvr[2][0] = sensArr[3][2]

  rcvr[0][1] = time2
  rcvr[1][1] = time3
  rcvr[2][1] = time4

  for ellipse in range(0, 3):
    #calculate x locs for EOE EO1
    ei[ellipse][A] = rcvr[ellipse][0] / 2
    ei[ellipse][B] = pow(rcvr[ellipse][1] * SPEED_WAVE / 2, 2)
    ei[ellipse][C] = ei[ellipse][B] - pow(ei[ellipse][A], 2)

    #calculate x locs of intersections
    intersects = CEIntersect(ei[ellipse][A], ei[ellipse][B], r2)
    tempIntersect[ellipse * 2][0] = intersects[0]
    tempIntersect[ellipse * 2 + 1][0] = intersects[1]

    #calculate y^2 for any found xs
    for i in range(0, 2):
      ySqr[ellipse][i % 2] = r2 - pow(tempIntersect[ellipse * 2 + i][0], 2)

      #check for invalid x or y locations
      if (tempIntersect[ellipse * 2 + i][0] != 0) and (ySqr[ellipse][i % 2] >= 0):
        tempIntersect[ellipse * 2 + i][1] = pow(ySqr[ellipse][i % 2], 1/2)

    if ellipse == 1:
      found = 0
      #try all 4 possible intersection points with tolerance against 3rd ellipse
      for i in range(0, 2):
        for j in range(2, 4):
          if tempIntersect[i][0] != 0:
            if isInRange(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                         tempIntersect[j][0]):
              found = 1
              result[0] = tempIntersect[i][0]
              result[1] = tempIntersect[i][1]
      
      if found == 0:
        break
    elif ellipse == 2:
      #circle circle intersections in 3D space
      for i in range(4, 6):
        if(tempIntersect[i][1] != 0):
          circY[i % 2][0] = pow(result[1], 2) - pow(tempIntersect[i][0], 2)
          circY[i % 2][1] = pow(tempIntersect[i][1], 2) - pow(result[0], 2)
  
          if circY[i % 2][0] < 0 or circY[i % 2][1] < 0:
            continue

          circY[i % 2][0] = pow(circY[i % 2][0], 1/2)
          circY[i % 2][1] = pow(circY[i % 2][1], 1/2)

          if(isInRange(circY[i % 2][1] - tol, circY[i % 2][1] + tol, circY[i % 2][0])):
            result[1] = (circY[i % 2][0] + circY[i % 2][1]) / 2
            result[2] = tempIntersect[i][0]
 
  #DEBUG
  if debug:
    print('+=[DEBUG]===============================+======================================+')
    print('| resolveTArray      sonarSim 1.4       ', end = '')
    print('| Data: {0:7.5f} {1:7.5f} {2:7.5f} {3:7.5f}\t|'.format(time1, 
                                                                  time2, 
                                                                  time3, 
                                                                  time4))
    for i in range(0, 3):
      print('+-[Part{} EOE EO{}]-----------------------+--------------------------------------+'.format(i, i + 1))
      print('|  ABC: {0:9.3f} {1:9.3f} {2:9.3f}\t|'.format(ei[i][A], 
                                                          ei[i][B], 
                                                          ei[i][C]), 
                                                  end = '')
      print(' XLocs: {0:9.2f} {1:9.2f}\t\t|'.format(tempIntersect[i * 2][0], 
                                                  tempIntersect[i * 2 + 1][0]))
      for j in range(i * 2, (i + 1) * 2):
        if tempIntersect[j][0] == 0:
          print('| - X{}: no solution\t\t\t|\t\t\t\t\t|'.format(j + 1))
        elif tempIntersect[j][1] == 0:
          print('| - Y{0:}: undef sqrt({1:18.3f})\t|\t\t\t\t\t|'.format(j + 1,
                                                               ySqr[0][j % 2]))
        else:
          print('| + X{0:}: {1:8.3f}\t\t\t| Y{0:}: {2:8.3f}\t\t\t\t|'.format(j + 1,
                                                          tempIntersect[j][0], 
                                                          tempIntersect[j][1]))
    print('+---------------------------------------+--------------------------------------+'.format(i, i + 1))
    if found:
      print('| +  X: {0:10.3f} Y: {1:10.3f}\t\t\t\t\t\t\t|'.format(result[0], 
                                                               result[1]))
      for i in range(0, 2):
        if circY[i][0] < 0 or circY[i][1] < 0:
          print('| - invalid Y1 or Y2\t\t\t\t\t\t\t\t|')
        elif circY[i][0] == 0 and circY[i][1] == 0:
          print('| - no Y\t\t\t\t\t\t\t\t\t|')
        elif result[2] != 0:
          print('| + Y1: {0:10.3f} Y2: {1:10.3f}\t> X: {2:8.3f} Y: {3:8.3f} Z:{4:8.3f}\t|'.format(
                                                                   circY[i][0],
                                                                   circY[i][1],
                                                                   result[0],
                                                                   result[1],
                                                                   result[2]))
        else:
          print('| - Y1: {0:10.3f} Y2: {1:10.3f}\t\t\t\t\t\t|'.format(circY[i][0],
                                                                  circY[i][1]))
    print('+=======================================+======================================+\n')
  
  return result

'''calcTime--------------------------------------------------------------------
Calculates processed time for given positions of object and receiver

xObj     - x displacement of object from emitter
yObj     - y displacement of object from emitter
rcvrX    - x displacement of receiver from emitter
rcvrY    - y displacement of receiver from emitter
exact    - whether to return exact or processed time
debug    - whether to print debug messages
[return] - time processed by receiver given the sample rate and speed of sound
----------------------------------------------------------------------------'''
def calcTime(xObj, yObj, zObj, xRcvr, yRcvr, zRcvr, exact, debug):
  distEmitterObj  = pow(pow(xObj, 2) + 
                        pow(yObj, 2) + 
                        pow(zObj, 2), 1/2)
  distObjReceiver = pow(pow(xObj - xRcvr, 2) + 
                        pow(yObj - yRcvr, 2) +
                        pow(zObj - zRcvr, 2), 1/2)
  totalDist = distEmitterObj + distObjReceiver
  totalTime = totalDist / SPEED_WAVE

  
  if debug:
    print('DEBUG - CT -{0:4.2f} {1:4.2f} {2:4.2f} {3:4.2f} {4:4.2f} {5:4.2f} {6:7.4f} {7:7.4f} {8:7.4f} {9:7.4f}'.format(
          xObj, yObj, zObj, xRcvr, yRcvr, zRcvr, 
          distEmitterObj, distObjReceiver, totalDist, totalTime))
  if(exact):
    return totalTime
  else:
    return totalTime - totalTime % (1 / SENS_SAMPLE) + (1 / SENS_SAMPLE)

'''Driver----------------------------------------------------------------------
Initializes time table, object times, and prints time table through delegation
----------------------------------------------------------------------------'''
def driver():
  start = time.time() * 1000

  #initialize objs array with times
  for obj in range(0, NUM_OBJECTS):
    for rcvr in range(0, SENS_NUM):
      sensArr[rcvr][3 + obj] = calcTime(objs[obj][0], objs[obj][1], 
                                        objs[obj][2], sensArr[rcvr][0], 
                                        sensArr[rcvr][1], sensArr[rcvr][2], 
                                        0, CALC_TIME_DEBUG)

  #clear file, all subsequent writes append to this file
  #file = open('timeTable', 'w')
  #file.write('')

  #print time table with all possible locs of objects
  #printPossibleLocs(TOLERANCE)
  '''
  #single object ellipse intersection detection
  for obj1 in range(0, NUM_OBJECTS):
    intersectEllipse(objs[obj1][2], objs[obj1][3], objs[obj1][4], TOL_DIST)
  '''
  #multiple object ellipse intersection detection
  i = 0
  locs = np.zeros((NUM_OBJECTS * EXTRA_FACTOR, 3))
  for obj1 in range(0, NUM_OBJECTS):
    for obj2 in range(0, NUM_OBJECTS):
      for obj3 in range(0, NUM_OBJECTS):
        for obj4 in range(0, NUM_OBJECTS):
          if(sensArr[0][3 + obj1] == 0 or sensArr[1][3 + obj2] == 0 or 
             sensArr[2][3 + obj3] == 0 or sensArr[3][3 + obj4] == 0):
            continue
          result = resolveTArray(sensArr[0][3 + obj1], sensArr[1][3 + obj2],
                                 sensArr[2][3 + obj3], sensArr[3][3 + obj4],
                                 TOL_DIST, INTER_ELL_DEBUG)
          if(result[2] != 0):
            dup = 0
            for j in range(0, i):
              if(isInRange(locs[j][0] - TOL_OBJ, locs[j][0] + TOL_OBJ, result[0]) and
                 isInRange(locs[j][1] - TOL_OBJ, locs[j][1] + TOL_OBJ, result[1]) and
                 isInRange(locs[j][2] - TOL_OBJ, locs[j][2] + TOL_OBJ, result[2])):
                dup = 1
            if dup == 0:
              for k in range(0, 3):
                locs[i][k] = result[k]
              i = i + 1
              sensArr[0][3 + obj1] = 0
              sensArr[1][3 + obj2] = 0
              sensArr[2][3 + obj3] = 0
              sensArr[3][3 + obj4] = 0

  end = time.time() * 1000
  print('Time: ', end - start, 'ms')
  print('      +===================================================+')
  print('      |  E: {0:5} {1:5} {2:5}   | R1: {3:5} {4:5} {5:5}   |'.format(
                                                           sensArr[0][0],
                                                           sensArr[0][1],
                                                           sensArr[0][2],
                                                           sensArr[1][0],
                                                           sensArr[1][1],
                                                           sensArr[1][2]))
  print('      | R2: {0:5} {1:5} {2:5}   | R3: {3:5} {4:5} {5:5}   |'.format(
                                                           sensArr[2][0],
                                                           sensArr[2][1],
                                                           sensArr[2][2],
                                                           sensArr[3][0],
                                                           sensArr[3][1],
                                                           sensArr[3][2]))

  print('      +=========================+=========================+')
  print('      |  In no particular Order:                          |')
  print('      +-------------------------+-------------------------+')
  print('      |  Found Locs             |  Actual Locs            |')  
  print('      +-------------------------+-------------------------+')
  print('      |  X       Y       Z      |  X       Y       Z      |')  
  print('      +=========================+=========================+')
  for i in range(0, NUM_OBJECTS * EXTRA_FACTOR):
    print('   {} '.format(repr(i + 1).rjust(2)), end = '|\t')
    if(locs[i][2] == 0):
      print('\t\t\t|', end = '')
    else:
      print('{0:7.3f} {1:7.3f} {2:7.3f}'.format(locs[i][0], 
                                                locs[i][1],
                                                locs[i][2]),
                                        end = '\t|')
    if(objs[i][0] == 0) and objs[i][1] == 0 and objs[i][2] == 0:
      print('\t\t\t  |')
    else:
      print(' {0:7.3f} {1:7.3f} {2:7.3f} |'.format(objs[i][0],
                                                   objs[i][1],
                                                   objs[i][2]))
  print('      +-------------------------+-------------------------+')  

driver()
