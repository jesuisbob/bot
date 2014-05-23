#!/usr/bin/python2

import socket
import time
import string
import re
from select import select
import sys
import curses

VERSION = "PythonBot: 0.1 powered by Snorky"

numeric_events = {"001": "welcome","002": "yourhost","003": "created","004": "myinfo","005": "featurelist","200": "tracelink","201": "traceconnecting","202": "tracehandshake","203": "traceunknown","204": "traceoperator","205": "traceuser","206": "traceserver","207": "traceservice","208": "tracenewtype","209": "traceclass","210": "tracereconnect","211": "statslinkinfo","212": "statscommands","213": "statscline","214": "statsnline","215": "statsiline","216": "statskline","217": "statsqline","218": "statsyline","219": "endofstats","221": "umodeis","231": "serviceinfo","232": "endofservices","233": "service","234": "servlist","235": "servlistend","241": "statslline","242": "statsuptime","243": "statsoline","244": "statshline","250": "luserconns","251": "luserclient","252": "luserop","253": "luserunknown","254": "luserchannels","255": "luserme","256": "adminme","257": "adminloc1","258": "adminloc2","259": "adminemail","261": "tracelog","262": "endoftrace","263": "tryagain","265": "n_local","266": "n_global",
"300": "none","301": "away","302": "userhost","303": "ison","305": "unaway","306": "nowaway","311": "whoisuser","312": "whoisserver","313": "whoisoperator","314": "whowasuser","315": "endofwho","316": "whoischanop","317": "whoisidle","318": "endofwhois","319": "whoischannels","321": "liststart","322": "list","323": "listend","324": "channelmodeis","329": "channelcreate","331": "notopic","332": "currenttopic","333": "topicinfo","341": "inviting","342": "summoning","346": "invitelist","347": "endofinvitelist","348": "exceptlist","349": "endofexceptlist","351": "version","352": "whoreply","353": "namreply","361": "killdone","362": "closing","363": "closeend","364": "links","365": "endoflinks","366": "endofnames","367": "banlist","368": "endofbanlist","369": "endofwhowas","371": "info","372": "motd","373": "infostart","374": "endofinfo","375": "motdstart","376": "endofmotd","377": "motd2","381": "youreoper","382": "rehashing","384": "myportis","391": "time","392": "usersstart","393": "users","394": "endofusers","395": "nousers",
"401": "nosuchnick","402": "nosuchserver","403": "nosuchchannel","404": "cannotsendtochan","405": "toomanychannels","406": "wasnosuchnick","407": "toomanytargets","409": "noorigin","411": "norecipient","412": "notexttosend","413": "notoplevel","414": "wildtoplevel","421": "unknowncommand","422": "nomotd","423": "noadmininfo","424": "fileerror","431": "nonicknamegiven","432": "erroneusnickname","433": "nicknameinuse","436": "nickcollision","437": "unavailresource","441": "usernotinchannel","442": "notonchannel","443": "useronchannel","444": "nologin","445": "summondisabled","446": "usersdisabled","451": "notregistered","461": "needmoreparams","462": "alreadyregistered","463": "nopermforhost","464": "passwdmismatch","465": "yourebannedcreep","466": "youwillbebanned","467": "keyset","471": "channelisfull","472": "unknownmode","473": "inviteonlychan","474": "bannedfromchan","475": "badchannelkey","476": "badchanmask","477": "nochanmodes","478": "banlistfull","481": "noprivileges","482": "chanoprivsneeded","483": "cantkillserver","484": "restricted","485": "uniqopprivsneeded","491": "nooperhost","492": "noservicehost",
"501": "umodeunknownflag","502": "usersdontmatch",}


DEBUG = False


LIST=["!help", "!quit", "!conn"]


def init_conn(channel, nickname, server, port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((server, port))
    return s

def send_data(s, msg):
    msg = msg + "\r\n"
    s.send(msg)

def ping(s, msg):
    send_data(s, "PONG %s" % msg)

def conn(s, channel, nickname, host):
    ident = "aa"
    realname = "bb"
    #Send data for connection
    send_data(s, "NICK %s" % nickname)
    send_data(s, "USER %s %s oxy :%s" % (ident, host, realname))
    #Waiting 
    time.sleep(2)
    #Join the channel
    send_data(s, "JOIN %s" % channel)

def cctp(s, line):
    nick, msg_type, chan = info(line)
    if (re.findall(ur"^.+VERSION.+$", line[3])):
        #[':Snorky!Silentd@snorky', 'PRIVMSG', 'Oxy', ':\x01VERSION\x01'] 
        send_data(s, (("NOTICE %s \001VERSION %s\001")% (nick, VERSION)))
    else:
        send_data(s, (("NOTICE %s \001THE_GAME %s\001")% (nick, "www.tukif.com")))

def info(line):
    nick = line[0].split("!")[0][1:]
    msg_type = line[1]
    channel = line[2]
    return nick, msg_type, channel

def welcome(s, channel, name):
    send_data(s, "PRIVMSG %s Bonjour %s !!!" % (channel, name))

def menu(s, channel):
    for cmd in LIST:
        send_data(s, ("PRIVMSG %s %s" % (channel, cmd)))
        time.sleep(0.2)

def display(win, data):
    win.move(0,0)
    win.deleteln()
    win.addstr(47,1, data)
    win.move(48,1)
    win.refresh()

def do_command(s, line, connected, channel, win):
    #[':Snorky!Silentd@snorky', 'PRIVMSG', '#Snorky_land', ':zz']
    #:Snorky!Silentd@snorky PRIVMSG #Snorky_land :zz
    #[':Snorky!Silentd@snorky', 'JOIN', ':#bot']
    regex = ur"^:\x01.+\x01$"
    victim = line[0].split("!")[0][1:] 
    
    try:
        if (connected == 0):
            display(win, (' '.join(map(str, line))))
            if (line[1] == "JOIN"):
                connected = 1
        elif(line[1] == "JOIN"):
            welcome(s, channel, victim)
        #CTCP VERSION
        elif (re.findall(regex, line[3])):
            pass
            #    cctp(s, line)
        #Menu
        elif (line[3]==":!menu"):
            menu(s, channel)
        #Chanserv Notification
        elif(victim == "ChanServ"):
            pass
            #print line
        else:
            data = line[0].split("!")[0][1:] + "\t| " + ' '.join(line[3:])[1:]
            display(win,data)
            #print line[0].split("!")[0][1:], "\t| ", ' '.join(line[3:])[1:]
    except:
        win.addstr(0,0,"Fail!")
    
    #time.sleep(4)
    return connected

def master(s, channel, nickname, server, port):
    readbuffer = ""
    connected = 0
    stdscr = curses.initscr()
    win = curses.newwin(50, 150, 0, 0)

    while True:
        read, _, _ = select([s], [],[], 0.1)
        if read:
            readbuffer=readbuffer+s.recv(512)
            temp=string.split(readbuffer, "\n")
            readbuffer=temp.pop( )
        
            for line in temp:
                line=string.rstrip(line)
                line=string.split(line)
                if(line[0]=="PING"):
                    ping(s, line[1])
                else :
                    connected = do_command(s, line, connected, channel, win)
        
        console, _, _ = select([sys.stdin], [],[], 0.1)
        
        if console:
            try:
                
                data = win.getstr(48,1)
                #data = sys.stdin.readline()
                tmp = data.split()

                if data == '!quit':
                    send_data(s, "QUIT The Game Bitch")
                    curses.endwin()
                    break
                if(tmp[0] == "/who"):
                    send_data(s,data[1:])
                elif(tmp[0] == "/nick"):
                    send_data(s,data[1:])
                else:
                    send_data(s,"PRIVMSG %s %s" % (channel,data))
                display(win, data)
            except:
                pass
    curses.endwin()

def main():
    import sys
    if len(sys.argv) != 4:
        print "Usage: testbot <server[:port]> <channel> <nickname>"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    s = init_conn(channel, nickname, server, port)
    conn(s, channel, nickname, server)

    master(s, channel, nickname, server, port)


if __name__ == "__main__":
    main()
