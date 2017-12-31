import numpy as np

class Game:
	def __init__(self, komi, board):
		self.board = board
		self.komi = komi
		self.board_sz = len(board)

		# keeps track of board history for 'ko' rule
		self.board_hist = [np.copy(board)] 
	
		# keeps track for scoring
		self.prisoners = {-1: 0, 1: 0}

	# function called from is_valid
	# valid Moves must not be suicidal 
	def not_suicidal(self, move):
		self.place_piece(move)

		# first check if move captures anything. If not, do logic for suicidal move
		captures_anything = False

		# check to see if it captures anything. If capturing something, move valid
		moves_ls = self._get_cardinal_directions(move)
		for elem in moves_ls:
			# check OPPOSITE COLOR liberties
			liberties, seen_ls = self.flood_fill_liberties(elem, flip(move[2]), [])
			if liberties == 0 and len(seen_ls) != 0:
				captures_anything = True	

		# The move captures nothing - now we check if is also suicidal 
		if captures_anything is False:
			# check CURRENT color liberties
			liberties, seen_ls = self.flood_fill_liberties(move, move[2], [])
			if liberties == 0:
				# placing the piece gives 0 liberties. 
				self.board = np.copy(self.board_hist[-1]) # reset the board
				# False - the move IS suicidal and Invalid
				return False
			else: # there are liberties still. not suicidal
				self.board = np.copy(self.board_hist[-1]) # reset the board
				return True
			
		# something is captured, so move is not suicidal	
		else: # captures_anything is True
			self.board = np.copy(self.board_hist[-1]) # reset the board
			return True

	# function called from is_valid
	# determines if the ko rule is in effect
	def ko_rule_valid(self, move):
		self.place_piece(move)
		# copy the prisoner dictionary for re-use
		prisoner_dict = dict(self.prisoners)

		# must evaluate the move to see
		self.life_and_death(move)
		
		ko_valid = True
	
		# ko is impossible for first few moves
		if len(self.board_hist) < 4:
			ko_valid = True
		
		# check previous board positions for ko rule 
		elif np.array_equal(self.board_hist[-2], self.board):
			ko_valid = False
		
		self.prisoners = prisoner_dict # reset the prisoner count after test
		self.board = np.copy(self.board_hist[-1]) # reset the board
		return ko_valid
		
	# Greedy boolean evaluation to see if it is valid
	def is_valid(self, move):
		if self.board[move[0], move[1]] == 0:
			if self.not_suicidal(move):
				if self.ko_rule_valid(move):
					return True
				else:
					return False
			else:
				return False
		else:
			return False

	'''
	The main recursive algorithm for flood_fill.
	Flood fill explores adjacent spaces in the board which are of a 
	similar color. It returns the explored spaces and also the number of 
	open adjacent spaces to the group

	A recursive solution is used because the board size is very small (20x20),
	and performance is not an issue
	'''
	def flood_fill_liberties(self, start, cap_color, seen_ls):

		# test if move is on the board grid or is already explored
		if not in_board(start, self.board_sz) or start in seen_ls:
			return 0, seen_ls

		row = start[0]
		col = start[1]

		# the same color: keep looking
		if self.board[row, col] == cap_color: 
			seen_ls.append((row, col)) # keep track of the pieces seen

			# look in four directions for more spaces
			libt1, _ = self.flood_fill_liberties((row - 1, col), cap_color, seen_ls)
			libt2, _ = self.flood_fill_liberties((row + 1, col), cap_color, seen_ls)
			libt3, _ = self.flood_fill_liberties((row, col - 1), cap_color, seen_ls)
			libt4, _ = self.flood_fill_liberties((row, col + 1), cap_color, seen_ls)

		elif self.board[row, col] == 0: # there is a liberty - its blank
			return 1, seen_ls
		elif self.board[row, col] == flip(cap_color): # opposite color. no liberty
			return 0, seen_ls
		else:
			raise ValueError

		# sum up the liberties #TODO CHANGE
		liberties = libt1 + libt2 + libt3 + libt4
		return liberties, seen_ls
		
	# removes the pieces in the 'seen' list if it has no liberties: they're captured
	def remove_seen_ls(self, seen_ls):
		for coord in seen_ls:
			x = coord[0]
			y = coord[1]
			self.board[x,y] = 0
			

	# looks in four directions to return list of directions to check
	def _get_cardinal_directions(self, move):
		# check life and death for all for directions
		up = (move[0] - 1, move[1])
		down = (move[0] + 1, move[1])
		left = (move[0], move[1] - 1)
		right = (move[0], move[1] + 1)

		# makes sure each move is valid
		raw_list = [up, down, left, right]
		valid_list = []
		for elem in raw_list:
			if in_board(elem, self.board_sz):
				valid_list.append(elem)

		return valid_list

	# Checks which pieces are alive and which are dead. Updates it
	def life_and_death(self, move):
		captured_color = flip(move[2])

		# look in four directions of piece placed to check captures
		valid_list = self._get_cardinal_directions(move)
		
		# run each check in four directions using flood_fill algorithm
		for elem in valid_list:
			liberties, seen_ls = self.flood_fill_liberties(elem, captured_color, [])
			if liberties == 0:
				self.remove_seen_ls(seen_ls)

				# updates prisoners count
				prisoners_num = len(seen_ls)
				if captured_color == -1:
					self.prisoners[-1] += prisoners_num
				elif captured_color == 1:
					self.prisoners[1] += prisoners_num
				else: 
					raise ValueError

	# places the piece on the board
	def place_piece(self, move):
		x = move[0]
		y = move[1]
		self.board[x,y] = move[2]

	# the main entry point into board logic and board updating
	def update(self, move):

		# Player 'passes' in move, move color is '0'
		if move[2] == 0:
			self.board_hist.append(np.copy(self.board))
			return True	
		
		# make sure move is valid before placing
		if self.is_valid(move):
			self.place_piece(move)
			self.life_and_death(move)
			self.board_hist.append(np.copy(self.board))

			return True
		else:
			return False

# Class function used to flip turns
def flip(turn):
	if turn is -1: 
		return 1				
	elif turn is 1:
		return -1
	else:
		raise ValueError

def in_board(elem, sz):
	if (elem[0] >= 0 and elem[0] < sz
		and elem[1] >= 0 and elem[1] < sz):
		return True
	else:
		return False
