import heapq
import math

class Node:
    def __init__(self, r, c):
      self.r = r
      self.c = c
      self.cost = float('inf')      # g cost (distance from start node)
      self.heuristic = 0            # h cost (distance from end node - for Dijsktra's algorithm, h = 0)
      self.f_score = float('inf')   # f = g + h
      self.parent = None
      self.occupant = None          # None = empty, 0 = start, 1 = end, 2 = obstacle, 3 = flag, 4 = rover

    def __lt__(self, other):
      return self.f_score < other.f_score

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

# A* algorithm
def a_star(start, goal, grid, obstacles):
  open_set = []
  heapq.heappush(open_set, start)
  start.cost = 0
  start.heuristic = euclidean_distance(start, goal)
  start.f_score = start.heuristic

  while open_set:
      current = heapq.heappop(open_set)
      if current == goal:
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
              neighbor.heuristic = euclidean_distance(neighbor, goal)
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