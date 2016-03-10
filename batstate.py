#!/usr/bin/env python
import os
import time, datetime
import subprocess
import operator

# ps class runs ps -e, reads the TIME given and
# if run again after a certain amount of time,
# new TIME values are there. delta of TIME value
# equals actual CPU usage of that process during
# interval

class ps:
    def __init__(self):
        self.buffer = []
        self.buffer_max = 5
        self.path="/proc/"
        return

    def query_p(self,pid,parameter):
        fullpath = os.path.join(self.path,pid,parameter)
        if os.path.isfile(fullpath):
            f = file(fullpath,"r")
            d = f.read()
            f.close()
            d = d.strip()
            return d


    def parse_stat(self, stat):
        if not stat:
            return False
        tmp = stat.split(")")

        pre = tmp[0].split("(")

        pre_pid = int(pre[0].split()[0])
        pre_name = pre[1]

        fwd = tmp[1].split()

        #full = [pre_pid] + [pre_name] + fwd

        key_names = ["state","ppid","pgrp","session","tty","tpgid","flags","min_flt","cmin_flt","maj_flt","cmaj_flt","utime","stime","cutime","cstime","priority","nice","nlwp","alarm","start_time","vsize","rss","rss_rlim","start_code","end_code","start_stack","kstk_esp","kstk_eip","wchan","exit_signal","processor","rtprio","sched"]

        resultd = dict()
        for i in range(min(len(key_names),len(fwd))):
            k = key_names[i]
            v = fwd[i]
            try:
                v = int(v)
            except:
                #print "meh:("
                continue

            #print k+" = "+str(v)
            resultd[k] = v

        resultd["pid"] = pre_pid
        resultd["proc"] = pre_name

        return resultd
        
        
    def parse_stat_time(self, pstat):
        tmp = pstat

        if not tmp:
            return        
        try:
            return tmp["utime"]+tmp["stime"]+tmp["cutime"]+tmp["cstime"]
        except:
            return 0



    def query(self,pid):
        #print "PID = "+str(pid)
        stat = self.query_p(pid,"stat")

        if not stat:
            return False

        pstat = self.parse_stat(stat)

        t = self.parse_stat_time(pstat)
        cmdline = self.query_p(pid,"cmdline")

        pstat["time"] = t
        pstat["cmdline"] = cmdline

        #print pid, t, pstat["proc"]

        return pstat
        

    def alt_query_all(self):


        newlines = dict()


        
        l = os.listdir(os.path.join(self.path))
        for item in l:
            if item != "self":
                t = self.query(item)

                if t:
                    dataset = [t["time"], t["proc"]] # cmdline
                    newlines[t["pid"]] = dataset
        #return self.values


        now = datetime.datetime.now()
        timestamp = time.mktime(now.timetuple()) * 1000.0 + now.microsecond/1000.0

#        print timestamp
        

        dataset = [timestamp,newlines]

        self.buffer.append(dataset)

        # limit buffer to certain length
        if len(self.buffer)>self.buffer_max:
            self.buffer = self.buffer[-self.buffer_max:]

        return dataset




    def query_all(self):
        # 
        # run ps -e, split and store into dict 
        d = subprocess.check_output(["ps","-e"])

        dlines = d.split("\n")


        newlines = dict()
        for line in dlines[1:]: # skip header
            newline = line.split()
            if len(newline)>1:
                xpid = int(newline[0])
                xcmd = newline[-1]
                xtime = newline[2]

                xday = 0

                if "-" in xtime:
                    xday,xtime = xtime.split("-")

                xtime = xtime.split(":")
                xtime = int(xday)*(60*60*24) + int(xtime[0])*3600 + int(xtime[1])*60 + int(xtime[2])
                
                newlines[xpid] = [xtime,xcmd]


        now = datetime.datetime.now()
        timestamp = time.mktime(now.timetuple()) * 1000.0 + now.microsecond/1000.0

#        print timestamp


        dataset = [timestamp,newlines]

        self.buffer.append(dataset)

        # limit buffer to certain length
        if len(self.buffer)>self.buffer_max:
            self.buffer = self.buffer[-self.buffer_max:]

        return dataset



    def delta(self):
        if len(self.buffer)<2:
            print "not enough data"
            return # no data there, yet

        a = self.buffer[-1] # last one
        b = self.buffer[0] # first one

        a_time = a[0]
        b_time = b[0]

        a_pids = a[1].keys()
        b_pids = b[1].keys()

        deltas = []

        sum = 0

        for a_pid in a_pids:
            if not a_pid in b_pids:
                continue

            delta_time = a[1][a_pid][0] - b[1][a_pid][0]

            if delta_time>0:
                deltas+= [[ delta_time, a_pid, a[1][a_pid][1] ]]
                sum+=delta_time


        delta_time = a_time - b_time

        for line in deltas:
            line+=[1000.0*line[0]/delta_time]

#            print line, ("%3.1f"%(1000.0*line[0]/delta_time))

        print "CPU% total ", 1000.0*sum / delta_time

        deltas.sort(key=operator.itemgetter(-1), reverse=True)

        print "PID\tCPU%\tproc"
        for line in deltas:
            print "%i\t%3.1f\t%s"%(line[1],line[-1],line[2])
#            print line



    def prettyprint(self):
        print "-"*40
        self.delta()
    


class battery:
    def __init__(self,name="BAT0"):
        self.path="/sys/class/power_supply/"
        self.name=name
        self.values = dict()    

    
    def query_all(self):
        l = os.listdir(os.path.join(self.path,self.name))
        for item in l:
            self.query(item)
        return self.values

    def query(self,parameter):
        fullpath = os.path.join(self.path,self.name,parameter)
        if os.path.isfile(fullpath):
            f = file(fullpath,"r")
            d = f.read()
            f.close()
            d = d.strip()
            if not "\n" in d:
                self.values[parameter] = d.strip()
                return d
            else:
                return
        return

    def prettyprint(self):
        keys = list(self.values.keys())
        keys.sort()
        for k in keys:
            print "%s\t%s"%(k,self.values[k])

if __name__ == "__main__":
    b = battery()

    b.query_all()
    b.prettyprint()

    print "-"*40

    p = ps()


#    p.alt_query_all()
    #p.query("31733")


    for i in range(1,10):
        p.alt_query_all()
        time.sleep(3)
        #p.alt_query_all()
        p.prettyprint()

