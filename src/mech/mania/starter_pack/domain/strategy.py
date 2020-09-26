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
        self.buffoon = 0
        self.memory = memory
        self.logger = logging.getLogger('strategy')
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level = logging.INFO)

    def make_decision(self, player_name: str, game_state: GameState) -> CharacterDecision:
        """
        Parameters:
        player_name (string): The name of your player
        game_state (GameState): The current game state
        """
        self.api = API(game_state, player_name)
        self.my_player = game_state.get_all_players()[player_name]
        self.board = game_state.get_pvp_board()
        self.curr_pos = self.my_player.get_position()
        self.monster_positions = game_state.get_monsters_on_board("buffoon")
        self.logger.info(str(game_state.get_monsters_on_board("buffoon")))

        # last_action, type = self.memory.get_value("last_action", str)
        # if last_action is not None and last_action == "PICKUP":
        #     self.memory.set_value("last_action", "EQUIP")
        #     return CharacterDecision(
        #         decision_type="EQUIP",
        #         action_position=None,
        #         action_index=self.my_player.get_free_inventory_index()
        #     )

        # tile_items = self.board.get_tile_at(self.curr_pos).items
        # if tile_items is not None or len(tile_items) > 0:
        #     self.memory.set_value("last_action", "PICKUP")
        #     return CharacterDecision(
        #         decision_type="PICKUP",
        #         action_position=None,
        #         action_index=0
        #     )

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
        #     action_position=move_down_position(),#find_position_to_move(self.my_player, enemy_pos),
        #     action_index=0
        # )
        # self.logger.info("yes3")
        # return decision

        target_pos: Position = self.curr_pos
        if target_pos.y == 12:
            self.logger.info("Attacking!")
            return CharacterDecision(
                decision_type="ATTACK",
                action_position=self.curr_pos,#self.monster_positions[0],
                action_index=0
            )
            # self.buffoon = 1
            # self.logger.info("On board " + str(target_pos.board_id) +" move to (" + str(target_pos.x) + ", " + str(target_pos.y) + ")")
            # decision = CharacterDecision(
            #     decision_type="MOVE",
            #     action_position=target_pos.create(target_pos.x, target_pos.y - 3, target_pos.get_board_id()),
            #     action_index=0
            # )
            
            # return decision
        # elif self.buffoon == 0:
        #     self.logger.info("On board " + str(target_pos.board_id) +" move to (" + str(target_pos.x) + ", " + str(target_pos.y) + ")")
        #     decision = CharacterDecision(
        #         decision_type="MOVE",
        #         action_position=target_pos.create(target_pos.x, target_pos.y + 3, target_pos.get_board_id()),
        #         action_index=0
        #     )
        #     self.logger.info("Moving!")
        #     return decision
        # else:
        #     pass


    # feel free to write as many helper functions as you need!
    def find_position_to_move(self, player: Position, destination: Position) -> Position:
        path = self.api.find_path(player.get_position(), destination)
        pos = None
        if len(path) < player.get_speed():
            pos = path[-1]
        else:
            pos = path[player.get_speed() - 1]
        return pos
    
    def move_down_position(self):
        target_pos = self.curr_pos
        target_pos.create(target_pos.x, target_pos.y, target_pos.get_board_id())
        self.logger.info("yes2")
        return target_pos

    def zhou_astar_path(self, player: Position, destination: Position) -> Position:
        frontier = []
        heapq.heapify(frontier)
        start = Node(0, None, (player.x, player.y))
        heapq.heappush(frontier, (0, (player.x, player.y)))
        visited = set()
        visited.add((player.x, player.y))
        while frontier:
            curr = heapq.heappop(frontier)[1]
            if curr.coord == (destination.x, destination.y):
                path = []
                while curr:
                    path.append(curr.coord)
                    curr = curr.prev
                path.reverse()
                return path
            neighbors = self.getNeighbors(curr.coord[0], curr.coord[1])
            for n in neighbors:
                if n not in visited:
                    dist = abs(destination.y - n[1]) + abs(destination.x - n[0])
                    newNode = Node(curr.cost + 1, curr, n)
                    heapq.heappush(frontier, (newNode.cost + dist, newNode.coord))
                    visited.add(n)
        return []

    def getNeighbors(self, getx, gety):
        neighbors = []
        for n in [(0,1), (0,-1), (-1,0), (1,0)]:
            coord = (getx + n[0], gety + n[1])
            if coord in self.obstacles or coord in self.bad_monster_squares:
                continue
            else:
                neighbors.append(coord)
        return neighbors

    def get_obstacles(self, game_state):
        grid = self.board.get_grid
        self.obstacles = set()
        for x_idx in range(len(grid)):
            for y_idx in range(len(grid[x_idx])):
                tile = self.board.get_tile_at(Position(x_idx, y_idx, "buffoon"))
                if tile.TileType == "VOID" or tile.TileType == "IMPASSIBLE":
                    print((x,y), tile.TileType)
                    self.obstacles.add((x,y))
        return self.obstacles:

    def get_monsters(self, gameState, board_id):
        monsters = game_state.get_monsters_on_board(board_id)
        self.bad_monster_squares = set()
        for monster in monsters:
            m_p = monster.position
            for direction in [(0,1), (0,-1), (-1,0), (1,0)]:
                for step in range(monster.aggro_range):
                    self.bad_monster_squares.add((direction[0] * step + monster.position.x , direction[1] * step + monster.position.y))
        return self.bad_monster_squares