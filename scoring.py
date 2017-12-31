import numpy as np

# This class scores the board
class Scoring:

	# tmp counting 
	counter = 0

	def __init__(self, game):
		self.board = game.board
		self.komi = game.komi
		self.board_sz = len(game.board)
		self.prisoners = game.prisoners
		self.score = {-1: 0, 1: 0}

		# we do not want to go over blanks twice
		self.seen_board = np.zeros(shape = (self.board_sz, self.board_sz))
	
	def add_score(self, blank_ls, stone_ls):
		# must decide if 'Dame' for scoring  
		has_white = False
		has_black = False

		# check for black and white in stone_ls
		for coord in stone_ls:
			if self.board[coord[0], coord[1]] == -1:
				has_black = True
			elif self.board[coord[0], coord[1]] == 1:
				has_white = True
			else:
				pass
		
		# exclusive or to check for 'dame'
		if has_black ^ has_white:
			print("has_black ", has_black, "has_white ", has_white)
			print(has_black ^ has_white)
			
			# second condition to prevent scoring 1st and second move of game
			if has_black and (len(blank_ls) < self.board_sz ** 2 - 2):
				self.score[-1] += len(blank_ls)
			elif has_white and (len(blank_ls) < self.board_sz ** 2 - 2): 
				self.score[1] += len(blank_ls)
			else:
				pass

	def add_to_seen(self, blank_ls):
		for coord in blank_ls:
			self.seen_board[coord[0], coord[1]] = 1 # set it equal to 1

	def _valid_move(self, start, blank_ls):
		# test if valid move (exists on board, or isn't going into itself)
		if (start[0] < 0 or start[0] >= self.board_sz
			or start[1] < 0 or start[1] >= self.board_sz
			or start in blank_ls):

			#print("flood fill test: invalid move, ", start)
			return False 
		else:
			return True

	# recursively counts for score 
	def flood_fill_cnt(self, start, blank_ls, stone_ls):
		Scoring.counter += 1


		row = start[0]
		col = start[1]

		if self._valid_move((row, col), blank_ls) == False:
			return blank_ls, stone_ls

		up = (row - 1, col)
		down = (row + 1, col)
		left = (row, col - 1)
		right = (row, col + 1)

		# We need fast performance - need to check if valid BEFORE we recurse
		if self.board[row, col] == 0: # it's a blank. keep counting score.
			blank_ls.append((row, col))
			if self._valid_move(up, blank_ls):
				blank_ls1, stone_ls1 = self.flood_fill_cnt(up, blank_ls, stone_ls)
			else: 
				blank_ls1, stone_ls1 = blank_ls, stone_ls

			if self._valid_move(down, blank_ls):
				blank_ls2, stone_ls2 = self.flood_fill_cnt(down, blank_ls, stone_ls)
			else: 
				blank_ls2, stone_ls2 = blank_ls, stone_ls

			if self._valid_move(left, blank_ls):
				blank_ls3, stone_ls3 = self.flood_fill_cnt(left, blank_ls, stone_ls)
			else: 
				blank_ls3, stone_ls3 = blank_ls, stone_ls

			if self._valid_move(right, blank_ls):
				blank_ls4, stone_ls4 = self.flood_fill_cnt(right, blank_ls, stone_ls)
			else: 
				blank_ls4, stone_ls4 = blank_ls, stone_ls

		elif self.board[row, col] != 0: # It is a stone. Stop looking 
			stone_ls.append((row, col))
			return blank_ls, stone_ls
		else:
			raise ValueError

		#blank_ls = blank_ls1.extend(blank_ls2.extend(blank_ls3.extend(blank_ls4)))
		# extend is an inplace function
		blank_ls = (blank_ls1 + blank_ls2) + (blank_ls3 + blank_ls4)
		#if (len(stone_ls1) + len(stone_ls2) + len(stone_ls3) + len(stone_ls4) > 0):
		stone_ls = (stone_ls1 + stone_ls2) + (stone_ls3 + stone_ls4)

		return blank_ls, stone_ls

	def score_it(self):
		import time
		t0 = time.time()
		for i in range(self.board_sz):
			for j in range(self.board_sz):
				if self.seen_board[i, j] == 0:
					blank_ls, stone_ls = self.flood_fill_cnt((i, j), [], [])
					# remove duplicates, then turn to set again
					if len(blank_ls) > 0:
						blank_ls = list(set(blank_ls))
						self.add_to_seen(blank_ls)
						self.add_score(blank_ls, stone_ls)

		# count opposite color which is captured, and add to score
		black_score = self.score[-1] + self.prisoners[1]
		white_score = self.score[1] + self.prisoners[-1]

		t1 = time.time()
		print(t1 - t0)

		final_score = {-1: black_score, 1: white_score + self.komi} 
		return final_score

