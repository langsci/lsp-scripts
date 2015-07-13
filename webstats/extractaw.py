import glob
import re 
import os
import BeautifulSoup
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors

  
class Catalog():
  def __init__(self, books='books.tsv'):
    #read ID and title of books from file
    self.books = dict([l.strip().split('\t') for l in open(books).read().decode('iso-8859-1').split('\n')]) 
    #collect all directories with access information
    self.dirs = glob.glob('webreport_langsci-press.org_catalog_20[0-9][0-9]_[01][0-9]')
    #extract access data from all log files
    self.monthstats = dict([(d[-7:],Stats(os.path.join(d,'awstats.langsci-press.org.urldetail.html')).getBooks()) for d in self.dirs]) 
  
  def plotall(self): 
    for month in self.monthstats: 
      for book in self.monthstats[month]:
	self.plot(book, self.monthstats[month][book]) 
	
  def plotaggregate(self):
    """ compute totals for books and print out """
    
    d = {}    
    for month in self.monthstats: 
      for book in self.monthstats[month]:
	try:
	  d[book] += self.monthstats[month][book]
	except KeyError:
	  d[book] = self.monthstats[month][book]
    for book in d:
	self.plot(book, d[book])
	
  def plotcumulative(self):
    """ compute totals for books per month and print out """
    
    d = {}
    for month in sorted(self.monthstats):
      print ''
      print month
      print 30*'='
      for book in sorted(self.monthstats[month]):
	try:
	  d[book] += self.monthstats[month][book]
	except KeyError:
	  d[book] = self.monthstats[month][book]
	self.plot(book, d[book]) 
	
  def plot(self,book,hits):
    """print to standard out"""
    
    print hits, hits/20*'|', self.books[str(book)]
    
  def matplotcumulative(self,ID=False):
    """
    produce cumulative graph
    
    Aggregate cumulative data for time sequence.
    Plot this data with matplotlib.
    """
    
    #sort the keys so we get them in temporal order
    labels = sorted(self.monthstats.keys())
    print labels
    
    #setup matplot 
    fig = plt.figure()
    #use a wide picture
    fig.set_figwidth(12)
    ax = plt.subplot(111)
    #fig.add_subplot(ax)
     
    plt.rc('legend',**{'fontsize':9}) 
    #fig.patch.set_visible(False)
    #ax.axis('off')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_ylabel('downloads')
    ax.set_xlabel('months')   
    #setup colors and shapes to select from
    colors = plt.cm.Set1(np.linspace(0, 1, 45))
    print colors
    #colors = 'bgrcmyk'
    shapes = 'v^osp*D'
    
    #store data to plot here so we can sort before plotting
    plots = []
    for book in self.books:
      if ID and book!=str(ID):
	print 'skipping', repr(ID), repr(book)
	continue
      print book,':',
      tmp = 0 
      #initialize axes
      x = range(len(labels)+1)
      y = [None for i in range(len(labels)+1)]
      #update values for axes
      for i,month in enumerate(labels):	 
	try:
	  y[i] = tmp+self.monthstats[month][int(book)]
	  tmp = y[i]
	except KeyError:#no downloads this month
	  y[i] = tmp
      #print y  
      for i,j in enumerate(y):
	if i == 0:
	  continue
	if y[i]!=None and y[i]<70:
	  y[i-1]=None
      print y
      #colors and shapes for lines should be identical for 
      #a book across several graphics, but different for 
      #different books. Use a hash function to assign colors
      #and shapes
      seed = hash(book)
      c = colors[seed%len(colors)]
      s = shapes[seed%len(shapes)]
      #store plot data for future usage
      plots.append([x,y,c,s,self.books[book]]) 
    #sort plot data according to highest total downloads
    #Then plot the plots
    for plot in sorted(plots, key=lambda k: k[1][-2],reverse=True): 
      #print plot
      if plot[1][-2]<30: #make sure no test or bogus data are displayed
	continue
      #print labels
      if ID!=False:
	n = 0	
	for t in y:
	  if t==None:
	    n += 1
	plot[0] = plot[0][n:]
	plot[1] = plot[1][n:]
	labels = labels[n:]
      print len(plot[0]),len(plot[1]),len(labels)
      print plot
      #plot line
      ax.plot(plot[0],plot[1] ,color=plot[2],linewidth=1.5)
      #plot marks
      ax.plot(plot[0],plot[1],plot[3],color=plot[2],label=plot[4])
      ax.text(len(labels)-1, plot[1][-2], '  %s'%plot[1][-2], fontsize=7) 
    #plot x-axis labels
    plt.xticks(x, [l[-5:].replace('_','/') for l in labels], fontsize = 10) 
    #position legend box
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.66, box.height]) 
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False,numpoints=1) 
    #save file
    if ID:
      plt.savefig('cumulative%s.png'%ID)
    else:
      plt.savefig('cumulativeall.png')
    
	
	  
      
       
    
class Stats():
  def __init__(self,f):
    """
    navigate the html file to find the relevant <td>s and
    create a dictionary mapping urls to download figures
    """
    
    self.hits = dict(
		      [
			(
			  #locate key
			  tr.findAll('td')[0].text,
			  #remove thousands separator and convert value to int
			  int(tr.findAll('td')[1].text.replace(',',''))
			) for tr in BeautifulSoup.BeautifulSoup(open(f))\
				  .find('table',attrs={'class':'aws_data'})\
				  .findAll('tr')[1:]
		      ]
		  )
    
  def getBooks(self):
    """
    analyze the access data and aggregate stats for books across publication formats
    """
    
    d = {}
    for k in self.hits:
      if 'view' in k: #ignore /download/, which is used for files other than pdf
	try:
	  #extract ID
	  i = int(re.search('view/([0-9]+)',k).groups()[0])
	except AttributeError:
	  print "no valid book key in %s" %k
	  continue
	try:
	  #accumulate figures for the various publication formats
	  d[i] += self.hits[k]
	except KeyError:
	  d[i] = self.hits[k]
    return d
    
if __name__=='__main__':
  c = Catalog()
  c.matplotcumulative() 
  #for b in c.books: 
    #c.matplotcumulative(ID=b)
	