import heapq
import math
from enum import Enum

class Occupant(Enum):
    UNKNOWN = -1
    EMPTY = 0
    OBSTACLE = 1
    REDFLAG = 2
    BLUEFLAG = 3
    ROVER = 4
    REDBUTTON = 5
    BLUEBUTTON = 6

class Node:
    def __init__(self, r, c):
      self.r = r
      self.c = c
      self.cost = float('inf')        # g cost (distance from start node)
      self.heuristic = 0              # h cost (distance from end node - for Dijsktra's algorithm, h = 0)
      self.f_score = float('inf')     # f = g + h
      self.parent = None
      self.occupant = Occupant.UNKNOWN
      self.occupant_ref = None        # Reference to the rover object in the cell
      self.visited = False

    def __lt__(self, other):
      return self.f_score < other.f_score
    
    def is_occupied(self):
      return self.occupant != Occupant.EMPTY

# Manhattan distance is the sum of the horizontal and vertical distances between two points
def manhattan_distance(start, end):
  return abs(start.r - end.r) + abs(start.c - end.c)

# Euclidean distance is the straight-line distance between two points
def euclidean_distance(start, end):
  return math.sqrt((start.r - end.r) ** 2 + (start.c - end.c) ** 2)

# Get the (non-obstacle) neighbors of a node
def get_neighbors(node, grid, obstacles):
  directions = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]  # 8-way connectivity
  neighbors = []
  for dr, dc in directions:
      nr, nc = node.r + dr, node.c + dc
      if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and (nr, nc) not in obstacles:
          neighbors.append(grid[nr][nc])
  return neighbors

# A* algorithm - used once the destination has been determined
def a_star(rows, cols, start, goal, obstacles):

  # Create a virtual grid of nodes to run the algorithm on (based on the rover's gridview and obstacles)
  grid = [[Node(r, c) for c in range(cols)] for r in range(rows)]
  startNode =  grid[start.r][start.c]
  endNode = grid[goal.r][goal.c]

  # Start the A* algorithm
  open_set = []
  heapq.heappush(open_set, startNode)
  startNode.cost = 0
  startNode.heuristic = euclidean_distance(startNode, endNode)
  startNode.f_score = startNode.heuristic

  while open_set:
      current = heapq.heappop(open_set)
      if current == endNode:
          path = []
          while current:
              path.append((current.r, current.c))
              current = current.parent
          return path[::-1]

      for neighbor in get_neighbors(current, grid, obstacles):
          if abs(current.r - neighbor.r) == 1 and abs(current.c - neighbor.c) == 1: 
            movement_cost = 1.414
          else:
            movement_cost = 1
          tentative_g_score = current.cost + movement_cost
          if tentative_g_score < neighbor.cost:
              neighbor.parent = current
              neighbor.cost = tentative_g_score
              neighbor.heuristic = euclidean_distance(neighbor, endNode)
              neighbor.f_score = neighbor.cost + neighbor.heuristic
              if neighbor not in open_set:
                  heapq.heappush(open_set, neighbor)

  return None  # Path not found

# For testing
if __name__ == "__main__":
  width, height = 10, 10
  obstacles = {(3, 3), (3, 4), (4, 3), (4, 4)}  # Example obstacles cells
  grid = [[Node(r, c) for c in range(width)] for r in range(height)]

  start = grid[0][0]
  goal = grid[9][9]

  path = a_star(start, goal, grid, obstacles)
  print("Path from start to goal:", path)