'''
Class for dealing with mzXML files and handling the data. Particularly useful for decoding the 
peak lists. 
'''
import sys
import base64 #Imports a binary converter package
import struct
import gzip #For file handling
import xml.parsers.expat
from MSScan import MS1Scan, MS2Scan

#Defines a class of objects of MzXML type. Will innitialize with the following values. 
class MzXML():
    def __init__(self):
        self.msLevel = 0
        self.current_tag = ''
        self.tag_level = 0
        self.MS1_list = []
        self.MS2_list = []
        
    #Function that decodes a single line *** Need to determine what line is so this can be called ***
    def decode_spectrum(self,line):
        #Decodes a given line of... ????
        decoded = base64.decodestring(line)

        #Determines unpack format which is specific to the type of data being examined
        tmp_size = len(decoded)/4
        unpack_format1 = ">%dL" % tmp_size

        #Declares an index which will be used to dictacte positive or negative scans
        idx = 0

        #Declares list for mzs and intensities
        mz_list = []
        intensity_list = []

        #Loops through the decoded, unpacked line and breaks them apart into positive and negative scans
        for tmp in struct.unpack(unpack_format1,decoded):
            tmp_i = struct.pack("I",tmp) 
            tmp_f = struct.unpack("f",tmp_i)[0] 
            if( idx % 2 == 0 ):
                mz_list.append( float(tmp_f) )
            else:
                intensity_list.append( float(tmp_f) )
            idx += 1
            
        #Returns the two lists of intensitiesand mzs
        return mz_list,intensity_list

    def _start_element(self,name,attrs):
        #Increments the tag_level for the MzXML object and updates the current_tag
        self.tag_level += 1
        self.current_tag = name

        #If it's a precursorMz it adjusts accordingly *** Not entirely sure what's happening here ***
        if( name == 'precursorMz' ):
            self.MS2_list[-1].precursor_intensity = float(attrs['precursorIntensity'])

            self.MS2_list[-1].precursor_charge = 0
            if( attrs.has_key('precursorCharge') ):
                self.MS2_list[-1].precursor_charge = int(attrs['precursorCharge'])
        #If the element being read in is a scan, checks what the scan level is and initializes a list of that type
        if( name == 'scan' ):
            self.msLevel = int(attrs['msLevel'])
            if( self.msLevel == 1 ):
                tmp_ms = MS1Scan()
            elif( self.msLevel == 0 ): # *************** changed ms level from == 2 to ==0**************
                tmp_ms = MS2Scan()
            else:
                print("What is it?",attrs)
                sys.exit(1)

            #Assigns attributes to their logical properties
            tmp_ms.id = int(attrs['num'])
            tmp_ms.peak_count = int(attrs['peaksCount'])
            tmp_ms.filter_line = attrs['filterLine']
            tmp_ms.retention_time = float(attrs['retentionTime'].strip('PTS'))
            tmp_ms.low_mz = float(attrs['lowMz'])
            tmp_ms.high_mz = float(attrs['highMz'])
            tmp_ms.base_peak_mz = float(attrs['basePeakMz'])
            tmp_ms.base_peak_intensity = float(attrs['basePeakIntensity'])
            tmp_ms.total_ion_current = float(attrs['totIonCurrent'])
            tmp_ms.list_size = 0
            tmp_ms.encoded_mz = ''
            tmp_ms.encoded_intensity = ''
            tmp_ms.mz_list = []
            tmp_ms.intensity_list = []

            #Adds the scan to the correct list of scans
            if( self.msLevel == 1 ):
                self.MS1_list.append(tmp_ms)
            elif( self.msLevel == 0 ): # *************** changed ms level from == 2 to ==0**************
                #tmp_ms.ms1_id = self.MS1_list[-1].id
                self.MS2_list.append(tmp_ms)
                
    #Reduces the tag level, sets current_tag to '' and msLevel at 0
    def _end_element(self,name):
        self.tag_level -= 1
        self.current_tag = ''
        self.msLevel == 0

    
    def _char_data(self,data):
        if( self.current_tag == 'precursorMz' ):
            self.MS2_list[-1].precursor_mz = float(data)

        if( self.current_tag == 'peaks' ):
            mz_list, intensity_list = self.decode_spectrum(data)
            mz_string = ''.join([struct.pack('>f',i) for i in mz_list])
            intensity_string = ''.join([struct.pack('>f',i) for i in intensity_list])
            if( self.msLevel == 1 ):
                self.MS1_list[-1].list_size += len(mz_list)
                self.MS1_list[-1].encoded_mz += base64.encodestring(mz_string)
                self.MS1_list[-1].encoded_intensity += base64.encodestring(intensity_string)
                self.MS1_list[-1].mz_list += mz_list 
                self.MS1_list[-1].intensity_list += intensity_list

            elif( self.msLevel == 0 ):
                self.MS2_list[-1].list_size += len(mz_list)
                self.MS2_list[-1].encoded_mz += base64.encodestring(mz_string)
                self.MS2_list[-1].encoded_intensity += base64.encodestring(intensity_string)
                self.MS2_list[-1].mz_list = mz_list
                self.MS2_list[-1].intensity_list = intensity_list
    
    def parse_file(self,filename_xml):
        sys.stderr.write("Read %s ... "%filename_xml)
        f_xml = open(filename_xml,'r')
        if( filename_xml.endswith('.gz') ):
            f_xml = gzip.open(filename_xml,'rb')
        content_list = []
        for line in f_xml:
            content_list.append(line)
        f_xml.close()

        expat = xml.parsers.expat.ParserCreate()
        expat.StartElementHandler = self._start_element
        expat.EndElementHandler = self._end_element
        expat.CharacterDataHandler = self._char_data
        expat.Parse("".join(content_list))
        
        sys.stderr.write("Done\n")



