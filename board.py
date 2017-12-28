import numpy as np

class Game:
	def __init__(self, komi, board):
		self.board = board
		self.komi = komi
		self.board_sz = len(board)
		# need to prevent aliasing in board
		self.board_hist = [np.copy(board)] 
		self.prisoners = {-1: 0, 1: 0}

	def not_suicidal(self, move):
		self.place_piece(move)
		captures_anything = False

		# check to see if it captures anything, which would make it OK
		moves_ls = self.get_valid_moves(move)
		for elem in moves_ls:
			# check OPPOSITE COLOR liberties
			liberties, seen_ls = self.flood_fill_liberties(elem, flip(move[2]), [])
			if liberties == 0 and len(seen_ls) != 0:
				print('Something is captured')
				captures_anything = True	

		# The move captures nothing - now we check if is also suicidal 
		if captures_anything is False:
			# check CURRENT color liberties
			print('nothing captured... checking if suicidal')
			print(move)
			liberties, seen_ls = self.flood_fill_liberties(move, move[2], [])
			print(liberties)
			if liberties == 0:
				# placing the piece gives 0 liberties. isnt_suicidal val is FALSE
				print('Nothing is captured, and placing in suicidal part')
				self.board = np.copy(self.board_hist[-1]) # reset the board
				return False
			else: # there are liberties still. not suicidal
				print('Nothing is captured, but not suicidal')
				self.board = np.copy(self.board_hist[-1]) # reset the board
				return True
			
		# something is captured, so move is not suicidal	
		else: # captures_anything is True
			self.board = np.copy(self.board_hist[-1]) # reset the board
			return True

	# determines if the ko rule is in effect
	def ko_rule_valid(self, move):
		self.place_piece(move)
		prisoner_dict = dict(self.prisoners)
		self.life_and_death(move)
		
		ko_valid = True
	
		if len(self.board_hist) < 4:
			ko_valid = True

		# need to implement compares
		elif np.array_equal(self.board_hist[-2], self.board):
			ko_valid = False
		
		self.prisoners = prisoner_dict # reset the prisoner count after test
		self.board = np.copy(self.board_hist[-1]) # reset the board
		return ko_valid

		
	# Greedy boolean evaluate
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



	# recursively counts for liberties and carries the seen_list
	# may double count liberties - but 0 is 0
	def flood_fill_liberties(self, start, cap_color, seen_ls):

		# test if valid move
		if (start[0] < 0 or start[0] >= self.board_sz
			or start[1] < 0 or start[1] >= self.board_sz
			or start in seen_ls):

			print("flood fill test: invalid move, ", start)
			return 0, seen_ls

		row = start[0]
		col = start[1]

		if self.board[row, col] == cap_color: # the same color: keep looking
			seen_ls.append((row, col))
			libt1 = self.flood_fill_liberties((row - 1, col), cap_color, seen_ls)
			libt2 = self.flood_fill_liberties((row + 1, col), cap_color, seen_ls)
			libt3 = self.flood_fill_liberties((row, col - 1), cap_color, seen_ls)
			libt4 = self.flood_fill_liberties((row, col + 1), cap_color, seen_ls)

		elif self.board[row, col] == 0: # there is a liberty - its blank
			return 1, seen_ls
		elif self.board[row, col] == flip(cap_color): # opposite color. no liberty
			return 0, seen_ls
		else:
			raise ValueError

		liberties = libt1[0] + libt2[0] + libt3[0] + libt4[0]
		#print(liberties, seen_ls)
		return liberties, seen_ls
		
	# removes the 'seen' list if it has no liberties
	def remove_seen_ls(self, seen_ls):
		print('removing seen list')
		print(seen_ls)
		for coord in seen_ls:
			x = coord[0]
			y = coord[1]
			self.board[x,y] = 0
			
	# looks in four directions to return list of directions to check
	def get_valid_moves(self, move):
		# check life and death for all for directions
		up = (move[0] - 1, move[1])
		down = (move[0] + 1, move[1])
		left = (move[0], move[1] - 1)
		right = (move[0], move[1] + 1)

		# makes sure each move is valid
		raw_list = [up, down, left, right]
		valid_list = []
		for elem in raw_list:
			if (elem[0] >= 0 and elem[0] <= self.board_sz
				and elem[1] >= 0 and elem[1] <= self.board_sz):
				valid_list.append(elem)

		return valid_list

	# checks which are alive and which are dead. Updates it
	def life_and_death(self, move):
		captured_color = flip(move[2])
		print('captured color: ', captured_color)
		valid_list = self.get_valid_moves(move)
		
		for elem in valid_list:
			liberties, seen_ls = self.flood_fill_liberties(elem, captured_color, [])
			if liberties == 0:
				print('no liberties')
				self.remove_seen_ls(seen_ls)
				prisoners_num = len(seen_ls)
				if captured_color == -1:
					self.prisoners[-1] += prisoners_num
				elif captured_color == 1:
					self.prisoners[1] += prisoners_num
				else: 
					raise ValueError

	def place_piece(self, move):
		x = move[0]
		y = move[1]
		print("before piece placed: ", self.board[x,y])
		self.board[x,y] = move[2]
		print("after piece placed: ", self.board[x,y])

	# the main entry point into board updating
	def update(self, move):

		# passing logic, move color is 0
		if move[2] == 0:
			self.board_hist.append(np.copy(self.board))
			return True	
		
		# make sure move is valid before placing
		if self.is_valid(move):
			print(move)
			self.place_piece(move)
			print('after move...')
			self.life_and_death(move)
			self.board_hist.append(np.copy(self.board))

			return True
		else:
			return False

	def is_playing(self):
		return True

def flip(turn):
	if turn is -1: 
		return 1				
	elif turn is 1:
		return -1
	elif turn is 0:
		return  'Not Empty'
	else:
		raise ValueError
