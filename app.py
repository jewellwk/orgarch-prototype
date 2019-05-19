from flask import Flask, request, render_template, redirect, url_for, flash
from simulate_data import Simulate
from config import Config
import time
import random
app = Flask(__name__)
app.config['SECRET_KEY']='tempconfig'

count = [0]
statsa = [0,0,0,0,0,0,0]
page_tablea = []
main_mema = []
cachea = []
tlba = []
tlboffseta = []
log_mema = {}
cache_hita = 0
cache_missa = 0
tlb_hita = 0
tlb_missa = 0
page_hita = 0
page_missa = 0
animationa = 0

@app.route('/')
@app.route('/about')
@app.route('/modules')
def index():	
	return render_template("base.html")
	
@app.route('/simulate', methods=['GET', 'POST'])	
def simulate():
	form = Simulate()
	stats = statsa
	page_table = page_tablea
	main_mem = main_mema
	cache = cachea
	tlb = tlba
	tlboffset = tlboffseta
	log_mem = log_mema
	
	if form.validate_on_submit():
		if request.form['button'] == 'Process':
			#take reference list and convert it into a list of int values
			reference_list = [i for i in request.form['data']]
			
			#builds a dictionary (won't repeat duplicate values) of the reference list to be stored into logical memory
			for i in range(len(reference_list)):
				log_mem.update({reference_list[i]:reference_list[i]})
				
			#build cache
			for i in range(4):
				cache.append(request.form['cache_'+str(i)])
			
			#build tlb 
			for i in range(2):
				tlb.append(request.form['tlb'+str(i)+'page'])
				tlboffset.append(request.form['tlb'+str(i)+'offset'])
				
			#build page table and main memory	
			for i in range(8):
				page_table.append(request.form['page'+str(i)+'frm'])
				main_mem.append(request.form['frame'+str(i)])
			
			#checks the radio button to the set frame replacement policy 
			reppol = 1 if request.form['reppol'] == 'LFU' else 2 if request.form['reppol'] == 'Belady' else 0
			
			#run simulation and calculate hits and misses
			stats = run(reference_list, cache, tlb, tlboffset, page_table, main_mem, reppol, count)
		elif request.form['button'] == 'Compare Algorithms':
			reference_list = [i for i in request.form['data']]
			if len(reference_list) <= 4:
				flash("Sorry, your list of page references is too short to utilize this feature. Please go back and add more pages.")
				return render_template("compalgs.html")
			else:
				fstats, rstats, bstats, bfaults, ffaults, rfaults = compare_algs(reference_list)
				return render_template("compalgs.html", fstats=fstats, rstats=rstats, bstats=bstats, ffaults=ffaults, bfaults=bfaults, rfaults=rfaults, reference_list=reference_list)
		
	return render_template("simulate.html", form=form, stats=stats, cache=cache, page_table=page_table, tlb=tlb, tlboffset=tlboffset, main_mem=main_mem, log_mem=log_mem)
	
def run(reference_list, cache, tlb, tlboffset, page_table, main_mem, reppol, count):
	cache_hit = cache_hita
	cache_miss = cache_missa
	tlb_hit = tlb_hita
	tlb_miss = tlb_missa
	page_hit = page_hita
	page_miss = page_missa
	animation = animationa

	#for i in range(len(reference_list)):
	i = count[0]
	count[0]+= 1
	if i < len(reference_list):
		
		page = reference_list[i]
		
		flash("Now processing page: "+page)

		#go to cache to see if value exists within cache
		if page in cache:
			flash("Page "+page+ " is already within the cache resulting in a cache hit.")
			cache_hit+=1
		#if not in cache check tlb
		elif page in tlb:
			flash("Page "+page+ " is not within the cache and has generated a cache miss. However, it is in within the TLB resuting in a TLB hit.")
			#if in TLB
			tlb_hit+=1
			cache_miss+=1
			
			#update cache
			update(reppol, reference_list, cache, page)
			flash("The cache has now been updated with page "+page)
			
			animation = 1
			#if not in tlb check full page table
		elif page in page_table:
			flash("Page "+page+ " is not within the TLB or the cache.")
			flash("It has generated a TLB and cache miss.")
			flash("The system must now check the entire page table.")
			flash('It is within the page table resuting in a page table hit.')
			#if in page table
			page_hit+=1
			tlb_miss+=1
			cache_miss+=1
			
			#update tlb
			updatetlb(i, tlb, tlboffset, page)
			flash("The TLB has now been updated with page "+page)
			
			#update cache
			update(reppol, reference_list, cache, page)
			flash("The cache has now been updated with page "+page)
			
			animation = 2
		else:
			flash("Page "+page+ " is not within the cache, TLB, or page table.")
			flash("The system needs to retrieve the page from logical memory and save it to the disk.")
			flash("Last, it must bring the page into main memory and update all components to resume execution.")
			page_miss+=1
			tlb_miss+=1
			cache_miss+=1
			
			#map to next available frame
			update(reppol, reference_list, main_mem, page)
			flash("Main memory has now been updated with page "+page)
				
			#update page table
			update(reppol, reference_list, page_table, page)
			flash("The page table has now been updated with page "+page)
			
			#update tlb
			updatetlb(i, tlb, tlboffset, page)
			flash("The TLB has now been updated with page "+page)
			
			#update cache
			update(reppol, reference_list, cache, page)
			flash("The cache has now been updated with page "+page)
			
			animation = 3
	else:
		count = [0]
		statsa = [0,0,0,0,0,0,0]
		page_tablea = []
		main_mema = []
		cachea = []
		tlba = []
		tlboffseta = []
		log_mema = {}
				
	return cache_hit, cache_miss, tlb_hit, tlb_miss, page_hit, page_miss, animation

def update(reppol, reference_list, array, page):
	if '' in array:
		update = array.index('')
		array[update]=page
	else:
		if reppol == 0:
			old = lru(reference_list, array, page)
			update = array.index(reference_list[old])
			array[update]=page
		elif reppol == 1:
			old = lfu(reference_list, array, page)
			update = array.index(str(old))
			array[update]=page
		else:
			old = belady(reference_list, array, page)
			update = array.index(str(old))
			array[update]=page
		
def updatetlb(count, tlb, tlboffset, page):
	if '' in tlb:
		update = tlb.index('')
		tlb[update]=page
		tlboffset[update] = update
	else:
		update = count%2
		tlb[update]=page
		tlboffset[update] = update
	
#look ahead and replace the frame that isn't going to be called within the next 3 references
def belady(reference_list, array, index):
	after = reference_list[int(index):]	
	for i in range(3):
		if i in array and i not in after:
			page = i
			break
	if page != None:
		return page
	else:
		return array[random.randint(0,3)]
			
#take a count of each entity within array and replace the frame that used the least
def lfu(reference_list, array, index): 
	before = reference_list[:int(index)]
	tally = {}
	for i in before:
		tally[i] = before.count(i)
	key_min = min(tally.keys(), key=(lambda k: tally[k]))
	return key_min

#check the prior frames and replace the one that was first used	
def lru(reference_list, array, index):
	current = reference_list.index(index)
	options = array[current - len(array):current]	
	unique = []
	for i in options:
		if i not in unique:
			unique.append(i)
	return unique[len(unique)-1]
	
def compare_algs(reference_list):
	bstats = []
	rstats = []
	fstats = []
	bfaults = 4
	ffaults = 4
	rfaults = 4
	bframes = [-1,-1,-1,-1]
	rframes = [-1,-1,-1,-1]
	fframes = [-1,-1,-1,-1]
	
	fstats.append(reference_list[0]+": page fault")
	fstats.append(reference_list[1]+": page fault")
	fstats.append(reference_list[2]+": page fault")
	fstats.append(reference_list[3]+": page fault")
	fframes[0] = reference_list[0]
	fframes[1] = reference_list[1]
	fframes[2] = reference_list[2]
	fframes[3] = reference_list[3]
	i = 4
	while i < len(reference_list):
		if reference_list[i] in fframes:
			fstats.append(reference_list[i])
		else:
			ffaults+=1
			#least frequently used
			fstats.append(reference_list[i]+": page fault")
			before = reference_list[i-4:i]
			tally = {}
			for a in before:
				tally[a] = before.count(a)
			key_min = min(tally.keys(), key=(lambda k: tally[k]))
			fframes[fframes.index(key_min)] = reference_list[i]
		i+=1
	
	rstats.append(reference_list[0]+": page fault")
	rstats.append(reference_list[1]+": page fault")
	rstats.append(reference_list[2]+": page fault")
	rstats.append(reference_list[3]+": page fault")
	rframes[0] = reference_list[0]
	rframes[1] = reference_list[1]
	rframes[2] = reference_list[2]
	rframes[3] = reference_list[3]
	i = 4
	while i < len(reference_list):
		if reference_list[i] in rframes:
			rstats.append(reference_list[i])
		else:
			rfaults+=1
			rstats.append(reference_list[i]+": page fault")
			#least recently used
			options = reference_list[:i]	
			unique = []
			for b in options:
				if b not in unique:
					unique.append(b)	
			rframes[rframes.index(unique[len(unique)-1])] = reference_list[i]
		i+=1
			
	bstats.append(reference_list[0]+": page fault")
	bstats.append(reference_list[1]+": page fault")
	bstats.append(reference_list[2]+": page fault")
	bstats.append(reference_list[3]+": page fault")
	bframes[0] = reference_list[0]
	bframes[1] = reference_list[1]
	bframes[2] = reference_list[2]
	bframes[3] = reference_list[3]
	i = 4
	while i < len(reference_list):
		if reference_list[i] in bframes:
			bstats.append(reference_list[i])
		else:
			bfaults+=1
			bstats.append(reference_list[i]+": page fault")
			#belady look ahead to the next 3 pages
			after = reference_list[i+1:]	
			for c in range(3):
				if c in bframes and c not in after:
					bframes[after.index(c)] = reference_list[i]
					break
				else:
					bframes[random.randint(0,3)] = reference_list[i]
		i+=1
					
	return fstats, rstats, bstats, bfaults, ffaults, rfaults