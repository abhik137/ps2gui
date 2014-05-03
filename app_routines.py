#!/usr/bin/env python
import sys,os,sqlite3
import cookielib, urllib2
import re, shutil

initial_run=0

user_home = os.environ['HOME']
app_home = user_home + "/.ps2gui"
ps_info_file=app_home+"/psinfo"
db_file = app_home + "/station_info.db"

def migrate_database(old_db,new_db):
    print "Attempting to migrate the content of the old database to the new database"
    conn = sqlite3.connect(new_db)
    cono = sqlite3.connect(old_db)

    curn = conn.execute("SELECT COUNT(*) FROM info")
    curo = cono.execute("SELECT COUNT(*) FROM info")

    ## assuming PS stations increase with every revision. 
    if curn.fetchall()[0][0] == curo.fetchall()[0][0]:
        print "The number of station remain unchanged"
        print "DEBUG: The migration tool has completed basic checks and the database remains unchanged"
        os.remove(new_db)
        return False
    else:
        olddata = cono.execute("SELECT * FROM info").fetchall()
        cono.close()

        for tup in olddata:
            url = tup[3]
            pref = tup[4]
            notes = tup[5]

            conn.execute("UPDATE info SET pref=(?) where url=(?)", (pref,url))
            conn.execute("UPDATE info SET notes=(?) where url=(?)", (notes,url))
        conn.commit()
        conn.close()

        os.remove(db_file)
        os.rename(new_db,db_file)
        return True

def parse_and_write(raw_content,file_name):
    print "Parsing the data."
    urls=re.findall(r'href="(.*?)"', raw_content)
    rurls=[ a for a in urls if "problemBankStation" in a ]

    staloc = re.findall(r'href=".*?">(.*?)<',raw_content)[5:-1]
    stations=[]
    locations=[]

    for itera in staloc:
        stations.append(itera.split(",")[:-1] )
        locations.append(itera.split(",")[-1])

    finallist=[]

    with open(file_name,"w") as fp:
        for itera in xrange(len(stations) ):
            str="%s##%s##%s\n" % (stations[itera][0],locations[itera],rurls[itera])
            fp.write(str)

def export_prefs():
    conn = sqlite3.connect(db_file)
    raw_pref = conn.execute("select pref,sno+1 from info where pref != 0 order by pref asc").fetchall()

    exportfile = user_home + "/finalpreflist"

    if os.path.exists(exportfile):
        os.remove(exportfile)

    with open(exportfile,"w") as fp:
        for itera in xrange(0,len(raw_pref)):
            line ="%d %d\n" % (raw_pref[itera][0],raw_pref[itera][1])
            fp.write(line)


def validate_and_fetch():
    print "Trying to fetch the data."
    cj = cookielib.CookieJar()

    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    ## Use a graphical tool to present the username password dialog. Worst case use Zenity.
    commandoutput = os.popen("zenity --password --username","r").readline()
    if len(commandoutput.split('|')) != 2:
        print "Please provide the username and password"
        if initial_run:
            shutil.rmtree(app_home)
            sys.exit()
        if os.path.exists(app_home + "/tempdatabase.db"):
            os.remove(app_home + "/tempdatabase.db")
        sys.exit()

    username=commandoutput.split("|")[0].strip('\n')
    password=commandoutput.split("|")[1].strip('\n')
    #username=raw_input("Username:")
    #password = getpass.getpass()
    payload="uid=%s&pwd=%s" % (username,password)
    page = opener.open("http://www.bits-pilani.ac.in:12355/student_notice_login.asp", payload)
    page.close()

    page=opener.open("http://www.bits-pilani.ac.in:12355/problembankisem1415_Disp2.asp")
    website_raw_content=page.read()

    if "problemBankStation" not in website_raw_content:
        page.close()
        ## Here as well. 
        print "Username or Password wrong"
        return False
    else:
        page.close()
        if os.path.exists(ps_info_file):
            os.remove(ps_info_file)

        parse_and_write(website_raw_content,ps_info_file)
        return True

def populate_empty_database(databasefile):
    print "Trying to populate the core database"
    funcreturn = validate_and_fetch()

    if funcreturn:
        ## If this is true then the webpage has been downloaded and written in a convinient format to a text file.
        with open(ps_info_file,"r") as filep:
            global initial_run
            initial_run=0
            psinfocontent=filep.readlines()
            conn = sqlite3.connect(databasefile)
            counter=0
            for line in psinfocontent:
                tempcontent=line.split("##")
                name = tempcontent[0]
                location = tempcontent[1]
                url = tempcontent[2].strip('\n')
                pref=0
                notes=""
                conn.execute("insert into info values (?,?,?,?,?,?)", (counter,name,location,url,pref,notes,))
                counter=counter+1
            conn.commit()
            conn.close()
    else:
        if initial_run:
            shutil.rmtree(app_home)
        if os.path.exists(app_home + "/tempdatabase.db"):
            os.remove(app_home + "/tempdatabase.db")
        sys.exit()


def check_create_database(databasefile):
    if not os.path.exists(app_home):
        os.makedirs(app_home)
        global initial_run
        initial_run = 1

    if not os.path.exists(databasefile):
	   conn = sqlite3.connect(databasefile)
	   conn.execute('CREATE TABLE info(sno int,name text,location text, url text, pref int, notes text)')
	   conn.commit()
	   conn.close()
	   populate_empty_database(databasefile)

