import csv
import sys

def read_data(csv_file):
	"""Read a csv file and return a list of itemset."""
	res = []
	with open(csv_file, 'rU') as f:
		reader = csv.reader(f)
		for row in reader:
			res.append(list(set(row)))  # Remove duplicates in one itemset.
	res.pop(0)  # Remove the csv header row.
	return res

def check_and_join(itemset_1, itemset_2):
	""" Implement the join step in apriori_gen function.

	Details:
		Let p = itemset1, q = temset2 be two (k-1)-itemsets in L_{k-1}.
		Check whether p.item_1 = q.item_1 ... q.item_{k-2} = p.item_{k-2}, p.item_{k-1} < q.item_{k-1}.
		If yes, returns a new itemset = p U q. Otherwise, return None.

	Args:
		itemset_1: a tuple of length k-1.
		itemset_2: a tuple of length k-1.

	Returns:
		If check is True, return new_itemset: an tuple of length k.
		If check is False, return False.

	"""
	l = len(itemset_1)
	if itemset_1[-1] < itemset_2[-1] and itemset_1[: l - 1] == itemset_2[: l - 1]:
		new_itemset = list(itemset_1[:])
		new_itemset.append(itemset_2[-1])
		return tuple(new_itemset)
	else:
		return False

def apriori_gen(prev_l):
	""""Generate candidates for k-itemsets from (k-1)-itemsets.

	Args:
		prev_l: a list of itemset of length k-1.

	Returns:
		curr_l: a list of itemset of length k derived from prev_l.
	
	"""
	# Join step.
	curr_l = []
	for i in range(0, len(prev_l)):
		for j in range(i + 1, len(prev_l)):
			itemset = check_and_join(prev_l[i], prev_l[j])
			if itemset:
				curr_l.append(itemset)
			else:
				break

	# Prune step.
	remove_l = []
	for itemset in curr_l:
		for item in itemset:
			subset = list(itemset[:])
			subset.remove(item)
			subset = tuple(subset)
			if subset not in prev_l:
				remove_l.append(itemset)
				break
	for itemset in remove_l:
		curr_l.remove(itemset)
	return curr_l

def contain_sublist(lst, sub_lst):
	return set(lst + sub_lst) == set(lst)

def add_itemset_freq(itemset_freq, itemset):
	if itemset in itemset_freq:
		itemset_freq[itemset] += 1
	else:
		itemset_freq[itemset] = 1

def apriori_algorithm(dataset, min_supp):
	"""Use Apriori Algorithm to find all larget itemsets that have support >= min_supp. 

	Args:
		dataset: the list of itemset where each itemset is a list of items (words).
		min_supp: the minimum support given by user.

	Returns: 
		large_itemsets (list).

	"""
	large_itemsets = []  # Contains all large itemsets, each itemset is of type ().
	itemset_freq = {}  # The occurences of each itemset, e.g. {("jacket"): 35}.
	transaction_num = len(dataset)

	# First pass: count item occurences to determine the large 1-itemsets.
	for transaction in dataset:
		print transaction
		for item in transaction:
			itemset = (item,)
			add_itemset_freq(itemset_freq, itemset)
	l1 = []  # store the large 1-itemsets.
	for itemset, freq in itemset_freq.iteritems():
		if float(freq) / transaction_num >= min_supp:
			l1.append(itemset)
	l1.sort()
	large_itemsets += l1

	# For kth pass, l store the  
	prev_l = l1
	while prev_l:
		candidates =  apriori_gen(prev_l)
		for row in dataset:
			for itemset in candidates:
				if contain_sublist(row, list(itemset)):
					add_itemset_freq(itemset_freq, itemset)
		curr_l = []
		for itemset in candidates:
			if itemset in itemset_freq and float(itemset_freq[itemset]) / transaction_num >= min_supp:
				curr_l.append(itemset)
		large_itemsets += curr_l
		prev_l = curr_l

	print itemset_freq
	return large_itemsets

def build_association_rules(large_itemsets):
	pass

if __name__ == "__main__":
	# Get command line arguments.
	csv_file= sys.argv[1]
	min_supp = float(sys.argv[2])
	min_conf = float(sys.argv[3])

	# Read transactions data from file.
	dataset = read_data(csv_file)

	# Find large itemsets by Apriori algorithm.
	large_itemsets = apriori_algorithm(dataset, min_supp)

	# Build association rules from large itemsets.
	build_association_rules(large_itemsets)