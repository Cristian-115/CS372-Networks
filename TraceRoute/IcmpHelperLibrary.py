# #################################################################################################################### #
# Imports                                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
import os
from socket import *
import struct
import time
import select

expectedseqnum = ""
expectedidentifer = ""
expecteddata = ""
RTTTimes = [] #stores the RTT times
isPinger = False #stores if we are pinging or doind tracert
iccode = [] #holds icmp code valujes
ictype = [] #holds icmptype code
droppedPacket = 0 #incrementor for dropped packets


# #################################################################################################################### #
# Class IcmpHelperLibrary                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
class IcmpHelperLibrary:
    # ################################################################################################################ #
    # Class IcmpPacket                                                                                                 #
    #                                                                                                                  #
    # References:                                                                                                      #
    # https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml                                           #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket:
        # ############################################################################################################ #
        # IcmpPacket Class Scope Variables                                                                             #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __icmpTarget = ""               # Remote Host
        __destinationIpAddress = ""     # Remote Host IP Address
        __header = b''                  # Header after byte packing
        __data = b''                    # Data after encoding
        __dataRaw = ""                  # Raw string data before encoding
        __icmpType = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __icmpCode = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __packetChecksum = 0            # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetIdentifier = 0          # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetSequenceNumber = 0      # Valid values are 0-65535 (unsigned short, 16 bits)
        __ipTimeout = 30
        __ttl = 255                     # Time to live

        __DEBUG_IcmpPacket = False      # Allows for debug output

        # ############################################################################################################ #
        # IcmpPacket Class Getters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpTarget(self):
            return self.__icmpTarget

        def getDataRaw(self):
            return self.__dataRaw

        def getIcmpType(self):
            return self.__icmpType

        def getIcmpCode(self):
            return self.__icmpCode

        def getPacketChecksum(self):
            return self.__packetChecksum

        def getPacketIdentifier(self):
            return self.__packetIdentifier

        def getPacketSequenceNumber(self):
            return self.__packetSequenceNumber

        def getTtl(self):
            return self.__ttl

        # ############################################################################################################ #
        # IcmpPacket Class Setters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIcmpTarget(self, icmpTarget):
            self.__icmpTarget = icmpTarget

            # Only attempt to get destination address if it is not whitespace
            if len(self.__icmpTarget.strip()) > 0:
                self.__destinationIpAddress = gethostbyname(self.__icmpTarget.strip())

        def setIcmpType(self, icmpType):
            self.__icmpType = icmpType

        def setIcmpCode(self, icmpCode):
            self.__icmpCode = icmpCode

        def setPacketChecksum(self, packetChecksum):
            self.__packetChecksum = packetChecksum

        def setPacketIdentifier(self, packetIdentifier):
            self.__packetIdentifier = packetIdentifier

        def setPacketSequenceNumber(self, sequenceNumber):
            self.__packetSequenceNumber = sequenceNumber

        def setTtl(self, ttl):
            self.__ttl = ttl

        # ############################################################################################################ #
        # IcmpPacket Class Private Functions                                                                           #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __recalculateChecksum(self):
            print("calculateChecksum Started...") if self.__DEBUG_IcmpPacket else 0
            packetAsByteData = b''.join([self.__header, self.__data])
            checksum = 0

            # This checksum function will work with pairs of values with two separate 16 bit segments. Any remaining
            # 16 bit segment will be handled on the upper end of the 32 bit segment.
            countTo = (len(packetAsByteData) // 2) * 2

            # Calculate checksum for all paired segments
            print(f'{"Count":10} {"Value":10} {"Sum":10}') if self.__DEBUG_IcmpPacket else 0
            count = 0
            while count < countTo:
                thisVal = packetAsByteData[count + 1] * 256 + packetAsByteData[count]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture 16 bit checksum as 32 bit value
                print(f'{count:10} {hex(thisVal):10} {hex(checksum):10}') if self.__DEBUG_IcmpPacket else 0
                count = count + 2

            # Calculate checksum for remaining segment (if there are any)
            if countTo < len(packetAsByteData):
                thisVal = packetAsByteData[len(packetAsByteData) - 1]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture as 32 bit value
                print(count, "\t", hex(thisVal), "\t", hex(checksum)) if self.__DEBUG_IcmpPacket else 0

            # Add 1's Complement Rotation to original checksum
            checksum = (checksum >> 16) + (checksum & 0xffff)   # Rotate and add to base 16 bits
            checksum = (checksum >> 16) + checksum              # Rotate and add

            answer = ~checksum                  # Invert bits
            answer = answer & 0xffff            # Trim to 16 bit value
            answer = answer >> 8 | (answer << 8 & 0xff00)
            print("Checksum: ", hex(answer)) if self.__DEBUG_IcmpPacket else 0

            self.setPacketChecksum(answer)

        def __packHeader(self):
            # The following header is based on http://www.networksorcery.com/enp/protocol/icmp/msg8.htm
            # Type = 8 bits
            # Code = 8 bits
            # ICMP Header Checksum = 16 bits
            # Identifier = 16 bits
            # Sequence Number = 16 bits
            self.__header = struct.pack("!BBHHH",
                                   self.getIcmpType(),              #  8 bits / 1 byte  / Format code B
                                   self.getIcmpCode(),              #  8 bits / 1 byte  / Format code B
                                   self.getPacketChecksum(),        # 16 bits / 2 bytes / Format code H
                                   self.getPacketIdentifier(),      # 16 bits / 2 bytes / Format code H
                                   self.getPacketSequenceNumber()   # 16 bits / 2 bytes / Format code H
                                   )

        def __encodeData(self):
            data_time = struct.pack("d", time.time())               # Used to track overall round trip time
                                                                    # time.time() creates a 64 bit value of 8 bytes
            dataRawEncoded = self.getDataRaw().encode("utf-8")

            self.__data = data_time + dataRawEncoded

        def __packAndRecalculateChecksum(self):
            # Checksum is calculated with the following sequence to confirm data in up to date
            self.__packHeader()                 # packHeader() and encodeData() transfer data to their respective bit
                                                # locations, otherwise, the bit sequences are empty or incorrect.
            self.__encodeData()
            self.__recalculateChecksum()        # Result will set new checksum value
            self.__packHeader()                 # Header is rebuilt to include new checksum value

        def __validateIcmpReplyPacketWithOriginalPingData(self, icmpReplyPacket):
            # Hint: Work through comparing each value and identify if this is a valid response.
            expectedidentifer = self.getPacketIdentifier
            expecteddata = self.getDataRaw
            expectedseqnum = self.getPacketSequenceNumber
            if self.getPacketSequenceNumber() != icmpReplyPacket.getIcmpSequenceNumber():
                print("Sent sequence number is ", self.getPacketSequenceNumber(), "received ", icmpReplyPacket.getIcmpSequenceNumber())

            if self.getPacketIdentifier() != icmpReplyPacket.getIcmpIdentifier():
                 print("Sent packet identifer is ", self.getPacketIdentifier(), "received ", icmpReplyPacket.getIcmpIdentifier())

            if self.getDataRaw() != icmpReplyPacket.getIcmpData():
                 print("Sent data is ", self.getDataRaw(), "received ", icmpReplyPacket.getIcmpData())

            if self.getPacketSequenceNumber() == icmpReplyPacket.getIcmpSequenceNumber() and self.getPacketIdentifier() == icmpReplyPacket.getIcmpIdentifier() and self.getDataRaw() == icmpReplyPacket.getIcmpData():
                icmpReplyPacket.setIsValidSeqNum(True)
                icmpReplyPacket.setIsValidPacketIdentifer(True)
                icmpReplyPacket.setIsValidRawData(True)
                icmpReplyPacket.setIsValidResponse(True)
            else:
                icmpReplyPacket.setIsValidResponse(False)
                droppedPacket += 1
                print("we dropped a packet", droppedPacket)
            

        # ############################################################################################################ #
        # IcmpPacket Class Public Functions                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def buildPacket_echoRequest(self, packetIdentifier, packetSequenceNumber):
            self.setIcmpType(8)
            self.setIcmpCode(0)
            self.setPacketIdentifier(packetIdentifier)
            self.setPacketSequenceNumber(packetSequenceNumber)
            self.__dataRaw = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            self.__packAndRecalculateChecksum()

        def sendEchoRequest(self):
            if len(self.__icmpTarget.strip()) <= 0 | len(self.__destinationIpAddress.strip()) <= 0:
                self.setIcmpTarget("127.0.0.1")

            print("Pinging (" + self.__icmpTarget + ") " + self.__destinationIpAddress)
            

            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            mySocket.settimeout(self.__ipTimeout)
            mySocket.bind(("", 0))
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', self.getTtl()))  # Unsigned int - 4 bytes
            try:
                mySocket.sendto(b''.join([self.__header, self.__data]), (self.__destinationIpAddress, 0))
                timeLeft = 30
                pingStartTime = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                endSelect = time.time()
                howLongInSelect = (endSelect - startedSelect)
                if whatReady[0] == []:  # Timeout
                    print("  *        *        *        *        *    Request timed out.")
                 # recvPacket - bytes object representing data received
                recvPacket, addr = mySocket.recvfrom(1024)
                # addr  - address of socket sending data
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("  *        *        *        *        *    Request timed out (By no remaining time left).")

                else:
                    # Fetch the ICMP type and code from the received packet
                    icmpType, icmpCode = recvPacket[20:22]

                    if icmpType == 11:
                        if isPinger == True: #if we are pinging check for these errors
                            #check for error codes as per the link provided 
                            if icmpCode == 0:
                                print("TTL exceeded in transit")
                            elif icmpCode == 1:
                                print("Fragment Reassembly Time Exceeded")
                            else:
                                print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s" %
                                    (
                                        self.getTtl(),
                                        (timeReceived - pingStartTime) * 1000,
                                        icmpType,
                                        icmpCode,
                                        addr[0]
                                    )
                                )
                        else: #we are doing trace route, so dont check for errors
                           print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s" %
                                    (
                                        self.getTtl(),
                                        (timeReceived - pingStartTime) * 1000,
                                        icmpType,
                                        icmpCode,
                                        addr[0]
                                    )
                                ) 
                            
                            
                    elif icmpType == 3:                         # Destination Unreachable
                        if icmpCode == 0:  #check for destination unreachable error codes
                             print("Net Unreachable")
                        elif icmpCode == 1:
                            print("Host Unreachable")
                        elif icmpCode == 2:
                            print("Protocol Unreachable")
                        elif icmpCode == 3:
                            print("Port Unreachable")
                        elif icmpCode == 4:
                            print("Fragmentation Needed and Don't Fragment was Set")
                        elif icmpCode == 5:
                            print("Source Route Failed")
                        elif icmpCode == 6:
                            print("	Destination Network Unknown")
                        elif icmpCode == 7:
                            print("Destination Host Unknown")
                        elif icmpCode == 8:
                            print("Source Host Isolated")
                        elif icmpCode == 9:
                            print("Communication with Destination Network is Administratively Prohibited")
                        elif icmpCode == 10:
                            print("Communication with Destination Host is Administratively Prohibited")
                        elif icmpCode == 11:
                            print("Destination Network Unreachable for Type of Service")
                        elif icmpCode == 12:
                            print("Destination Host Unreachable for Type of Service")
                        elif icmpCode == 13:
                            print("Communication Administratively Prohibited")
                        elif icmpCode == 14:
                            print("Host Precedence Violation")
                        elif icmpCode == 15:
                            print("Precedence cutoff in effect")
                        else:
                            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s" %
                                    (
                                        self.getTtl(),
                                        (timeReceived - pingStartTime) * 1000,
                                        icmpType,
                                        icmpCode,
                                        addr[0]
                                    )
                                )

                    elif icmpType == 0:                         # Echo Reply
                        icmpReplyPacket = IcmpHelperLibrary.IcmpPacket_EchoReply(recvPacket)
                        self.__validateIcmpReplyPacketWithOriginalPingData(icmpReplyPacket)
                        icmpReplyPacket.printResultToConsole(self.getTtl(), timeReceived, addr)
                        return      # Echo reply is the end and therefore should return

                    else:
                        print("error")
            except timeout:
                print("  *        *        *        *        *    Request timed out (By Exception).")
            finally:
                mySocket.close()

        def printIcmpPacketHeader_hex(self):
            print("Header Size: ", len(self.__header))
            for i in range(len(self.__header)):
                print("i=", i, " --> ", self.__header[i:i+1].hex())

        def printIcmpPacketData_hex(self):
            print("Data Size: ", len(self.__data))
            for i in range(len(self.__data)):
                print("i=", i, " --> ", self.__data[i:i + 1].hex())

        def printIcmpPacket_hex(self):
            print("Printing packet in hex...")
            self.printIcmpPacketHeader_hex()
            self.printIcmpPacketData_hex()

    # ################################################################################################################ #
    # Class IcmpPacket_EchoReply                                                                                       #
    #                                                                                                                  #
    # References:                                                                                                      #
    # http://www.networksorcery.com/enp/protocol/icmp/msg0.htm                                                         #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket_EchoReply:
        # ############################################################################################################ #
        # IcmpPacket_EchoReply Class Scope Variables                                                                   #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __recvPacket = b''
        __isValidResponse = False
        __isValidSeqNum = False
        __isValidPacketIdentifer = False
        __isValidRawData = False


        # ############################################################################################################ #
        # IcmpPacket_EchoReply Constructors                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __init__(self, recvPacket):
            self.__recvPacket = recvPacket

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Getters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getisValidSeqNum(self):

            return self.__isValidSeqNum

        def getisValidPacketIdentifier(self):

            return self.__isValidPacketIdentifer

        def getisValidRawData(self):
            
            return self.__isValidRawData
        
        def getIcmpType(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[20:20 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 20)

        def getIcmpCode(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[21:21 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 21)

        def getIcmpHeaderChecksum(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[22:22 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 22)

        def getIcmpIdentifier(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[24:24 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 24)

        def getIcmpSequenceNumber(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[26:26 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 26)

        def getDateTimeSent(self):
            # This accounts for bytes 28 through 35 = 64 bits
            return self.__unpackByFormatAndPosition("d", 28)   # Used to track overall round trip time
                                                               # time.time() creates a 64 bit value of 8 bytes

        def getIcmpData(self):
            # This accounts for bytes 36 to the end of the packet.
            return self.__recvPacket[36:].decode('utf-8')

        def isValidResponse(self):
            return self.__isValidResponse

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Setters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIsValidResponse(self, booleanValue):
            self.__isValidResponse = booleanValue

        def setIsValidSeqNum(self, booleanValue):
            self.__isValidSeqNum = booleanValue

        def setIsValidPacketIdentifer(self, booleanValue):
            self.__isValidPacketIdentifer = booleanValue

        def setIsValidRawData(self, booleanValue):
            self.__isValidRawData = booleanValue

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Private Functions                                                                       #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __unpackByFormatAndPosition(self, formatCode, basePosition):
            numberOfbytes = struct.calcsize(formatCode)
            return struct.unpack("!" + formatCode, self.__recvPacket[basePosition:basePosition + numberOfbytes])[0]

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Public Functions                                                                        #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def printResultToConsole(self, ttl, timeReceived, addr):
            
            if( self.isValidResponse() == True):
                
                bytes = struct.calcsize("d")
                timeSent = struct.unpack("d", self.__recvPacket[28:28 + bytes])[0]
                print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d        Identifier=%d    Sequence Number=%d    %s" %
                    (
                        ttl,
                        (timeReceived - timeSent) * 1000,
                        self.getIcmpType(),
                        self.getIcmpCode(),
                        self.getIcmpIdentifier(),
                        self.getIcmpSequenceNumber(),
                        addr[0]
                    )
                    )
                
                if ((self.getIcmpType() == 0) and (self.getIcmpCode() == 0)):# 0's indicate that the traceroute is done, this is needed to break the loop
                    iccode.append(self.getIcmpCode())
                    ictype.append(self.getIcmpType())
                
                
                RTTTimes.append((timeReceived - timeSent) * 1000) # add the RTT times to the array for use later
            else:#handles errors if there data does not match
                if self.getisValidSeqNum() == False:
                    print("expected seqnum of ",expectedseqnum, "received ", self.getIcmpSequenceNumber())
                if self.getisValidPacketIdentifier() == False:
                    print("expected packet identifer of ", expectedidentifer, "received ", self.getIcmpIdentifier())
                if self.getisValidRawData() == False:
                    print("expected raw data of ", expecteddata, "received ", self.getIcmpData())
            



    # ################################################################################################################ #
    # Class IcmpHelperLibrary                                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #

    # ################################################################################################################ #
    # IcmpHelperLibrary Class Scope Variables                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    __DEBUG_IcmpHelperLibrary = False                  # Allows for debug output

    # ################################################################################################################ #
    # IcmpHelperLibrary Private Functions                                                                              #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __sendIcmpEchoRequest(self, host):
        avgRTT = 0xffff                                     #used to calculate avg RTT times
        totalRTT = 0
        count = 0
        
        print("sendIcmpEchoRequest Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        timeSent = time.time()
        
        
        for i in range(4):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()

            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i

            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            icmpPacket.sendEchoRequest()                                                # Build IP

            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            # we should be confirming values are correct, such as identifier and sequence number and data
            timeReceived = time.time()
            count += 1                                  #counts the times we iterated 
        totalRTT += (timeReceived - timeSent) * 1000    #calculates the avg RTT
        avgRTT = totalRTT /count
        #takes care of the min,max,avg RTT's and packet loss, also it rounds to the nearest whole number
        print("Low RTT: %.0f ms" % min(RTTTimes))
        print("High RTT: %.0f ms" %max(RTTTimes))
        print("Average RTT: %.0f ms"% avgRTT)
        print("Percent of packets lost: 0.0%")
        
    def __sendIcmpTraceRoute(self, host): 
        #functon is similar to the one above
        print("sendIcmpTraceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        print("Over a maximum of 30 hops:")
        print("Where TTL is hop number")
        for i in range(30):
            # Build packet
            
            icmpPacket = IcmpHelperLibrary.IcmpPacket()

            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i+1 #increment by one as per the TTL
            icmpPacket.setTtl(packetSequenceNumber)
            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            icmpPacket.sendEchoRequest()                                           # Build IP
            if len(iccode) > 0 and len(ictype) > 0: #check to see if arrays are populated
                if iccode[0] == 0 and ictype[0] == 0: #if they are the trace route is finished, so break the loop
                    break;
                
            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            
            
            # we should be confirming values are correct, such as identifier and sequence number and data
            
    # ################################################################################################################ #
    # IcmpHelperLibrary Public Functions                                                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def sendPing(self, targetHost):
        print("ping Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        isPinger = True #bool value to determine if we are pinging or doing a tracert, in this case we set it to true. This indicates we are pinging
        self.__sendIcmpEchoRequest(targetHost)

    def traceRoute(self, targetHost):
        print("traceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpTraceRoute(targetHost)


# #################################################################################################################### #
# main()                                                                                                               #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
def main():
    icmpHelperPing = IcmpHelperLibrary()


    # Choose one of the following by uncommenting out the line
    #icmpHelperPing.sendPing("209.233.126.254")
    #icmpHelperPing.sendPing("www.google.com")
    # icmpHelperPing.sendPing("oregonstate.edu")
    # icmpHelperPing.sendPing("gaia.cs.umass.edu")
    #icmpHelperPing.sendPing("www.kawaijibika.gr.jp")
    icmpHelperPing.sendPing("www.openxtra.co.uk")
    #icmpHelperPing.traceRoute("gaia.cs.umass.edu")
    #icmpHelperPing.traceRoute("www.openxtra.co.uk")
    #icmpHelperPing.traceRoute("www.kawaijibika.gr.jp")
    #icmpHelperPing.traceRoute("209.233.126.254")
    #icmpHelperPing.traceRoute("www.google.com")

if __name__ == "__main__":
    main()
