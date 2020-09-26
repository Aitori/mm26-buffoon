import logging

from mech.mania.starter_pack.domain.model.characters.character_decision import CharacterDecision
from mech.mania.starter_pack.domain.model.characters.position import Position
from mech.mania.starter_pack.domain.model.game_state import GameState
from mech.mania.starter_pack.domain.api import API

import heapq

class Node:
    def __init__(self, cost, prev, loc):
        self.cost = cost
        self.prev = prev
        self.coord = loc

class Strategy:
    def __init__(self, memory):
        # self.hard_code_state = [0, 0]
        self.memory = memory
        self.logger = logging.getLogger('strategy')
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level = logging.INFO)

        self.board_id = "buffoon"

    def make_decision(self, player_name: str, game_state: GameState) -> CharacterDecision:
        """
        Parameters:
        player_name (string): The name of your player
        game_state (GameState): The current game state
        """
        # game
        self.api = API(game_state, player_name)
        self.player = game_state.get_all_players()[player_name]
        self.pvpboard = game_state.get_pvp_board()
        self.board = game_state.get_board(self.board_id)

        # player
        self.curr_pos = self.player.get_position()
        self.weapon = self.player.get_weapon()

        # environment
        self.obstacles = self.get_obstacles(game_state)
        self.bad_monster_squares, self.weakest_monster  = self.get_monsters_and_weakest(game_state, self.board_id)
        self.weakest_monster_position = self.weakest_monster.get_position()
        self.logger.info('monster position:{},{}'.format(self.weakest_monster_position.x, self.weakest_monster_position.y))
        # last_action, type = self.memory.get_value("last_action", str)
        # if last_action is not None and last_action == "PICKUP":
        #     self.memory.set_value("last_action", "EQUIP")
        #     return CharacterDecision(
        #         decision_type="EQUIP",
        #         action_position=None,
        #         action_index=self.my_player.get_free_inventory_index()
        #     )

        tile_items = self.board.get_tile_at(self.curr_pos).items
        if len(tile_items) > 0:
            self.memory.set_value("last_action", "PICKUP")
            self.logger.info("picking up item: {}".format(tile_items))
            return CharacterDecision(
                decision_type="PICKUP",
                action_position=None,
                action_index=0
            )
        for d in [(1,0),(-1,0),(0,1),(0,-1)]:
            target_pos = Position.create(self.curr_pos.x + d[0], self.curr_pos.y + d[1], self.curr_pos.get_board_id())
            tile_items = self.board.get_tile_at(self.curr_pos).items
            if len(tile_items) > 0:
                self.memory.set_value("last_action", "MOVE")
                self.logger.info("moving to item")
                return CharacterDecision(
                    decision_type="MOVE",
                    action_position=target_pos,
                    action_index=0
                )
        # weapon = self.my_player.get_weapon()
        # enemies = self.api.find_enemies(self.curr_pos)
        # if enemies is None or len(enemies) > 0:
        #     self.memory.set_value("last_action", "MOVE")
        #     return CharacterDecision(
        #         decision_type="MOVE",
        #         action_position=self.my_player.get_spawn_point(),
        #         action_index=0
        #     )

        # enemy_pos = enemies[0].get_position()
        # if self.curr_pos.manhattan_distance(enemy_pos) <= weapon.get_range():
        #     self.memory.set_value("last_action", "ATTACK")
        #     return CharacterDecision(
        #         decision_type="ATTACK",
        #         action_position=enemy_pos,
        #         action_index=0
        #     )

        # self.logger.info("yes1")
        # self.memory.set_value("last_action", "MOVE")
        # decision = CharacterDecision(
        #     decision_type="MOVE",
        #     action_position=self.find_position_to_move(self.my_player, enemy_pos),
        #     action_index=0
        # )
        # self.logger.info("yes3")
        # return decision

        return self.hard_code_action()
        
        # ## Choose weakest monster
        # # Check if weakest monster is in attack range
        # if self.curr_pos.manhattan_distance(self.weakest_monster_position) <= self.weapon.get_range():
        #     return CharacterDecision(decision_type="ATTACK", action_position=self.weakest_monster_position, action_index=0)
        # ## Move to weakest monster!
        # self.logger.info("Chosen weakest monster: " + str(self.weakest_monster.get_name()) + " || location: (" + str(self.weakest_monster_position.x) + "," + str(self.weakest_monster_position.y) + ")")

        # positionToMove = self.zhou_astar_path_to_move(self.curr_pos, self.weakest_monster_position)

        # return CharacterDecision(decision_type="MOVE", action_position=positionToMove, action_index=0)

    # Find position to move using API
    def find_position_to_move(self, player: Position, destination: Position) -> Position:
        path = self.api.find_path(player.get_position(), destination)
        pos = None
        if len(path) < player.get_speed():
            pos = path[-1]
        else:
            pos = path[player.get_speed() - 1]
        return pos
    
    # hard code
    def hard_code_action(self):
        self.logger.info("Currently at:{},{}".format(self.curr_pos.x, self.curr_pos.y))
        target_pos = Position.create(self.curr_pos.x + 1, self.curr_pos.y, self.curr_pos.get_board_id())
        if abs(self.curr_pos.y - self.weakest_monster_position.y) + abs(self.curr_pos.x - self.weakest_monster_position.x) <= 1:
                self.logger.info("attacking")
                decision = CharacterDecision(
                    decision_type="ATTACK",
                    action_position=self.weakest_monster_position,
                    action_index=0
                )
                return decision
        # if abs(self.curr_pos.y - self.weakest_monster_position.y) >= 2:
        #     if self.curr_pos.y - self.weakest_monster_position.y > 0:
        #         target_pos = Position.create(self.curr_pos.x, self.curr_pos.y - 2, self.curr_pos.get_board_id())
        #     else:
        #         target_pos = Position.create(self.curr_pos.x, self.curr_pos.y + 2, self.curr_pos.get_board_id())
        # elif abs(self.curr_pos.x - self.weakest_monster_position.x) >= 2:
        #     if self.curr_pos.x - self.weakest_monster_position.x > 0:
        #         target_pos = Position.create(self.curr_pos.x - 2, self.curr_pos.y, self.curr_pos.get_board_id())
        #     else:
        #         target_pos = Position.create(self.curr_pos.x + 2, self.curr_pos.y, self.curr_pos.get_board_id())
        # else:
        if self.curr_pos.y > self.weakest_monster_position.y + 1:
            target_pos = Position.create(self.curr_pos.x, self.curr_pos.y - 1, self.curr_pos.get_board_id())
        elif self.curr_pos.y < self.weakest_monster_position.y:
            target_pos = Position.create(self.curr_pos.x, self.curr_pos.y + 1, self.curr_pos.get_board_id())
        elif self.curr_pos.x > self.weakest_monster_position.x:
            target_pos = Position.create(self.curr_pos.x - 1, self.curr_pos.y, self.curr_pos.get_board_id())
        elif self.curr_pos.x < self.weakest_monster_position.x:
            target_pos = Position.create(self.curr_pos.x - 1, self.curr_pos.y, self.curr_pos.get_board_id())
        self.logger.info("walk to:{},{}".format(target_pos.x, target_pos.y))
        decision = CharacterDecision(
            decision_type="MOVE",
            action_position=target_pos,
            action_index=0
        )
        return decision
        # if target_pos.y < 7:
        #     self.hard_code_state = [0, 0]
        #     self.logger.info("moving1")
        #     target_pos = Position.create(target_pos.x, target_pos.y + 1, target_pos.get_board_id())
        #     decision = CharacterDecision(
        #         decision_type="MOVE",
        #         action_position=target_pos,
        #         action_index=0
        #     )
        # elif self.hard_code_state[0] == 0 and self.hard_code_state[1] < 12:
        #     self.hard_code_state[1] += 1
        #     self.logger.info("attacking1")
        #     target_pos = Position.create(target_pos.x - 1, target_pos.y, target_pos.get_board_id())
        #     decision = CharacterDecision(
        #         decision_type="ATTACK",
        #         action_position=target_pos,
        #         action_index=0
        #     )
        # elif self.hard_code_state[0] == 0:
        #     self.hard_code_state[1] == 0
        #     self.hard_code_state[0] == 1

        # move to 2nd slime    
        # if self.hard_code_state[1] == 1 and target_pos.x < 6:
        #     self.logger.info("moving2")
        #     target_pos = Position.create(target_pos.x + 1, target_pos.y, target_pos.get_board_id())
        #     decision = CharacterDecision(
        #         decision_type="MOVE",
        #         action_position=target_pos,
        #         action_index=0
        #     )
        # elif self.hard_code_state[1] == 1 and self.hard_code_state[1] < 12:
        #     self.hard_code_state[1] += 1
        #     self.logger.info("attacking2")
        #     target_pos = Position.create(target_pos.x, target_pos.y - 1, target_pos.get_board_id())
        #     decision = CharacterDecision(
        #         decision_type="ATTACK",
        #         action_position=target_pos,
        #         action_index=0
        #     )
        # elif self.hard_code_state[1] == 1:
        #     self.hard_code_state[1] = 0
        #     self.hard_code_state[0] = 2
        
        # if self.hard_code_state[0] == 2:
        #     self.logger.info("moving3")
        #     target_pos = Position.create(target_pos.x - 1, target_pos.y, target_pos.get_board_id())
        #     decision = CharacterDecision(
        #         decision_type="MOVE",
        #         action_position=target_pos,
        #         action_index=0
        #     )

        # self.logger.info("target position:{},{}".format(target_pos.x, target_pos.y))
        
    # def bfs_path_to_move(self, target: Position)
    # Use astar to find path that doesn't aggro to target destination
    def zhou_astar_path_to_move(self, player: Position, destination: Position) -> Position:
        frontier = []
        path = []
        pp = player.get_position()
        heapq.heapify(frontier)
        start = Node(0, None, (pp.x, pp.y))
        heapq.heappush(frontier, (0, (pp.x, pp.y)))
        visited = set()
        visited.add((pp.x, pp.y))
        while frontier:
            curr = heapq.heappop(frontier)[1]
            if curr.coord == (destination.x, destination.y):
                while curr:
                    path.append(curr.coord)
                    curr = curr.prev
                path.reverse()
                break
            neighbors = self.getNeighbors(curr.coord[0], curr.coord[1])
            for n in neighbors:
                if n not in visited:
                    dist = abs(destination.y - n[1]) + abs(destination.x - n[0])
                    newNode = Node(curr.cost + 1, curr, n)
                    heapq.heappush(frontier, (newNode.cost + dist, newNode.coord))
                    visited.add(n)
        if len(path) < player.get_speed():
            pos = path[-1]
        else:
            pos = path[player.get_speed() - 1]
        return destination.create(pos[0], pos[1], self.board_id)

    # Find valid neighbors given coordinates
    def getNeighbors(self, getx, gety):
        neighbors = []
        for n in [(0,1), (0,-1), (-1,0), (1,0)]:
            coord = (getx + n[0], gety + n[1])
            if coord in self.obstacles or coord in self.bad_monster_squares:
                continue
            else:
                neighbors.append(coord)
        return neighbors

    # Get coords of obstacles
    def get_obstacles(self, game_state):
        grid = self.board.get_grid()
        obstacles = set()
        for x_idx in range(len(grid)):
            for y_idx in range(len(grid[x_idx])):
                tile = self.board.get_tile_at(Position.create(x_idx, y_idx, "buffoon"))
                if tile.get_type() == "VOID" or tile.get_type() == "IMPASSIBLE":
                    # print((x_idx,y_idx), tile.get_type())
                    obstacles.add((x_idx,y_idx))
        return obstacles

    # Get coords of monster aggro squares
    def get_monsters_and_weakest(self, game_state, board_id):
        monsters = game_state.get_monsters_on_board(board_id)
        bad_monster_squares = set()
        weakest = self.findWeakest(monsters)
        self.logger.info(str(len(monsters)))
        self.logger.info(str(monsters[0]))
        for monster in monsters:
            m_p = monster.get_position()
            m_a = monster.get_aggro_range() + 1
            # skip over weakest monster
            # if m_p == weakest.get_position():
            #     continue
            for x in range(0, m_a):
                for y in range(0, m_a - x):
                    bad_monster_squares.add((m_p.x + x, m_p.y + y))
                    bad_monster_squares.add((m_p.x + x, m_p.y - y))
                    bad_monster_squares.add((m_p.x - x, m_p.y + y))
                    bad_monster_squares.add((m_p.x - x, m_p.y - y))
        return bad_monster_squares, weakest

    # Find weakest monster
    def findWeakest(self, monsters):
        sortedM = sorted(monsters, key=lambda x:x.get_level())
        return sortedM[0]