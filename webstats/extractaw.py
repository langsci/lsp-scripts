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


class Book():
  def __init__(self, ID, title, colors, shapes):
    seed = hash(ID)
    self.ID = int(ID)
    self.title = title 
    self.downloads = {}
    #colors and shapes for lines should be identical for 
    #a book across several graphics, but different for 
    #different books. Use a hash function to assign colors
    #and shapes
    self.color = colors[seed%len(colors)]
    self.shape = shapes[seed%len(shapes)]
        
  
  def getGraph(self,timeframe=-1):
    pass
  

  def getYAggregates(self,labels,threshold):    
    basis = [self.downloads.get(label,0) for label in labels]
    aggregate = [sum(basis[0:i+1]) for i,el in enumerate(basis)]
    aggregate = [(a if a>threshold else 0) for a in aggregate]    
    return aggregate
  
  def zeros2nones(self,a):
    result = []
    for i,e in enumerate(a):
      try:
        if a[i+1]==0:
          result.append(None)
        else:
          result.append(e)
      except IndexError:
          result.append(e)
    return result
          
          
      
  
class Catalog():
  def __init__(self, booksfile='books.tsv'):
    #read ID and title of books from file
    lines = open(booksfile).read().decode('utf8').split('\n') 
    print lines
    #put ID as key and title as value in dictionary
    #self.books = dict([l.strip().split('\t') for l in lines if l.strip()!='']) 
    #setup colors and shapes to select from
    colors = plt.cm.Set1(np.linspace(0, 1, 45)) 
    #colors = 'bgrcmyk'
    shapes = 'v^osp*D'    
    self.books = {} 
    for l in lines:
      if l.strip()!='':
        ID, title = l.strip().split('\t') 
        ID = int(ID)
        self.books[ID] = Book(ID, title, colors, shapes)
    #collect all directories with access information
    self.dirs = glob.glob('webreport_langsci-press.org_catalog_20[0-9][0-9]_[01][0-9]')
    #extract access data from all log files
    self.monthstats = dict([(d[-7:], Stats(os.path.join(d,'awstats.langsci-press.org.urldetail.html')).getBooks()) for d in self.dirs]) 
    aggregationdictionary = {}
    for bID in self.books:
      aggregationdictionary[int(bID)] = {}   
    print aggregationdictionary
    for month in self.monthstats: 
      for book in self.monthstats[month]:
        if int(book) in self.books:
          try:
            aggregationdictionary[book][month] = self.monthstats[month][book]
          except KeyError:          
            aggregationdictionary[book][month] = 0        
    for bookID in aggregationdictionary:
      self.books[bookID].downloads = aggregationdictionary[bookID]
    
    self.countrystats = dict([(d[-7:],CountryStats(os.path.join(d,'awstats.langsci-press.org.alldomains.html')).getCountries()) for d in self.dirs]) 
    #print self.countrystats
  
  #def plotall(self): 
    #for month in self.monthstats: 
      #for book in self.monthstats[month]:
	#self.plot(book, self.monthstats[month][book]) 
         
        
  def plotaggregate(self):
    """ compute totals for books and print out """
    
    aggregationdictionary = {}    
    for month in self.monthstats: 
      for book in self.monthstats[month]:
        try:
          aggregationdictionary[book] += self.monthstats[month][book]
        except KeyError:
          aggregationdictionary[book] = self.monthstats[month][book]
    for book in aggregationdictionary:
      self.plot(book, aggregationdictionary[book])

  def plotcumulative(self):
    """ compute totals for books per month and print out """
    
    aggregationdictionary = {}
    for month in sorted(self.monthstats):
      print ''
      print month
      print 30*'='
      for book in sorted(self.monthstats[month]):
        try:
          aggregationdictionary[book] += self.monthstats[month][book]
        except KeyError:
          aggregationdictionary[book] = self.monthstats[month][book]
        self.plot(book, aggregationdictionary[book]) 


  def plot(self,book,hits):
    """print to standard out"""
    
    print hits, hits/20*'|', self.books[str(book)]
    
    
  def matplotcumulative(self,ID=False, legend=True, fontsizetotal=15, threshold=99):
    """
    produce cumulative graph
    
    Aggregate cumulative data for time sequence.
    Plot this data with matplotlib.
    """
    
    #sort the keys so we get them in temporal order
    labels = sorted(self.monthstats.keys())
    
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
    timeframe = 11 #how many months should be displayed?f
    
    #store data to plot here so we can sort before plotting
    plots = []
    aggregatedownloads = 0
    for bookID in self.books:
      print bookID
      if ID and bookID!=ID:
	#print 'skipping', repr(ID), repr(book)
	continue
      print bookID,':',
      #initialize axes      
      x = range(len(labels)+1)
      #update values for axes
      y = self.books[bookID].getYAggregates(labels,threshold)     
      print y
      #store plot data for future usage
      plots.append([x,y,self.books[bookID]])   
      try:
        aggregatedownloads +=  y[-2]
      except TypeError:
        pass
    if ID==False:
      print "total downloads of all books", aggregatedownloads
    #sort plot data according to lowest total downloads
    #Then plot the plots
    n = 0	
    displaylimit = timeframe
    origlabels = labels
    for plot in sorted(plots, key=lambda k: k[1][-2],reverse=True): 
      #print plot
      if plot[1][-2]<30: #make sure no test or bogus data are displayed
        continue
      #print labels
      n = 0   
      if ID!=False: 
        for t in y:#calculate number of None fields and restrict output to non-None values and the preceding value
          if t==None:
            n += 1
        plot[0] = plot[0][n-1:]
        plot[1] = plot[1][n-1:]
        labels = labels[n:] 
      #plot line
      xs = plot[0][-timeframe-1:] + [None]
      ys = plot[1][-timeframe-1:] + [None]
      color = plot[2].color
      shape = plot[2].shape
      totaldownloads = ys[-2]
      ax.plot(xs, ys, color=color, linewidth=1.5) 
      #plot marks
      ax.plot(xs, ys, shape, color=color, label="%s (%s)" % (plot[2].title, ys[-2])) 
      ax.text(len(origlabels)-1, totaldownloads, '      %s'%totaldownloads, fontsize=fontsizetotal) 
      if timeframe > len(xs)-n :
        displaylimit = len(xs)-n    

    #plot x-axis labels
    plt.xticks(x[-timeframe:][n:], [l[-5:].replace('_','/') for l in labels[-timeframe+1:]], fontsize = 10) 
    #plt.xticks(xs[-displaylimit-1:], [l[-5:].replace('_','/') for l in labels[-displaylimit-1:]], fontsize = 10) 
    #position legend box
    if legend:
      box = ax.get_position()
      ax.set_position([box.x0, box.y0, box.width * 0.66, box.height]) 
      ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False,numpoints=1) 
    #else:
      #ax.legend_.remove()
    #save file
    if ID:
      plt.savefig('%s.svg'%ID)
      plt.savefig('%s.png'%ID)
    else:
      plt.savefig('cumulativeall.svg')
      plt.savefig('cumulativeall.png')
    plt.close(fig)
   
  def plotCountries(self,threshold=12):
    """
    Produce a pie chart of downloads per country.
    $threshold countries will be named, the rest
    will be aggregated as "other"
    """
    
    aggregationdictionary = {}
    for month in self.countrystats:
      monthdictionary = self.countrystats[month]
      for country in monthdictionary:
        try:
          aggregationdictionary[country] += int(monthdictionary[country].replace(',',''))
        except KeyError:
          aggregationdictionary[country] = int(monthdictionary[country].replace(',',''))
          
    for k in aggregationdictionary:
      print k, aggregationdictionary[k]
    #get list of countries and downloads
    list_ = [(k,aggregationdictionary[k]) for k in aggregationdictionary]        
    #sort list by number of downloads
    list_.sort(key=lambda x: x[1], reverse=True) 
    #compute values for named countries and "other"
    values = [t[1] for t in list_][:threshold]+[sum([t[1] for t in list_][threshold:])]  
    #set labels for named countries and "other"
    labels = ['%s: %s'%t for t in list_][:threshold]+['Other:%s'%values[-1]]
    #for i in range(threshold+1,len(labels)):
      #labels[i]=''
    print labels, values
    cmap = plt.get_cmap('Paired')
    colors = [cmap(i) for i in np.linspace(0, 1, threshold+1)]
    #setup matplot 
    fig = plt.figure()
    plt.axis("equal") 
    fig.set_figwidth(12)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.66, box.height]) 
    plt.pie(values, labels=labels, colors=colors, labeldistance=1.4)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False,numpoints=1) 
    plt.savefig('countries.png') 
    plt.savefig('countries.svg') 
	  
      
     
    
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
                        ) 
                        for tr in BeautifulSoup.BeautifulSoup(open(f))\
                                              .find('table',attrs={'class':'aws_data'})\
                                              .findAll('tr')[1:]
                      ]
                  )    


    
  def getBooks(self):
    """
    analyze the access data and aggregate stats for books across publication formats
    """
    
    aggregationdictionary = {}
    for k in self.hits:
      if 'view' in k: #ignore /download/, which is used for files other than pdf
        i=0
        try:
          #extract ID
          i = int(re.search('view/([0-9]+)',k).groups()[0])
        except AttributeError:
          print "no valid book key in %s" %k
          continue
        try:
          #accumulate figures for the various publication formats
          aggregationdictionary[i] += self.hits[k]
        except KeyError:
          aggregationdictionary[i] = self.hits[k]
    return aggregationdictionary
    
        
  def getCountries(self):
    """
    analyze the access data and aggregate stats for countries
    """
    
    aggregationdictionary = {}
    for k in self.hits: 
      try:
        #accumulate figures for the various publication formats
        aggregationdictionary[k] += self.hits[k]
      except KeyError:
        aggregationdictionary[k] = self.hits[k] 
    return aggregationdictionary
   
class CountryStats(Stats):
  def __init__(self,f):
    """
    navigate the html file to find the relevant <td>s and
    create a dictionary mapping urls to download figures
    """		  
    self.hits = dict(
                    [
                      (
                        #locate key
                        tr.findAll('td')[2].text,
                        #remove thousands separator and convert value to int
                        tr.findAll('td')[4].text
                      ) 
                      for tr in BeautifulSoup.BeautifulSoup(open(f))\
                                              .find('table',attrs={'class':'aws_data'})\
                                              .findAll('tr')[1:]
                    ]
                    )  

                    
if __name__=='__main__':
  c = Catalog()
  #print "country plot"
  #c.plotCountries(threshold=13)
  #print 30*'-'
  #print "global plot"
  c.matplotcumulative(fontsizetotal=7) 
  #print 30*'-'
  #print "individual plots"
  #for bookID in c.books: 
    #c.matplotcumulative(ID=bookID, legend=False)
    