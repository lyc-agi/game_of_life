from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 初始化玩家和游戏数据
players = {}
grid_size = 10  # 游戏网格大小

def create_empty_grid():
    return [[0 for _ in range(grid_size)] for _ in range(grid_size)]

def count_neighbors(grid, x, y):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    count = 0
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            count += grid[nx][ny]
    return count

def run_generation(grid):
    new_grid = create_empty_grid()
    for x in range(grid_size):
        for y in range(grid_size):
            neighbors = count_neighbors(grid, x, y)
            if grid[x][y] == 1 and (neighbors == 2 or neighbors == 3):
                new_grid[x][y] = 1
            elif grid[x][y] == 0 and neighbors == 3:
                new_grid[x][y] = 1
    return new_grid

@app.route('/')
def index():
    return render_template('index.html', grid_size=grid_size)

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    if username in players:
        return jsonify({'error': 'Username already exists'}), 400
    players[username] = {
        'grid': create_empty_grid(),
        'score': 0
    }
    return jsonify({'message': 'User registered successfully'})

@app.route('/set_cells', methods=['POST'])
def set_cells():
    username = request.json.get('username')
    cells = request.json.get('cells')
    if username not in players:
        return jsonify({'error': 'User not found'}), 400
    if len(cells) > 10:
        return jsonify({'error': 'Too many cells'}), 400

    grid = create_empty_grid()
    for x, y in cells:
        grid[x][y] = 1
    players[username]['grid'] = grid
    return jsonify({'message': 'Cells set successfully'})

@app.route('/play', methods=['POST'])
def play():
    username = request.json.get('username')
    if username not in players:
        return jsonify({'error': 'User not found'}), 400

    cells = request.json.get('cells')
    if len(cells) > 10:
        return jsonify({'error': 'Too many cells'}), 400

    grid = create_empty_grid()
    for x, y in cells:
        grid[x][y] = 1
    players[username]['grid'] = grid

    for _ in range(3):
        grid = run_generation(grid)
    players[username]['score'] = sum(sum(row) for row in grid)
    return jsonify({'score': players[username]["score"]})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    scores = sorted(((username, data['score']) for username, data in players.items()), key=lambda x: x[1], reverse=True)
    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True)
