# "Database code" for the DB Log.

import datetime
import psycopg2

DBNAME = "news" 

def get_articles():
  """Return three articles from the 'database', most recent three."""
  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  state1 = "select substring(path,10,1000) as m, count(path) from log join articles on substring(path,10,1000) = articles.slug group by m order by count desc limit 3"
  c.execute(state1)
  return c.fetchall()
  
  db.close() 

def print_articles():
  """print the articles"""
  rows = get_articles()
  print "The three most popular essay:"
  with open('output.txt','w') as f: 
    f.write("The three most popular essay: \n")	 
    for row in rows:
      print("%25s, %6s" %(row[0],row[1]))
      f.write("%25s, %6s\n" % (str(row[0]), str(row[1])))	


def get_authors():
  """get the most view of authors. create view step1 
     step1: create view step1 as select substring(path, 10,1000) as m, count(path), name from articles
            join log on substring(path, 10, 1000)=articles.slug join authors on authors.id=author group
            by m, authors.name order by count desc"""

  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  state2 = "select step1.name, sum(count) from step1 join authors on step1.name = authors.name group by step1.name order by sum desc"
  c.execute(state2)
  #db.commit()
  rows = c.fetchall()
  print "The most popular authors:"
  with open('output.txt','a+') as f: 
    f.write("The most popular authors: \n")	 
    for row in rows:
      print("%25s, %6s" %(row[0],row[1]))
      f.write("%25s, %6s\n" % (str(row[0]), str(row[1])))	
  db.close()

def get_errors():
  """get the most errors > 0.01. create two views in database: date1, date2
     date1: create view date1 as select date(time), count(status) from log group by date(time)
     date2: create view date2 as select date(time), count(status) from log where status!='200 OK' group by date(time)"""
  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  state3 = "select date1.date, (cast(date2.count as float)/cast(date1.count as float)) as avg from date2 join date1 on date1.date = date2.date where (cast(date2.count as float))/cast(date1.count as float) > 0.01"
  c.execute(state3)
  rows = c.fetchall()
  print "The most popular errors > 0.01:"
  with open('output.txt','a+') as f: 
    f.write("The most errors > 0.01: \n")	 
    for row in rows:
      print("%25s, %6s" %(row[0],row[1]))
      f.write("%25s, %6s\n" % (str(row[0]), str(row[1])))	
  db.close()

#
print_articles()
get_authors()
get_errors()
