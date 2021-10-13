from segment import Segment

# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    packetssent = 0 #tracks what char we left off on
    bigstr = ''
    seqnum = 0
    totalSize = 0
    dictonary = {}
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        packetssent = 0 #tracks what char we left off on
        bigstr = ''
        seqnum = 0
        totalSize = 0
        dictonary = {}

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...
        return self.bigstr

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
       

        # ############################################################################################################ #
        
        data = self.dataToSend
        totCharsSent = 0
        while True:
            segmentSend = Segment()
            dataChunk = data[self.seqnum:self.seqnum+4]
            self.seqnum +=4
            if dataChunk == "":
                break
            
            
            segmentSend.setData(self.seqnum,dataChunk)
            totCharsSent += 4
            print("Sending segment: ", segmentSend.to_string())
            # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(segmentSend)
            if totCharsSent + 4 > 15:
                break

        
        
        
        
        
        
      
            
            
        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)


        


        # ############################################################################################################ #
        # Display sending segment
            #segmentSend.setData(seqnum,data)
            #print("Sending segment: ", segmentSend.to_string())

        # Use the unreliable sendChannel to send the segment
            #self.sendChannel.send(segmentSend)

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()                  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()
        recStr = ''
      
        if (len(listIncomingSegments) >= 1):
            
            listIncomingSegments.sort(key=lambda self: self.seqnum) # sorts packets when they come out of order
            for i in range(len(listIncomingSegments)):
                #if listIncomingSegments[i].checkChecksum:
                    
                #print(listIncomingSegments[i].checkChecksum())
                recStr += listIncomingSegments[i].payload
                self.totalSize += len(recStr)
                """ if listIncomingSegments[i].acknum == -1: #this is data segment 
                    self.acknum = listIncomingSegments[i].acknum #set the ack and send it # sends packets multiple times so its not needed
                    Ack = Segment()
                    Ack.setAck(self.acknum)
                    self.sendChannel.send(Ack) """ 
                #else: # this is ack segment
                    #self.dictonary[self.seqnum] = listIncomingSegments[i].payload
        
            self.bigstr += recStr
    
        

      
    

        
        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented
        






        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segemnts?
        #print('processReceive(): Complete this...')

        # Somewhere in here you will be setting the contents of the ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...
        acknum = "0"


        # ############################################################################################################ #
        # Display response segment
        segmentAck.setAck(acknum)
        print("Sending ack: ", segmentAck.to_string())

        # Use the unreliable sendChannel to send the ack packet
        self.sendChannel.send(segmentAck)
