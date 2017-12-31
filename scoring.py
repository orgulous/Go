import numpy as np
import board as bd

# This class scores the board
class Scoring:

	def __init__(self, game):
		self.board = game.board
		self.komi = game.komi
		self.board_sz = len(game.board)
		self.prisoners = game.prisoners
		self.score = {-1: 0, 1: 0}

		# we do not want to go over blanks twice
		self.seen_board = np.zeros(shape = (self.board_sz, self.board_sz))

	# add up the score given list of blanks for a particular 'patch'
	def _add_score(self, blank_ls, stone_ls):
		# must decide if 'Dame' for scoring  
		has_white = False
		has_black = False

		# check for black and white in stone_ls
		for coord in stone_ls:
			if self.board[coord[0], coord[1]] == -1:
				has_black = True
			elif self.board[coord[0], coord[1]] == 1:
				has_white = True
		
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

	# keep track of parts of grid you have seen before
	def _add_to_seen(self, blank_ls):
		for coord in blank_ls:
			self.seen_board[coord[0], coord[1]] = 1 # set it equal to 1

	# recursively counts for score 
	# main logic for counting score
	def _flood_fill_cnt(self, start, blank_ls, stone_ls):
		row, col  = start[0], start[1]

		if not bd.in_board(start, self.board_sz) or start in blank_ls:
			#evalid_fill((row, col), blank_ls, stone_ls) == False:
			return blank_ls, stone_ls

		up = (row - 1, col)
		down = (row + 1, col)
		left = (row, col - 1)
		right = (row, col + 1)
		directions = [up, down, left, right]

		# LUCAS PLEASE REVIEW THIS BLOCK
		# We need fast performance - need to check if valid BEFORE we recurse
		if self.board[row, col] == 0: # it's a blank. keep counting score.
			blank_ls.append((row, col))

			if bd.in_board(up, self.board_sz) and up not in blank_ls:
				blank_ls1, stone_ls1 = self._flood_fill_cnt(up, blank_ls, stone_ls)
			else: 
				blank_ls1, stone_ls1 = blank_ls, stone_ls

			if bd.in_board(down, self.board_sz) and down not in blank_ls:
				blank_ls2, stone_ls2 = self._flood_fill_cnt(down, blank_ls, stone_ls)
			else: 
				blank_ls2, stone_ls2 = blank_ls, stone_ls

			if bd.in_board(left, self.board_sz) and left not in blank_ls:
				blank_ls3, stone_ls3 = self._flood_fill_cnt(left, blank_ls, stone_ls)
			else: 
				blank_ls3, stone_ls3 = blank_ls, stone_ls

			if bd.in_board(right, self.board_sz) and right not in blank_ls:
				blank_ls4, stone_ls4 = self._flood_fill_cnt(right, blank_ls, stone_ls)
			else: 
				blank_ls4, stone_ls4 = blank_ls, stone_ls

		elif self.board[row, col] != 0: # It is a stone. Stop looking 
			stone_ls.append((row, col))
			return blank_ls, stone_ls
		else:
			raise ValueError

		# add up the lists
		blank_ls = blank_ls1 + blank_ls2 + blank_ls3 + blank_ls4
		stone_ls = stone_ls1 + stone_ls2 + stone_ls3 + stone_ls4
	
		return blank_ls, stone_ls

	# score each of the positions by counting territories surrounded by colors
	# returns a final score
	def score_it(self):

		# find all 'patches' of empty board spaces surrounded by a color
		for i in range(self.board_sz):
			for j in range(self.board_sz):
				
				# make sure you don't count the same patch twice
				if self.seen_board[i, j] == 0:
					blank_ls, stone_ls = self._flood_fill_cnt((i, j), [], [])

					# remove duplicates, then add the score up using 
					if len(blank_ls) > 0:
						blank_ls = list(set(blank_ls))
						self._add_to_seen(blank_ls)
						self._add_score(blank_ls, stone_ls)

		# count opposite color which is captured, and add to score
		black_score = self.score[-1] + self.prisoners[1]
		white_score = self.score[1] + self.prisoners[-1]

		final_score = {-1: black_score, 1: white_score + self.komi} 
		return final_score

