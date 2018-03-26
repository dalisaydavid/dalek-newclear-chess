from __future__ import print_function
from copy import deepcopy
""" Initial board state.
 
     - N R K R N -  (COMPUTER)
     - - - B - - -
     - - - B - - -
     P - P - P - P
     - - - - - - -
     p - p - p - p
     - - - b - - -
     - - - b - - -
     - n r k r n -  (HUMAN)

"""

class Board:
	def __init__(self, rows, columns):
		self.rows = rows
		self.columns = columns
		self.board = [
			["-", "N", "R", "K", "R", "N", "-"],
			["-", "-", "-", "B", "-", "-", "-"],
			["-", "-", "-", "B", "-", "-", "-"],
			["P", "-", "P", "-", "P", "-", "P"],
			["-", "-", "-", "-", "-", "-", "-"],
			["p", "-", "p", "-", "p", "-", "p"],
			["-", "-", "-", "b", "-", "-", "-"],
			["-", "-", "-", "b", "-", "-", "-"],
			["-", "n", "r", "k", "r", "n", "-"]
		]

		self.indexed_board = [[j for j in range(i,i+7)] for i in range(0, 63, 7)]

		# List of lists. Each list in this list looks like:
		# <board_state>
		self.move_stack = []
	
	def retract_move(self):
		self.board = self.move_stack.pop()

	def get_state_hash(self):
		return "".join(["".join(row) for row in self.board])

	def get_location_of_piece(self, piece):
		for row_index in range(len(self.board)):
			for col_index in range(len(self.board[row_index])):
				if self.board[row_index][col_index] == piece:
					return (row_index,col_index)

	def get_pieces_remaining(self):
		pieces = {}
		row_index = 0
		for row in self.board:
			col_index = 0
			for col in row:
				if col != "-":
					pieces[col] = (row_index, col_index)
				col_index += 1
			row_index += 1
					
		return pieces

	# @param start: position of the piece.
	# @param piece_type OPTIONAL: 'c' for computer, 'h' for human. 
	def get_pieces_adjacent_to(self, start, piece_type=None):
		explosion_range = [
			start, 						# Middle (start==end. Same thing.)
			(start[0]-1,start[1]), 		# North
			(start[0]-1,start[1]+1),	# NorthEast
			(start[0],start[1]+1),		# East
			(start[0]+1,start[1]+1),	# SouthEast
			(start[0]+1,start[1]),		# South
			(start[0]+1,start[1]-1),	# SouthWest
			(start[0],start[1]-1),		# West
			(start[0]-1,start[1]-1),	# NorthWest
		]

		exploded_pieces = []
		for explosion_position in explosion_range:
			# if the explosions are not valid... skip them.
			if explosion_position[0] < 0 or explosion_position[0] > 8 or explosion_position[1] < 0 or explosion_position[1] > 6:
				continue
			if self.board[explosion_position[0]][explosion_position[1]] == '-':
				continue
			
			exploded_pieces.append(self.board[explosion_position[0]][explosion_position[1]])

		if not piece_type:
			return exploded_pieces
		elif piece_type == 'c':
			return filter(lambda piece: piece.isupper(), exploded_pieces)
		elif piece_type == 'h':
			return filter(lambda piece: piece.islower(), exploded_pieces)
		else:
			return []

	def move(self, piece, start, end):
		# Add this board state to the stack.
		self.move_stack.append(deepcopy(self.board))

		total_exploded = 0
		captured_piece = None

		# It's an explosion...
		if start[0] == end[0] and start[1] == end[1]:
			explosion_range = [
				start, 						# Middle (start==end. Same thing.)
				(start[0]-1,start[1]), 		# North
				(start[0]-1,start[1]+1),	# NorthEast
				(start[0],start[1]+1),		# East
				(start[0]+1,start[1]+1),	# SouthEast
				(start[0]+1,start[1]),		# South
				(start[0]+1,start[1]-1),	# SouthWest
				(start[0],start[1]-1),		# West
				(start[0]-1,start[1]-1),	# NorthWest
			]

			for explosion_position in explosion_range:
				# if the explosions are not valid... skip them.
				if explosion_position[0] < 0 or explosion_position[0] > 8 or explosion_position[1] < 0 or explosion_position[1] > 6:
					continue
				if self.board[explosion_position[0]][explosion_position[1]] == '-':
					continue
				
				exploded_piece = self.board[explosion_position[0]][explosion_position[1]]
				self.board[explosion_position[0]][explosion_position[1]] = '-'
				
				total_exploded += 1
				
			if total_exploded > 0:
				pass
				# print("boom.")

		else: # Normal move, no explosion.
			if self.board[end[0]][end[1]] != "-":
				captured_piece = self.board[end[0]][end[1]]

			self.board[start[0]][start[1]] = "-"
			self.board[end[0]][end[1]] = piece

		# Returns whether or not there was an exploded piece and whether or not there was a capture.
		return (total_exploded > 0, captured_piece is not None)

	def pad_string(self, value, padding):
		return "{value: <{padding}}".format(value=value, padding=padding)

	def display(self):
		for row_index in range(self.rows):
			for column_index in range(self.columns):
				if column_index == 0:
					print(self.pad_string(self.rows-row_index, 3), end='')
				print(self.pad_string(self.board[row_index][column_index], 3), end='')
			print()
		print('   ' + ''.join(map(lambda c: self.pad_string(c, 3), ['A','B','C','D','E','F','G'])))