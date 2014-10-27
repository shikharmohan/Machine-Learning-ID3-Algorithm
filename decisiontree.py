import csv
import sys
import random
import math
#{'ParentAlum ': 'true ', 'GoodLetters ': 'true ', 'IsRich ': 'false ', 'HasScholarship ': 'false ', 'GoodGrades ': 'false ', 'GoodSAT ': 'true ', 'SchoolActivities': 'true ', 'CLASS': 'false'}
inputFileName = sys.argv[1]
trials = int(sys.argv[3])
verbose = int(sys.argv[4])
dictionary = []

with open(inputFileName, 'r') as SET:
  reader = csv.DictReader(SET, delimiter = '\t')
  for row in reader:
    rowDict = {}
    for key in row.keys():
      if row[key].strip() == "true":
        rowDict[key.strip()] = True
      else:
        rowDict[key.strip()] = False
    dictionary.append(rowDict)

def plog(p):
	if p == 0:
		return 0
	else:
	 return float(-p*math.log(p,2))

def entropy(examples, key):
	if not examples:
		return 0
	length = float(len(examples))
	numT = 0
	numF = 0
	for i in examples:
		if i[key] == True:
			numT += 1
		elif i[key] == False:
			numF += 1

	ptrue = numT/length
	pfalse = numF/length
	entropyT = plog(ptrue)
	entropyF = plog(pfalse)
	entropyTotal = entropyT + entropyF
	return entropyTotal

def gain (examples, target, attr):
	length = float(len(examples))
	numT = 0
	numF = 0
	trueEx = []
	falseEx = []
	for i in examples:
		if i[attr] == True:
			numT += 1
			trueEx.append(i)
		elif i[attr] == False:
			numF += 1
			falseEx.append(i)
	ptrue = numT/length
	pfalse = numF/length
	result = entropy(examples, target) - ptrue*entropy(trueEx, target) - pfalse*entropy(falseEx, target)
	return result



def best (examples, target, attributes):
	highest = 0
	ret = attributes[0]
	for a in attributes:
		curr = gain(examples, target, a) 
		if curr > highest:
			ret = a
			highest = curr
	return ret


class Node:
	parent = 'root'
	value = -1
	attr = -1
	tChild = None
	fChild = None

def mostCommonValue(target, examples):
	t = 0
	f = 0
	for i in examples:
		if i[target] == True:
			t += 1
		else:
			f += 1
	if t>=f:
		return 1
	elif f > t:
		return 0


def id3(tset, target, attributes):
	#Create a Root node for the tree
	root = Node()
	pos = True
	neg = True
	for e in tset:
		if e['CLASS'] == False:
			pos = False
		if e['CLASS'] == True:
			neg = False
	#If all Examples are positive, Return the single-node tree Root, with label = +
	if pos:
		root.value = 1
		return root
	#I f all Examples are positive, Return the single-node tree Root, with label = -
	if neg:
		root.value = 0
		return root
	#If Attributes is empty, Return the single-node tree Root, with label = most common value of Targetattribute in Examples
	if not attributes:
		root.value = mostCommonValue(target, tset)
		return root
	else:
		bestAttr = best(tset, target, attributes)
		root.attr = bestAttr


		trueAttrEx = []
		falseAttrEx = []


		for i in tset:
			if i[bestAttr] == True:
				trueAttrEx.append(i)
			else:
				falseAttrEx.append(i)

		attributes.remove(bestAttr)
		
		if not trueAttrEx:
			tempnode = Node()
			tempnode.parent = bestAttr
			tempnode.value = mostCommonValue(target, tset)
			root.tChild = tempnode
		else:
			tempnode = id3(trueAttrEx, target, attributes)
			tempnode.parent = bestAttr
			root.tChild = tempnode
		if not falseAttrEx:
			tempnode = Node()
			tempnode.parent = bestAttr
			tempnode.value = mostCommonValue(target, tset)
			root.fChild = tempnode
		else:
			tempnode = id3(falseAttrEx, target, attributes)
			tempnode.parent = bestAttr
			root.fChild = tempnode
		return root

def correct (root, example):
	if root.value == 1:
		ret = True
	elif root.value == 0:
		ret = False
	else:
		if example[root.attr] == True:
			ret = correct(root.tChild, example)
		else:
			ret = correct(root.fChild, example)
	return ret

def printTree(rr):
	if rr.value == 0:
		print " parent: ", rr.parent, "- "
	elif rr.value == 1:
		print " parent: ", rr.parent, '+'
	elif rr:
		if not rr.tChild or rr.tChild.attr == -1:
			tC = 'leaf'
		else:
			tC = rr.tChild.attr
		if not rr.fChild or rr.fChild.attr == -1:
			fC = 'leaf'
		else:
			fC = rr.fChild.attr

		print " parent: ", rr.parent, "Attribute: ", rr.attr, " trueChild: ", tC, " falseChild: ", fC
	if rr.tChild:
		printTree(rr.tChild)
	if rr.fChild:
		printTree(rr.fChild)

meanId3 = 0
meanPrior = 0

#Run Program
for i in range(0, trials):
	print "----------------------------"
	print "DECISION TREE TRIAL ", i 
	print "----------------------------"

	trainingSetSize = int(sys.argv[2])
	random.shuffle(dictionary)
	trainSet = dictionary[0:trainingSetSize]
	testSet = dictionary[trainingSetSize:]

	positive = 0

	for i in trainSet:
		if i['CLASS'] == True:
			positive += 1

	pClassPos = positive/float(trainingSetSize)
	pClassNeg = (trainingSetSize - positive)/float(trainingSetSize)


	if pClassNeg > pClassPos:
		prior = 0
	else:
		prior = 1


	attr = dictionary[0].keys()
	attr.remove('CLASS')

	r = id3(trainSet, 'CLASS', attr)

	total = len(testSet)
	numCorrect = 0
	numCorrectPrior = 0

	if verbose == 1:
		print "VERBOSE OUTPUT:"
		print "Training Set Examples"
		for i in trainSet:
			print i

	if prior == 1:
		p = 'True'
	else:
		p = 'False'
	for i in range(0,total):
		if verbose == 1:
			print "----------"
			print "Test Example ", i
			print testSet[i]
			print "Actual: ", testSet[i]['CLASS'], " Tree result: ", correct(r, testSet[i]), " Prior Result: ", p
			print "----------"
		numCorrect = numCorrect + (correct(r, testSet[i]) == testSet[i]['CLASS'])
		numCorrectPrior = numCorrectPrior + (prior == testSet[i]['CLASS'])

	numcorrectpercent = (numCorrect/float(total))*100
	meanId3+= numcorrectpercent
	numcprior = (numCorrectPrior/float(total))*100
	meanPrior+= numcprior
	printTree(r)
	print "Percent ID3 Correctness: ", numcorrectpercent, "%"
	print "Percent Prior Correctness: ", numcprior, "%"


print "example file used = ", inputFileName
print "number of trials = ", trials
print "training set size for each trial = ", trainingSetSize
print "testing set size for each trial = ", len(testSet)
print "mean performance of decision tree over all trials = ",meanId3/trials ,"correct classification"
print "mean performance of using prior probability derived from the training set = ", meanPrior/trials, "correct classification"































