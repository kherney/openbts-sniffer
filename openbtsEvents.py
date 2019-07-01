from argparse import ArgumentParser

class GSMtools():

    def str_tmsi(self, tmsi):
        if tmsi != "":
			new_tmsi="0x"
			for a in tmsi:
				c=hex(ord(a))
				if len(c)==4:
					new_tmsi+=str(c[2])+str(c[3])
				else:
					new_tmsi+="0"+str(c[2])
			return new_tmsi
        else:
            return None

    def str_imsi(self,imsi):
        new_imsi=""
        temp=""
        if imsi != "":
            for c in range(len(imsi)):
                if c != 0:
                    temp=str(hex(ord(imsi[c])))[2:].zfill(2)
                    new_imsi += temp[1]+temp[0]
                else :
                    temp=str(hex(ord(imsi[c])))[2:].zfill(2)
                    new_imsi += temp[0]
            return new_imsi
        else:
            return None
    def toNumber(self,object):
        number="0x"
        for c in object:
            c=hex(ord(c))
            if len(c)==3:
                c="0x0"+c[2:]
            number += c[2:]
        return int(number,16)

    def showHexdump(self,object):
        object = [hex(ord(object[i])) for i in range(len(object))]
        print len(object)
        row=float(len(object)/16.0)
        if round(row)< row:
            row=round(row) +1
        elif round(row)>row:
            row=round(row)
        else:
            row =row

        for i in range(int(row)):
            p=[""]*16
            if row == i+1:
                p[:len(object)-(i)*16]=object[i*16:(i+1)*16]
            else:
                p = object[i*16:(i+1)*16]
            print "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                   p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],
                   p[9],p[10],p[11],p[12],p[13],p[14],p[15])

    def getIsdn(self,object):
        NumeroSource = ""
        Sourceln= ord(object[0x0c])%2
        if not Sourceln :
            Sourceln = ord(object[0x0c])/2.0
        else :
            Sourceln = round(ord(object[0x0c])/2.0)
        for k in object[0x0e:][:int(Sourceln)]:
            k = str(hex(ord(k)))[2:].zfill(2)
            NumeroSource += k[1]+k[0]
        return NumeroSource

    def isReady(self,*argv):
        return not bool("" in argv or None in argv)

class SDCCH4(GSMtools):
    def __init__(self):
        self.flags = True
        self.frame = 0
        self.ARFCN = 0
        self.sms = {"frag":[],"RP":[]}
        self.isdnSource = ""
        self.mensaje = ""
        self.imsi = ""
        self.tmsi = ""

    def assemblySMS(self):
        messageDump = []
        #message=[]
        if self.sms["frag"] and self.sms["RP"]:
            for cycle in self.sms.keys():
                for x in self.sms[cycle]:
                    #message.append(hex(ord(x)))
                    messageDump.append(x)
        self.isdnSource = self.getIsdn(messageDump)
        #print self.isdnSource
        #self.showHexdump(messageDump)
        self.gsmPacket(messageDump[0x19:])
        return messageDump

    def gsmPacket(self,object):
        #print len(object)
        #print ord(object[0])

        bins=""
        message=""
        #hexMess=object[1:ord(object[0])-1]
        hexMess=object[1:-1]
        uniCMess = [ord(c) for c in hexMess]
        #print uniCMess
        for i in uniCMess[::-1]:
            bins += str(bin(i)[2:].zfill(8))
        #print bins
        for i in range(len(bins)-7,0,-7):
            message += chr(int(bins[i:i+7],2))
        self.mensaje=message

    def emptyAttr(self):
        self.isdnSource = ""
        self.mensaje = ""
        self.imsi = ""
        self.tmsi = ""

class CCCH():
    def __init__(self):
        self.__timing=None
    def set_timing(self,object):
        self.__timing = object
    def get_timing(self):
        return str(self.__timing)
    def emptyAttr(self):
        self.__timing = None

class RunTime():
    def __init__(self):
        self.flags=0
        self.flagSMS = {"Assigment":False,
                        "PagingRespone":False,
                        "RPdata":False
                        }
        self.firstAlocation = {"Assigment":False,
                               "Identity": False
                               }

    def isPrintable(self,sdcch4,ccch):

        if self.procedure(self.flagSMS):
            print "Normal SMS \t Number: {} Message : {} Imsi: {} TA :{}".format(sdcch4.isdnSource, sdcch4.mensaje, sdcch4.imsi, ccch.get_timing())
            sdcch4.emptyAttr()
            ccch.emptyAttr()
            self.reset(self.flagSMS)
        elif self.procedure(self.firstAlocation) and self.flagSMS["RPdata"]:
            print "First Time \t Imsi : {} TA :{} ".format(sdcch4.imsi,ccch.get_timing())
            ccch.set_timing(None)
            sdcch4.imsi = ""
            self.reset(self.firstAlocation)
            self.flagSMS["RPdata"] = False
        else:
            pass

    def procedure(self,arg):
        if type(arg) == dict:
            return not bool(False in arg.values())
        else:
            return False

    def reset(self, arg):
        if type(arg) == dict:
            for index in arg.keys():
                arg[index]=False
        else:
            return False
    def setAssigment(self):
        self.firstAlocation["Assigment"] = True
        self.flagSMS["Assigment"] = True

def main(x):
    runtime.flags = False
    runtime.isPrintable(sdcch4,ccch)
    print(str(x)[10])
    p=str(x)
    if ord(p[0x36]) == 0x07: # CanalSDCCH/4


        if (ord(p[0x3c]) & 0x03) == 0x03 : #I, N(R)=0, N(S)=0 (Fragment)
            print "I, N(R)=0, N(S)=0 (Fragment)"
            sdcch4.frame = sdcch4.toNumber(p[0x32:][:4])
            sdcch4.sms["frag"]=p[0x3d:][:(ord(p[0x3c])>>2)]
            #sdcch4.showHexdump(p)
            #print "\n"
            #sdcch4.showHexdump(sdcch4.sms["frag"])
        elif (ord(p[0x3c]) & 0x01)==0x01: #(SMS) CP-DATA (RP) RP-DATA
            frameNumber = sdcch4.toNumber(p[0x32:][:4])
            if (sdcch4.frame + 51) == frameNumber: ##reesably Message
                print "(SMS) CP-DATA (RP) RP-DATA"
                #print frameNumber
                sdcch4.sms["RP"]=p[0x3d:][:(ord(p[0x3c])>>2)]
                #sdcch4.showHexdump(p)
                #print "\n"
                #sdcch4.showHexdump(sdcch4.sms["RP"])
                sdcch4.assemblySMS()
                sdcch4.frame=0
                runtime.flagSMS["RPdata"] = True


        if ord(p[0x3e]) == 0x27 and (ord(p[0x2e]) & 0x40) == 0x40:# Pagging Response -Uplink
            runtime.flagSMS["PagingRespone"] = True
            if (ord(p[0x45]) & 0x07)==0x04:  #TMSI
                sdcch4.tmsi = sdcch4.str_tmsi(p[0x46:][:4])
                print "Pagging Response Tmsi : {}".format(sdcch4.str_tmsi(p[0x46:][:4]))
            elif (ord(p[0x45]) & 0x01 )==0x01:  #IMSI
                print "Pagging Response IMSI : {}".format(sdcch4.str_imsi(p[0x45:][:8]))
                sdcch4.imsi = sdcch4.str_imsi(p[0x45:][:8])

        elif (ord(p[0x3e]) & 0x3f) == 0x19 and (ord(p[0x2e]) & 0x40) == 0x40 :#(DTAP) (MM) Identity Response -Uplink
            if (ord(p[0x40]) & 0x01) == 0x01 : #    IMSI
                print "Identity Location : {}".format(sdcch4.str_imsi(p[0x40:][:8]))
                sdcch4.imsi = sdcch4.str_imsi(p[0x40:][:8])
                runtime.firstAlocation["Identity"] = True


    if ord(p[0x36]) == 0x02 : # CCCH Channel

        if ord(p[0x3c]) == 0x3f : #(RR) Immediate Assignment
            ccch.set_timing(ord(p[0x44]))
            print "Immediate Assignment TA : {} ".format(ccch.get_timing())
            runtime.setAssigment()

        elif ord(p[0x3C]) == 0x02 : # (RR) Paging Request Type 1
            if (ord(p[0x3f]) & 0x07) == 0x04:  #TMSI
                print "Pagging Request Tmsi "
            elif (ord(p[0x3f]) )==0x08:  #IMSI
                print "Pagging Request IMSI "


def control(x):
    if runtime.flags:
        main(x)
    else:
        runtime.flags=True

if __name__ == "__main__":
    parser = ArgumentParser(prog= "EventCatcher",
                            conflict_handler='resolve',
                            description=" Programa para identificar los eventos generados por OpenBTS")
    parser.add_argument("-a", "--alltmsi", action="store_true", dest="show_all_tmsi", help="Show TMSI who haven't got IMSI (default  : false)")
    parser.add_argument("-i", "--iface", dest="iface", default="lo", help="Interface (default : lo)")
    parser.add_argument("-p", "--port", dest="port", default="4729", type=int, help="Port (default : 4729)")
    parser.add_argument("-s", "--sniff", action="store_true", dest="sniff", help="sniff on interface instead of listening on port (require root/suid access)")
    args = parser.parse_args()

    if args.sniff :
        from scapy.all import sniff
        sdcch4=SDCCH4()
        runtime=RunTime()
        ccch = CCCH()
        print "Frame \t Numero    Mensaje"
        sniff(iface="lo", filter="not icmp and not tcp and udp port {}".format(4729), prn=control, store=0)
