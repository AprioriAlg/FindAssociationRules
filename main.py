import csv
import operator
import itertools
import sys

OUTPUT_FILE = "output.txt"

def read_data(csv_file):
	"""Read a csv file and return a list of itemset."""
	res = []
	with open(csv_file, 'rU') as f:
		reader = csv.reader(f)
		for row in reader:
			row = list(set(row))
			if '' in row:
				row.remove('')
			res.append(row)  # Remove duplicates in one itemset.
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

def apriori_algorithm(dataset, min_supp, itemset_freq, fo):
	"""Use Apriori Algorithm to find all larget itemsets that have support >= min_supp. 

	Args:
		dataset: the list of itemset where each itemset is a list of items (words).
		min_supp: the minimum support given by user.
		itemset_freq: record the occurences (>=1) of each itemset.

	Returns: 
		large_itemsets (list).

	"""
	large_itemsets_supp = {}
	transaction_num = len(dataset)

	# First pass: count item occurences to determine the large 1-itemsets.
	for transaction in dataset:
		for item in transaction:
			itemset = (item,)
			add_itemset_freq(itemset_freq, itemset)
	l1 = []  # store the large 1-itemsets.
	for itemset, freq in itemset_freq.iteritems():
		supp = float(freq) / transaction_num
		if supp >= min_supp:
			l1.append(itemset)
			large_itemsets_supp[itemset] = supp
	l1.sort()

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
			if itemset in itemset_freq:
				supp = float(itemset_freq[itemset]) / transaction_num
				if supp >= min_supp:
					curr_l.append(itemset)
					large_itemsets_supp[itemset] = supp
		prev_l = curr_l

	fo.write("==Frequent itemsets (min_sup=%s%%)\n" % (min_supp * 100))
	sorted_large_itemsets_supp = sorted(large_itemsets_supp.items(), key=operator.itemgetter(1), reverse=True)
	for pair in sorted_large_itemsets_supp:
		itemset = list(pair[0])
		supp = pair[1]
		fo.write("%s, %s%%\n" % (itemset, (supp * 100))) 

	return large_itemsets_supp

def build_association_rules(large_itemsets_supp, itemset_freq, min_conf, fo):
	fo.write("\n==High-confidence association rules (min_conf=%s%%)\n" % (min_conf * 100))
	association_rules_conf = {}
	for itemset in large_itemsets_supp.keys():
		for r in range(1, len(itemset)):
			for subset in itertools.combinations(itemset, r):
				supp = large_itemsets_supp[itemset]
				conf = float(itemset_freq[itemset]) / itemset_freq[subset]
				if conf >= min_conf:
					rest = tuple(set(itemset) - set(subset))
					rule = (subset, rest, supp)
					association_rules_conf[rule] = conf
					#fo.write("%s => %s (Conf:%s%%, Supp: %s%%)\n" % (list(subset), list(left), conf * 100, supp * 100))
	sorted_association_rules_conf = sorted(association_rules_conf.items(), key=operator.itemgetter(1), reverse=True)
	for r in sorted_association_rules_conf:
		left = r[0][0]
		right = r[0][1]
		supp = r[0][2]
		conf = r[1]
		fo.write("%s => %s (Conf:%s%%, Supp: %s%%)\n" % (list(left), list(right), conf * 100, supp * 100))

if __name__ == "__main__":
	# Get command line arguments.
	csv_file= sys.argv[1]
	min_supp = float(sys.argv[2])
	min_conf = float(sys.argv[3])

	# Read transactions data from file.
	dataset = read_data(csv_file)

	itemset_freq = {}  # Record the occurences of each itemset, e.g. {("jacket"): 35}.
	fo = open(OUTPUT_FILE, 'w')

	# Find large itemsets by Apriori algorithm.
	large_itemsets_support = apriori_algorithm(dataset, min_supp, itemset_freq, fo)

	# Build association rules from large itemsets.
	build_association_rules(large_itemsets_support, itemset_freq, min_conf, fo)