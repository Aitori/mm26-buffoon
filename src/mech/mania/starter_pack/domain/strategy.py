import logging

from mech.mania.starter_pack.domain.model.characters import character
from mech.mania.starter_pack.domain.model.characters.character_decision import CharacterDecision
from mech.mania.starter_pack.domain.model.characters.position import Position
from mech.mania.starter_pack.domain.model.game_state import GameState
from mech.mania.starter_pack.domain.api import API

import collections
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
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') 
        self.board_id = "buffoon"
        self.stats = collections.defaultdict(int)

    def make_decision(self, player_name: str, game_state: GameState) -> CharacterDecision:
        """
        Parameters:
        player_name (string): The name of your player
        game_state (GameState): The current game state
        """
        self.logger.info("==========================NEW TURN==========================")
        self.api = API(game_state, player_name)
        self.character = game_state.get_character(player_name)
        self.my_player = game_state.get_all_players()[player_name]
        #self.pvpboard = game_state.get_pvp_board()
        self.board = game_state.get_board(self.board_id)
        self.curr_pos = self.my_player.get_position()
        self.monsters = game_state.get_monsters_on_board(self.board_id)

        self.obstacles = self.get_obstacles(game_state)
        self.bad_monster_squares = self.get_monsters(game_state, self.board_id)
        # cycle through items
        items = self.my_player.get_inventory()
        self.logger.info("items: {}".format(items))
        cur_weapon = self.my_player.get_weapon
        self.logger.info('performing inventory check')
        try:
            if self.character.clothes is not None: 
                self.print_stats(self.character.clothes)
        except:
            self.logger.info("no clothes to print")
            pass
        try:
            if self.character.hat is not None: 
                self.print_stats(self.character.hat)
        except:
            self.logger.info("no hat to print")
            pass
        try:
            if self.character.weapon is not None: 
                self.print_stats(self.character.weapon)
        except:
            self.logger.info("no weapon to print")
            pass
        try:
            if self.character.shoes is not None: 
                self.print_stats(self.character.shoes)
        except:
            self.logger.info("no shoes to print")
            pass
        try:    
            if self.character.accessory is not None: 
                self.print_stats(self.character.accessory)
        except:
            self.logger.info("no accessory to print")
            pass
        for i, item in reversed(list(enumerate(items))):
            # self.logger.info('exp change: {}, {}'.format(item.get_flat_experience_change(), item.get_percent_experience_change()))
            # self.logger.info('atk change: {}, {}'.format(item.get_flat_attack_change(), item.get_percent_attack_change()))
            # if item.get_flat_attack_change() > cur_weapon.get_flat_attack_change():
            #     self.logger.info('equiping item')
            #     return CharacterDecision(
            #         decision_type="EQUIP",
            #         action_position=None,
            #         action_index=i
            #     )
            try:
                self.logger.info("grading index {} in the inventory".format(i))
                # self.logger.info(type(item))
                
                item_type = item.__class__.__name__
                # self.logger.info(item_type)

                if "Consumable" in item_type:
                    #idk do we equip the consumable before we fite the guy
                    #but also if its a health potion do it now
                    self.logger.info('index {} is a consumable, eating!'.format(i))
                    #actually drop consumables fuck em (no wee eat them right there)
                    return CharacterDecision(
                            decision_type="EQUIP",
                            action_position=None,
                            action_index=i
                        )
                    # continue
                self.logger.info(self.print_stats(item))
                stat_mod = item.get_stats()
                new_stats = 0
                try: new_stats += stat_mod.get_flat_speed_change() * 0
                except: new_stats += 0
                try: new_stats += stat_mod.get_percent_speed_change() * 0
                except: new_stats += 0
                try: new_stats += stat_mod.get_flat_health_change() * .1
                except: new_stats += 0
                try: new_stats += stat_mod.get_percent_health_change() * 30
                except: new_stats += 0
                try: new_stats += stat_mod.get_flat_experience_change() * 10
                except: new_stats += 0
                try: new_stats += stat_mod.get_percent_experience_change() * 200
                except: new_stats += 0
                try: new_stats += stat_mod.get_flat_attack_change() * 10
                except: new_stats += 0
                try: new_stats += stat_mod.get_percent_attack_change() * 70
                except: new_stats += 0
                try: new_stats += stat_mod.get_flat_defense_change() * 2
                except: new_stats += 0
                try: new_stats += stat_mod.get_percent_defense_change() * 30
                except: new_stats += 0
                try: new_stats += stat_mod.get_flat_regen_per_turn() * 0
                except: new_stats += 0
                self.logger.info("got stats for index {}".format(i))
                # new_stats = stat_mods.get_flat_speed_change() + stat_mods.get_percent_speed_change() + stat_mods.get_flat_health_change() + stat_mods.get_percent_health_change() + stat_mods.get_flat_defense_change() + stat_mods.get_flat_attack_change() + stat_mods.get_percent_attack_change()
                self.logger.info("stat check for index {} is {}".format(i, new_stats))
                for typ in ["Clothes", "Hat", "Shoes", "Weapon", "Accessory"]:

                    if typ in item_type:
                        self.logger.info('index {} is a {}'.format(i, typ))
                        current_stats = self.stats[typ]
                        self.logger.info('old stats: {} , new stats: {}'.format(current_stats, new_stats))
                        if new_stats > current_stats:
                            self.logger.info("equipping")
                            self.stats[typ] = new_stats
                            return CharacterDecision(
                                decision_type="EQUIP",
                                action_position=None,
                                action_index=i
                            )
                        else:
                            self.logger.info("this {} sucks, dropping it".format(typ))
                            return CharacterDecision(
                                decision_type="DROP",
                                action_position=None,
                                action_index=i
                            )
            except Exception as e:
                
                self.logger.error(e)
                return CharacterDecision(
                    decision_type="DROP",
                    action_position=None,
                    action_index=0
                )

        
        # item pick up
        tile_items = self.board.get_tile_at(self.curr_pos).items
        if len(tile_items) > 0:
            self.memory.set_value("last_action", "PICKUP")
            self.logger.info("picking up item: {}".format(tile_items))
            try:
                for i in range(len(tile_items)):
                    self.logger.info("grading new item index {}".format(i))
                    if "Consumable" in tile_items[i].__class__.__name__:
                        return CharacterDecision(
                            decision_type="PICKUP",
                            action_position=self.curr_pos,
                            action_index=i
                        )
                    stat_mods = tile_items[i].get_stats()
                    stat_sum = stat_mods.get_flat_speed_change() * 0 + stat_mods.get_percent_speed_change() * 0 + stat_mods.get_flat_health_change() * .1 + stat_mods.get_percent_health_change() * 30 + stat_mods.get_flat_defense_change() * 2 + stat_mods.get_flat_attack_change() * 10 + stat_mods.get_percent_attack_change() * 70 +stat_mods.get_percent_defense_change() * 30 + stat_mods.get_flat_regen_per_turn() * 0 + stat_mods.get_flat_experience_change() * 10 + stat_mods.get_percent_experience_change() * 200
                    self.logger.info("new item stat: " + str(stat_sum))
                    self.logger.info("curr stat item: " + str(self.stats[tile_items[i].__class__.__name__]))
                    if stat_sum > self.stats[tile_items[i].__class__.__name__]:
                        self.logger.info("picking up item at index {}".format(i))
                        return CharacterDecision(
                            decision_type="PICKUP",
                            action_position=self.curr_pos,
                            action_index=i
                        )
                    else:
                        self.logger.info("skipping index {}, shitty item".format(i))
            except Exception as e:
                self.logger.error(e)
                self.logger.info("picking up item at index 0")
                return CharacterDecision(
                    decision_type="PICKUP",
                    action_position=self.curr_pos,
                    action_index=i
                )
        for d in [(1,0),(-1,0),(0,1),(0,-1)]:
            target_pos = Position.create(self.curr_pos.x + d[0], self.curr_pos.y + d[1], self.curr_pos.get_board_id())
            tile_items = self.board.get_tile_at(target_pos).items
            if len(tile_items) > 0:
                for i in range(len(tile_items)):
                    self.logger.info("grading new item index {}".format(i))
                    if "Consumable" in tile_items[i].__class__.__name__:
                        self.memory.set_value("last_action", "MOVE")
                        self.logger.info("moving to item")
                        return CharacterDecision(
                            decision_type="MOVE",
                            action_position=target_pos,
                            action_index=0
                        )
                    stat_mods = tile_items[i].get_stats()
                    stat_sum = stat_mods.get_flat_speed_change() * 0 + stat_mods.get_percent_speed_change() * 0 + stat_mods.get_flat_health_change() * .1 + stat_mods.get_percent_health_change() * 30 + stat_mods.get_flat_defense_change() * 2 + stat_mods.get_flat_attack_change() * 10 + stat_mods.get_percent_attack_change() * 70 +stat_mods.get_percent_defense_change() * 30 + stat_mods.get_flat_regen_per_turn() * 0 + stat_mods.get_flat_experience_change() * 10 + stat_mods.get_percent_experience_change() * 200
                    self.logger.info("new item stat: " + str(stat_sum))
                    self.logger.info("curr stat item: " + str(self.stats[tile_items[i].__class__.__name__]))
                    if stat_sum > self.stats[tile_items[i].__class__.__name__]:
                        self.memory.set_value("last_action", "MOVE")
                        self.logger.info("moving to item")
                        return CharacterDecision(
                            decision_type="MOVE",
                            action_position=target_pos,
                            action_index=0
                        )
                    else:
                        self.logger.info("skipping index {}, shitty item".format(i))
        
        ## Choose weakest monster
        weakestMonster = self.findWeakest(self.monsters, self.curr_pos)
        weapon = self.my_player.get_weapon()
        ## Check if weakest monster is in attack range
        if self.curr_pos.manhattan_distance(weakestMonster.position) <= weapon.get_range():
            self.logger.info("Attacking monster: " + str(weakestMonster.get_name()) + " with health " + str(weakestMonster.get_current_health()) + "/" + str(weakestMonster.get_max_health()))
            return CharacterDecision(decision_type="ATTACK", action_position=weakestMonster.get_position(), action_index=0)
        ## Move to weakest monster!
        self.logger.info("Chosen weakest monster: " + str(weakestMonster.get_name()) + " || location: (" + str(weakestMonster.get_position().x) + "," + str(weakestMonster.get_position().y) + ")")

        positionToMove = self.zhou_astar_path_to_move(self.my_player, weakestMonster.get_position())
        # hard code walk back
        if positionToMove[0] >= 6:
            positionToMove[0] = 4
        positionObjectToMove = self.curr_pos
        newPos = positionObjectToMove.create(positionToMove[0], positionToMove[1], self.board_id)
        self.logger.info("Location to move now: (" + str(newPos.x) + ", " + str(newPos.y) + ")")
        return CharacterDecision(decision_type="MOVE", action_position=newPos, action_index=0)



    # Find position to move using API
    def find_position_to_move(self, player: Position, destination: Position) -> Position:
        path = self.api.find_path(player.get_position(), destination)
        pos = None
        if len(path) < player.get_speed():
            pos = path[-1]
        else:
            pos = path[player.get_speed() - 1]
        return pos
    
    # Just moving down
    def move_down_position(self):
        target_pos = self.curr_pos
        target_pos.create(target_pos.x, target_pos.y, target_pos.get_board_id())
        self.logger.info("yes2")
        return target_pos

    # Use astar to find path that doesn't aggro to target destination
    def zhou_astar_path_to_move(self, player: Position, destination: Position):
        frontier = []
        path = []
        pp = player.get_position()
        heapq.heapify(frontier)
        start = Node(0, None, (pp.x, pp.y))
        heapq.heappush(frontier, (0, (pp.x, pp.y), start))
        visited = set()
        visited.add((pp.x, pp.y))
        while frontier:
            curr = heapq.heappop(frontier)[2]
            if curr.coord == (destination.x, destination.y):
                while curr:
                    path.append(curr.coord)
                    self.logger.info(str(curr.coord))
                    curr = curr.prev
                path.reverse()
                break
            neighbors = self.getNeighbors(curr.coord[0], curr.coord[1])
            for n in neighbors:
                if n not in visited:
                    dist = abs(destination.y - n[1]) + abs(destination.x - n[0])
                    newNode = Node(curr.cost + 1, curr, n)
                    heapq.heappush(frontier, (newNode.cost + dist, newNode.coord, newNode))
                    visited.add(n)
        return path[1]

    # Find valid neighbors given coordinates
    def getNeighbors(self, getx, gety):
        neighbors = []
        for n in [(0,1), (0,-1), (-1,0), (1,0)]:
            coord = (getx + n[0], gety + n[1])
            # if coord in self.obstacles or coord in self.bad_monster_squares:
            if coord in self.obstacles:
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
                curr_position = self.curr_pos
                newPos = curr_position.create(x_idx, y_idx, self.board_id)
                tile = self.board.get_tile_at(newPos)
                if tile.type == "VOID" or tile.type == "IMPASSIBLE":
                    obstacles.add((x_idx,y_idx))
        return obstacles

    # Get coords of monster aggro squares
    def get_monsters(self, game_state, board_id):
        monsters = game_state.get_monsters_on_board(board_id)
        bad_monster_squares = set()
        weakest = self.findWeakest(self.monsters, self.curr_pos)
        weakest_position = weakest.get_position()
        for monster in monsters:
            m_p = monster.get_position()
            # skip over weakest monster
            if m_p.x == weakest_position.x and m_p.y == weakest_position.y:
                continue
            for direction in [(0,1), (0,-1), (-1,0), (1,0)]:
                for step in range(monster.aggro_range):
                    bad_monster_squares.add((direction[0] * step + m_p.x , direction[1] * step + m_p.y))
        return bad_monster_squares

    # Find weakest monster
    def findWeakest(self, monsters, curr_pos):
        sortedM = sorted(monsters, key=lambda x:x.get_level())
        minLevel = 5#self.my_player.get_level()
        sameLevel = []
        j = 0
        while sortedM[j].get_level() <= minLevel:
            dist = curr_pos.manhattan_distance(sortedM[j].get_position())
            sameLevel.append((dist, sortedM[j]))
            j = j + 1
        nextMonster = sorted(sameLevel, key=lambda x:x[0])
        i = 0
        while nextMonster[i][1].get_current_health() <= 0:
            i = i + 1
        return nextMonster[i][1]

    def print_stats(self, item):

        stat_mods = item.get_stats()

        self.logger.info("item class: {}".format(item.__class__.__name__))
        try:
            self.logger.info("speed: {}, {}".format(stat_mods.get_flat_speed_change(), stat_mods.get_percent_speed_change()))
        except Exception as e:
            self.logger.error(e)
            self.logger.info("default speed: {}, {}".format(0, 0))
        try:
            self.logger.info("health: {}, {}".format(stat_mods.get_flat_health_change(), stat_mods.get_percent_health_change()))
        except Exception as e:
            self.logger.error(e)
            self.logger.info("defaulthealth: {}, {}".format(0, 0))
        try:
            self.logger.info("def: {}, {}".format(stat_mods.get_flat_defense_change(), stat_mods.get_percent_defense_change()))
        except Exception as e:
            self.logger.error(e)
            self.logger.info("default def: {}, {}".format(0, 0))
        try:
            self.logger.info("exp: {}, {}".format(stat_mods.get_flat_experience_change(), stat_mods.get_percent_experience_change()))
        except Exception as e:
            self.logger.error(e)
            self.logger.info("default exp: {}, {}".format(0, 0))
        try:
            self.logger.info("atk: {}, {}".format(stat_mods.get_flat_attack_change(), stat_mods.get_percent_attack_change()))
        except Exception as e:
            self.logger.error(e)
            self.logger.info("default atk: {}, {}".format(0, 0))
        
    def get_stat_num(self, new_item):
        new_stats = 0
        try: new_stats += stat_mod.get_flat_speed_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_percent_speed_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_flat_health_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_percent_health_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_flat_experience_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_percent_experience_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_flat_attack_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_percent_attack_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_flat_defense_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_percent_defense_change()
        except: new_stats += 0
        try: new_stats += stat_mod.get_flat_regen_per_turn()
        except: new_stats += 0
        return new_stats