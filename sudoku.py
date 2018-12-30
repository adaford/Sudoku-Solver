#!/usr/bin/python

import numpy as np
import sys
import copy


'''ddd
File reading function for sudoku
Input: filename
Output: a list of 2D numpy matrices representing sudokus
'''
def read_sudoku(fname):
	with open(fname) as f:
		f_input = [x.strip('\r\n') for x in f.readlines()]

	sudoku_list = []
	for i in xrange(len(f_input)):
		sudoku = np.zeros((9, 9))
		temp = f_input[i]
		for j in xrange(0, len(temp), 9):
			sudoku_row = temp[j:j + 9]
			for k in xrange(0, 9):
				sudoku[j / 9][k] = sudoku_row[k]
		sudoku_list.append(sudoku)

	return sudoku_list


'''
Printing function for sudoku,
Input: a 2D numpy matrix
'''
def print_sudoku(sudoku):
	print '+-------+-------+-------+'
	for i in xrange(0, 9):
		for j in xrange(0, 9):
			if j == 0:
				print '|',
			if sudoku[i][j] != 0:
				print int(sudoku[i][j]),
			else:
				print '*',
			if (j + 1) % 3 == 0:
				print '|',
		print ''
		if (i + 1) % 3 == 0:
			print '+-------+-------+-------+'
	print ''


'''
Utility function for finding constraints
Input: coordinate [row, col]
Output: constraints
'''
def get_constraint(coordinate, sudoku):
	value = sudoku[coordinate[0]][coordinate[1]]
	if value == 0:
		row = sudoku[coordinate[0], :]
		col = sudoku[:, coordinate[1]]

		row_constraint = row[np.nonzero(row)]
		col_constraint = col[np.nonzero(col)]
		block = get_block(coordinate, sudoku)

		blo_constraint = block[np.nonzero(block)]

		all_constraint = np.unique(np.concatenate((row_constraint, col_constraint, blo_constraint)))
		return all_constraint
	else:
		print 'not a variable'


'''
Utility function for getting a 3x3 sudoku block given a coordinate
Input: coordinate [row, col]
Output: 3x3 numpy matrix
'''
def get_block(coordinate, sudoku):
	row_range = [3 * (coordinate[0] / 3), 3 * (coordinate[0] / 3) + 3]
	col_range = [3 * (coordinate[1] / 3), 3 * (coordinate[1] / 3) + 3]
	return sudoku[row_range[0]:row_range[1], col_range[0]:col_range[1]]


def create_domains(sudoku):
	domains = []
	
	for i in range (0,9):
		for j in range (0,9):
			if sudoku[i][j] > 0:
				domains.append([sudoku[i][j]])
			else:
				domains.append([1,2,3,4,5,6,7,8,9])

	return domains

#return int block_number in range (0,8)
def find_block_number(coordinate):
	row = coordinate[0]
	col = coordinate[1]
	square = row * 9 + col

	if square < 9:
		block_number = square / 3
	elif square < 18:
		block_number = (square - 9) / 3
	elif square < 27:
		block_number = (square - 18) / 3

	elif square < 36:
		block_number = (square - 27) / 3 + 3
	elif square < 45:
		block_number = (square - 36) / 3 + 3
	elif square < 54:
		block_number = (square - 45) / 3 + 3

	elif square < 63:
		block_number = (square - 54) / 3 + 6
	elif square < 72:
		block_number = (square - 63) / 3 + 6
	elif square < 81:
		block_number = (square - 72) / 3 + 6

	return block_number

#return all coordinates in the given block
def find_block_coordinates(block_number):
	coordinates = []

	for i in range ((block_number / 3) * 3, ((block_number / 3) * 3) + 3):
		for j in range ((block_number % 3) * 3 , ((block_number % 3) * 3) + 3):
			coordinates.append([i,j])

	return coordinates

#find all arcs of a given coordinate
def find_neighbors(coordinate, sudoku):
	neighbors = []

	row = coordinate[0]
	col = coordinate[1]
	block_coordinates = find_block_coordinates(find_block_number(coordinate))
	
	for i in range (0,9):
		if i != row:
			neighbors.append([i,col])

	for j in range (0,9):
		if j != col:
			neighbors.append([row, j])

	for coordinates in block_coordinates:
		if coordinates[0] != row and coordinates[1] != col:
			neighbors.append(coordinates)

	return neighbors


def create_arcs(sudoku):
	arcs = []
	
	for i in range (0,9):
		for j in range (0,9):
			neighbors = find_neighbors([i,j], sudoku)
			for neighbor in neighbors:
				arcs.append([[i,j], neighbor])
	
	return arcs

def revise(sudoku, arc, domains):
	arc0 = arc[0][0] * 9 + arc[0][1]
	arc1 = arc[1][0] * 9 + arc[1][1]

	if len(domains[arc1]) == 1 and domains[arc1][0] in domains[arc0] and len(domains[arc0]) > 1:
		domains[arc0].remove(domains[arc1][0])
		return True

	return False

'''
AC-3 Algorithm
Input: 2D numpy matrix
Output: return True if a solution is found, with solved sudoku, False otherwise, with original sudoku
'''
def ac3(sudoku):
	orig_sudoku = copy.deepcopy(sudoku)

	domains = create_domains(sudoku) 

	arcs = create_arcs(sudoku)

	change = True

	while change == True:
		single_domain_count = 0
		change = False

		for arc in arcs:
			if revise(orig_sudoku, arc, domains) == True:
				change = True
		

		for i in range (0,9):
			for j in range (0,9):
				if len(domains[i * 9 + j]) == 1:
					single_domain_count += 1
					orig_sudoku[i][j] = domains[i * 9 + j][0]

		if single_domain_count == 81:
			return True, orig_sudoku

	return False, sudoku


def backtrack(queue):
	domains = copy.deepcopy(queue[0])
	del queue[0]
	return domains

#check for empty domains
def check_domains(domains):
	for domain in domains:
		if len(domain) == 0:
			return False

	return True
'''
Backtracking search Algorithm
Input: 2D numpy matrix
Output: return True if a solution is found, with solved sudoku, False otherwise, with original sudoku
'''
def bts(sudoku):
	solved_sudoku = copy.deepcopy(sudoku)

	domains = create_domains(sudoku)
	domains_orig = create_domains(sudoku) 
	arcs = create_arcs(sudoku)
	queue = [domains_orig]
	change = True

	# 1 revisory loop

	for arc in arcs:
		revise(solved_sudoku, arc, domains)
		
	while change == True or len(queue) > 0:
		change = False

		#find next square using MVR
		mvr = 9
		domain_counter = 0
		square = 0
		for domain in domains:
			if len(domain) < mvr and len(domain) > 1:
				mvr = len(domain)
				square = domain_counter
			domain_counter += 1
		
		#test next value
		test_value = domains[square][0]
		del domains[square][0]
		queue.insert(0, copy.deepcopy(domains))
		domains[square] = [test_value]

		#revise until a domain becomes empty
		change2 = True
		while check_domains(domains) == True and change2 == True:
			change2 = False
			for arc in arcs:
				if revise(solved_sudoku, arc, domains) == True:
					change = True
					change2 = True

		#test if finished or needs backtrack
		single_domain_count = 0
		bt = True
		while bt == True:
			bt = False
			for i in range (0,9):
				for j in range (0,9):
					if len(domains[i * 9 + j]) == 0:
						domains = backtrack(queue)
						bt = True
					elif len(domains[i * 9 + j]) == 1:
						single_domain_count += 1
						solved_sudoku[i][j] = domains[i * 9 + j][0]
					

		if single_domain_count == 81:
			return True, solved_sudoku

	return False, sudoku

'''
Main function
'''
def main():
	solved_count = 0
	sudoku_list = read_sudoku(sys.argv[1])
	solved_sudokus = []
	for sudoku in sudoku_list:
		print_sudoku(sudoku)
		if sys.argv[2] == 'ac3':
			print 'Using AC-3'
			solved, ret_sudoku = ac3(sudoku)
			if solved:
				print 'Solved Sudoku'
				print_sudoku(ret_sudoku)
				solved_count += 1
			else:
				print 'No solution found'
			solved_sudokus.append(ret_sudoku.flatten())
		elif sys.argv[2] == 'bts':
			print 'Using backtracking search'
			solved, ret_sudoku = bts(sudoku)
			if solved:
				print 'Solved Sudoku'
				print_sudoku(ret_sudoku)
				solved_count += 1
			else:
				print 'No solution found'
			solved_sudokus.append(ret_sudoku.flatten())
		else:
			print 'No such type'
		print ''
	print str(solved_count) + " " + "solved puzzles"

	np.savetxt('sudoku_solutions_'+sys.argv[2]+'.txt', solved_sudokus, fmt='%d', delimiter='')


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Arguments error'
	else:
		main()
