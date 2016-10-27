import pandas as pd
import time
import json

from pycorenlp import StanfordCoreNLP

def processWikipediaData(fileName, standardWikiDoc, simpleWikiDoc):
	standardWiki = {}
	simpleWiki = {}
	standardContent  = []
	simpleContent = []
	with open(fileName) as f:
		for line in f:
			fields = line.split("\t")
			if fields[0] not in standardWiki:
				standardContent = []
				simpleContent = []
				standardContent.append(fields[1])
				simpleContent.append(fields[2])

				standardWiki[fields[0]] = standardContent
				simpleWiki[fields[0]] = simpleContent
			else:
				standardContent = standardWiki[fields[0]]
				simpleContent = simpleWiki[fields[0]]
				if fields[1] not in standardContent:
					standardContent.append(fields[1])
				if fields[2] not in simpleContent:
					simpleContent.append(fields[2])

				standardWiki[fields[0]] = standardContent
				simpleWiki[fields[0]] = simpleContent

	with open(standardWikiDoc,"w") as f1:
		with open(simpleWikiDoc,"w") as f2:
			f1.write("docName"+"\tsentence\n")
			f2.write("docName"+"\tsentence\n")
			for key, values in standardWiki.iteritems():
				standardSent  = values
				simpleSent = simpleWiki[key]
				for sent in standardSent:
					f1.write(key+"\t"+sent+"\n")	
				for sent in simpleSent:
					f2.write(key+"\t"+sent+"\n")			
		#print key,"\t\t Nb Standard Sentence:", len(values)," Nb Simple Sentence: ",len(simpleWiki[key])

def parseDoc(docFileName, outFileName):
	df = pd.read_csv(docFileName, sep="\t")
	df.columns = ["docName","sentence"]
	docNames = df.docName.unique()
	nlp = StanfordCoreNLP('http://localhost:9000')
	parseResults = {}
	nb_sent = 0
	for docName in docNames:
		sents = df[df['docName'] == docName]['sentence'].values
		start_time = time.time()
		#print "Number of sentences : ",len(sents)
		nb_sent = nb_sent + len(sents)
		output = {}
		docStr = ( ' '.join([str(x) for x in sents]))
		output = nlp.annotate(docStr, properties={'timeout': '100000000','annotators': 'tokenize,ssplit,pos,lemma,ner,depparse, parse,coref','outputFormat': 'json'})
		#parseResults[docName] = output
		#print output
		elapsed_time = time.time() - start_time	
		#print "Number of sentence: ",len(sents), "Number of coreference chains : ",len(output['sentences']), " Elapsed time: ",elapsed_time

	print nb_sent, "," , len(docNames)
	print nb_sent/(len(docNames) * 1.0)

	
	for docName, result in parseResults.iteritems():
		print docName,"\t number of coreference chains :", len(result['corefs'])

	with open(outFileName, "w") as json_file:
		json.dump(parseResults, json_file)
	
	#with open(docFileName) as f:
	#	nlp = StanfordCoreNLP('http://localhost:1337')


# Questions:
# Does Stanford parser split the sentences correctly e.g. mapping it to the correct sent in ?
# 


#processWikipediaData("/home/slouvan/Documents/Projects/ParallelExtraction/data/input/annotations.txt",
#					 "/home/slouvan/Documents/Projects/ParallelExtraction/data/input/standardWiki.txt",
#					 "/home/slouvan/Documents/Projects/ParallelExtraction/data/input/simpleWiki.txt")

parseDoc("/home/slouvan/Documents/Projects/ParallelExtraction/data/input/standardWiki.txt",
	     "/home/slouvan/Documents/Projects/ParallelExtraction/data/input/standardWikiParse.json")

#with open("/home/slouvan/Documents/Projects/ParallelExtraction/data/input/standardWiki.txt") as f:
#	for line in f:
#		print line.split("\t")[1].strip()