#!/bin/python3

import sys
from threading import Thread
import gatt
import argparse
import random


SERV_IWOWN = '0000ff20-0000-1000-8000-00805f9b34fb'
SERV_DFU = '00001530-1212-efde-1523-785feabcd123'

CHAR_WRITE = '0000ff21-0000-1000-8000-00805f9b34fb'
CHAR_NOTIFY = '0000ff22-0000-1000-8000-00805f9b34fb'
CHAR_INDICATE = '0000ff23-0000-1000-8000-00805f9b34fb'

CHAR_DFU_CONTROL = '00001531-1212-efde-1523-785feabcd123'
CHAR_DFU_DATA = '00001532-1212-efde-1523-785feabcd123'


NOTIFY_MSG = [1,2]
NOTIFY_MSG_NOICON = [2, 2]
NOTIFY_CALL = [1,1]
NOTIFY_CALL_STH = [2,1]


class IWownDevice(gatt.Device):

    def set_command(self, cmd):
        self.cmd = cmd

    def services_resolved(self):
        super().services_resolved()
        self.dataacc = None

        self.iwown = None
        for s in self.services:
            print("SERVICE " + s.uuid)
            if s.uuid == SERV_IWOWN:
                self.iwown = s

        if self.iwown:
            self.iwown_write = None
            self.iwown_indicate = None
            for c in self.iwown.characteristics:
                print("CHARACTERISTIC " + c.uuid)
                if c.uuid == CHAR_WRITE:
                    self.iwown_write = c
                elif c.uuid == CHAR_INDICATE:
                    self.iwown_indicate = c
                    self.iwown_indicate.enable_notifications()

        ########################################
            if args.action == 'notif':
                for line in sys.stdin:
                    try:
                        line = cmd + formatMsg(line, [1, int(args.notiftype)])
                        line += [0]
                        print(line)
                        for i in range(0, len(line), 20):
                            cmd_part = line[i:i+20]
                            print(cmd_part)
                            self.iwown_write.write_value(cmd_part)
                        return
                    except TypeError:
                        print("wrong cmd")
                    except KeyboardInterrupt:
                        print("end")
                        exit(0)
                #self.iwown_write.read_value()



            else:
                self.cmd += [0]
                for i in range(0, len(cmd), 20):
                    cmd_part = cmd[i:i+20]
                    print(cmd_part)
                    self.iwown_write.write_value(cmd_part)


        ########################################

    @staticmethod
    def makeHeader(a, b):
        return [0x21, 0xFF, ((a & 0xf) << 4) | (b & 0xf)]

    def characteristic_value_updated(self, characteristic, value):
        # print("characteristic_value_updated {} {}".format(characteristic.uuid, value))

        if characteristic.uuid == CHAR_INDICATE:
            # accumulate data until we get desired size
            if self.dataacc is None:
                self.datatag = value[2]
                self.datalen = value[3]
                self.dataacc = value[4:]
            else:
                self.dataacc += value

            # if we've got all the data, process it!
            if self.datalen == len(self.dataacc):
                if self.datatag == 0:
                    fwversion = "{}.{}.{}.{}".format(self.dataacc[8], self.dataacc[9], self.dataacc[10], self.dataacc[11])
                    oadmode = (self.dataacc[6] << 8) | self.dataacc[7]
                    model = self.dataacc[2:6]
                    print("firmware: model={} version={} oadmode={}".format(model.decode('utf-8'), fwversion, oadmode))

                elif self.datatag == 1:
                    print("power {}%".format(self.dataacc[0]))

                else:
                    print("-----UNKNOWN RESULT----")
                    for i, x in enumerate(self.dataacc):
                        print("{}: {} {} {}".format(i, x, hex(x), chr(x)))

    def characteristic_read_value_succeeded(self, characteristic):
        print("characteristic_read_value_succeeded {}".format(characteristic.uuid))

    def characteristic_read_value_failed(self):
        print("characteristic_read_value_failed")

    def characteristic_write_value_succeeded(self, characteristic):
    #    print("characteristic_write_value_succeeded {}".format(characteristic.uuid))
        pass

    def characteristic_write_value_failed(self):
        print("characteristic_write_value_failed")

    def characteristic_enable_notifications_succeeded(self, characteristic):
        print("characteristic_enable_notifications_succeeded")
        exit(0)
        pass

    def characteristic_enable_notifications_failed(self, characteristic, error):
        print("characteristic_enable_notifications_failed")




def read_bmp():
    with open("bitmap.bmp", mode='rb') as file:
        bmp = file.read()
        nbmp = []

        for i in range(0, len(bmp)):
            if bmp[i] == 255:
                nbmp += [1]
            else:
                nbmp += [0]

        return nbmp


def formatMsg(msg, msg_type):

    msg = msg.rstrip("\n")
    msgBytes = msg_type

    #TODO
    API = 1

    if API == 1:

        msg = msg[:6]
        while len(msg) < 6:
            msg += " "

     #   bmp = read_bmp()
        #msgBytes += bmp[20:]

        #msgBytes += [1]
        for x in range(0, 1):
          #  msgBytes += [1]
           # msgBytes += [2]
         #   for i in range(0, 16*16):
          #      msgBytes += [random.randint(48,49)]
            pass

        i=0
        for ch in msg:
            i = not i
       #     msgBytes += [i]
            msgBytes += [1]
          #  msgBytes += [2]
          #  msgBytes += bytes(ch, "utf8")
          #  msgBytes += read_bmp()
            pass


            for x in range(0, 16):
                for y in range(0, 16):
                    msgBytes += [1]




    elif API == 2:
        msgBytes += [0xFF]    # for API2
        msgBytes += bytes(msg, "utf8")

    return msgBytes


parser = argparse.ArgumentParser(description='IWOWN command tool')
parser.add_argument('--usbhost', default='hci0', help='USB host to use')
parser.add_argument('action', help='what to do!', choices=["getfwinfo", 'getpower', 'dfumode', 'config', 'date', 'set_date', 'user_params', 'notif', 'selfie', 'end_notif', 'set_alarm'])
parser.add_argument('mac', help='mac address')
parser.add_argument('--notiftype', default='1', help='Notification type')
args = parser.parse_args()



try:
    manager = gatt.DeviceManager(adapter_name=args.usbhost)

    if args.action == 'getfwinfo':
        cmd = IWownDevice.makeHeader(0, 0)

    elif args.action == 'getpower':
        cmd = IWownDevice.makeHeader(0, 1)

#  elif args.action == 'dfumode':
    #  cmd = IWownDevice.makeHeader(0, 6)

    elif args.action == 'config':
        cmd = IWownDevice.makeHeader(1, 9)

    elif args.action == 'user_params':
        cmd = IWownDevice.makeHeader(2, 1)

    elif args.action == 'date':
        cmd = IWownDevice.makeHeader(1, 1)

    elif args.action == 'set_date':
        #TODO not working yet
        cmd = IWownDevice.makeHeader(1, 0) + [22, 1, 11, 11, 10, 0, 0]

    elif args.action == 'notif':
        #TODO not really working yet
        # vibrates, shows respective icon, but not text
        cmd = IWownDevice.makeHeader(3, 1)

    elif args.action == 'selfie':
        #TODO not working yet
        cmd = IWownDevice.makeHeader(4, 0)

    elif args.action == 'end_notif':
        #TODO not working yet
        cmd = IWownDevice.makeHeader(4, 1)

    elif args.action == 'set_alarm':
        #TODO not working yet
        cmd = IWownDevice.makeHeader(1, 4) + [0, 0, 0, 19, 32]


   # print(cmd)
  #  manager.set_timeout(3 * 1000)
    device = IWownDevice(mac_address=args.mac, manager=manager)
    device.set_command(cmd)
    device.connect()
  #  thread = Thread(target = start_mangr)
   # thread.start()
    manager.run()


 #   for line in sys.stdin:
    #    thread.join(1)
     #   thread.start()
   #     pass


except KeyboardInterrupt:
    print("")
  #  device.disconnect()
    pass
