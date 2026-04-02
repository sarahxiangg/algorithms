import sys
from collections import deque
import heapq


#bec IDS BEAM UCS

#sarah bfs, greedy, a*
class Node:
    def __init__(self, state, parent=None, g=0, depth=0):
        self.state = state          # (x, y)
        self.parent = parent
        self.g = g                  # path cost so far
        self.depth = depth          # depth for IDS


def parse_map(filename):
    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip() != '']

    dims = lines[0]
    start_line = lines[1]
    grid_lines = lines[2:]

    x_dim, y_dim = map(int, dims.split('x'))
    start_x, start_y = map(int, start_line.split('-'))

    grid = [list(row) for row in grid_lines]

    treasures = []
    portal_positions = {}

    for y in range(y_dim):
        for x in range(x_dim):
            tile = grid[y][x]
            if tile == 'X':
                treasures.append((x, y))
            if tile.isdigit():
                portal_positions[tile] = (x, y)

    portal_pairs = {}
    for symbol, coord in portal_positions.items():
        num = int(symbol)
        if num % 2 == 1:
            exit_symbol = str(num + 1)
            if exit_symbol in portal_positions:
                portal_pairs[coord] = portal_positions[exit_symbol]

    return {
        'x_dim': x_dim,
        'y_dim': y_dim,
        'start': (start_x, start_y),
        'grid': grid,
        'treasures': treasures,
        'portal_pairs': portal_pairs
    }


def in_bounds(x, y, data):
    return 0 <= x < data['x_dim'] and 0 <= y < data['y_dim']


def get_tile(state, data):
    x, y = state
    return data['grid'][y][x]


def is_goal(state, data):
    return get_tile(state, data) == 'X'


def is_wall(state, data):
    return get_tile(state, data) == 'W'


def move_cost(state, data):
    tile = get_tile(state, data)
    if tile == 'M':
        return 2
    if tile == 'B':
        return 3
    return 1


def heuristic(state, data):
    tile = get_tile(state, data)

    if state in data['portal_pairs']:
        exit_state = data['portal_pairs'][state]
        return min(abs(exit_state[0] - tx) + abs(exit_state[1] - ty)
                   for tx, ty in data['treasures'])

    return min(abs(state[0] - tx) + abs(state[1] - ty)
               for tx, ty in data['treasures'])


def get_children(node, data):
    x, y = node.state

    # If standing on a portal entrance, next move must be teleport to exit
    if node.state in data['portal_pairs']:
        exit_state = data['portal_pairs'][node.state]
        return [Node(exit_state, node, node.g, node.depth + 1)]

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # LEFT, RIGHT, UP, DOWN
    children = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        next_state = (nx, ny)

        if not in_bounds(nx, ny, data):
            continue
        if is_wall(next_state, data):
            continue

        cost = move_cost(next_state, data)
        children.append(Node(next_state, node, node.g + cost, node.depth + 1))

    return children


def reconstruct_path(node):
    path = []
    while node is not None:
        path.append(node.state)
        node = node.parent
    path.reverse()
    return path


def format_expanded(expanded):
    return ''.join(f'({x}, {y})' for x, y in expanded)


def format_path(path):
    return '[' + ', '.join(f'({x}, {y})' for x, y in path) + ']'


def print_success(search_name, expanded, goal_node):
    print(f'{search_name} Search Initiated')
    print(f'Expanded: {format_expanded(expanded)}')
    path = reconstruct_path(goal_node)
    print(f'Path Found: {format_path(path)}')
    print(f'Taking this path will cost: {goal_node.g} Willpower')


def print_failure(search_name, expanded):
    print(f'{search_name} Search Initiated')
    print(f'Expanded: {format_expanded(expanded)}')
    print('NO PATH FOUND!')


def bfs(filename):
    data = parse_map(filename)
    start = Node(data['start'])

    fringe = deque([start])
    expanded_set = set()
    expanded_order = []

    while fringe:
        node = fringe.popleft()

        if node.state in expanded_set:
            continue

        expanded_set.add(node.state)
        expanded_order.append(node.state)

        if is_goal(node.state, data):
            print_success('BFS', expanded_order, node)
            return

        for child in get_children(node, data):
            fringe.append(child)

    print_failure('BFS', expanded_order)


def ucs(filename):

    data = parse_map(filename)
    start = Node(data['start'])
    counter = 0

    fringe = [start]
    expanded_set = set()
    expanded_order = []

    while fringe:
        best_index = 0
        for i in range(1, len(fringe)):
            a = fringe[i]
            b = fringe[best_index]

            if (a.g, a.state[0], a.state[1]) < (b.g, b.state[0], b.state[1]):
                best_index = i

        node = fringe.pop(best_index)

        if node.state in expanded_set:
            continue

        expanded_set.add(node.state)
        expanded_order.append(node.state)

        if is_goal(node.state, data):
            print_success('UCS', expanded_order, node)
            return

        for child in get_children(node, data):
            fringe.append(child)



    
    print_failure('UCS', expanded_order)    


def greedy(filename):
    data = parse_map(filename)

    expanded_order = []

    pass


def astar(filename):
    pass

def ids(filename, limit):
    data = parse_map(filename)
    expanded_order = []

    for depth_limit in range(limit + 1):
        start = Node(data['start'])
        stack = [(start, [start.state])]
        expanded_set = set()

        while stack:
            node, path = stack.pop()

            if node.state in expanded_set:
                continue

            expanded_set.add(node.state)
            expanded_order.append(node.state)

            if is_goal(node.state, data):
                print_success('IDS', expanded_order, node)
                return

            if node.depth == depth_limit:
                continue

            children = get_children(node, data)

            for child in reversed(children):
                if child.state not in path:
                    stack.append((child, path + [child.state]))

    print_failure('IDS', expanded_order)
    



def beam(filename, width):
    data = parse_map(filename)
    start = Node(data['start'])

    expanded_set = set()
    expanded_order = []

    beam_nodes = [start]

    while beam_nodes:
        best_current_h = min(
            heuristic(node.state, data) for node in beam_nodes
        )

        successors = []
        successor_states = set()

        for node in beam_nodes:
            if node.state in expanded_set:
                continue

            expanded_set.add(node.state)
            expanded_order.append(node.state)

            if is_goal(node.state, data):
                print_success('Beam', expanded_order, node)
                return

            for child in get_children(node, data):
                
                if child.state not in expanded_set and child.state not in successor_states:
                    successors.append(child)
                    successor_states.add(child.state)

        if not successors:
            break

        
        successors.sort(
            key=lambda n: (
                heuristic(n.state, data),
                n.state[0],
                n.state[1]
            )
        )

      
        next_beam = successors[:width]

        
        best_next_h = heuristic(next_beam[0].state, data)
        if best_next_h < best_current_h:
            beam_nodes = next_beam
        else:
            break

    print_failure('Beam', expanded_order)



def main(strategy, filename):
    if strategy == 'B':
        bfs(filename)
    elif strategy == 'U':
        ucs(filename)
    elif strategy == 'G':
        greedy(filename)
    elif strategy == 'A':
        astar(filename)
    elif strategy == 'I':
        if len(sys.argv) < 4:
            print('IDS requires a depth limit parameter.')
            return
        limit = int(sys.argv[3])
        ids(filename, limit)
    elif strategy == 'M':
        if len(sys.argv) < 4:
            print('Beam Search requires a beam width parameter.')
            return
        width = int(sys.argv[3])
        beam(filename, width)
    else:
        print('Invalid search strategy.')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        # You can modify these values to test your code
        strategy = 'B'
        filename = 'example1.txt'
    else:
        strategy = sys.argv[1]
        filename = sys.argv[2]

    main(strategy, filename)