#ToDo List
#Adjacencies    -   Done
#Definitions    -   Done
#province.bmp   -   Done
#default.map    -   Done
#Positions      -   Done
#Localizations  -   Done
#terrainType    -   Done
#Ports          -   Done
#Areas          -   Done
#OTHER STUFF???


#User INPUTS
startProvicne = 7889
endProvince = 8286
newStartProvicne = 8212
#Makes selection area of map smaller to reduce time significantly
ChropedMap = False
XStart = 5846   #309
YStart = 267    #256
XEnd = 7570     #7565
YEnd = 1923     #3960


import copy
from decimal import *
import glob
import codecs
import re
from PIL import Image
import time
import itertools
from multiprocessing.pool import ThreadPool as Pool

class ProvinceDefinition:
    id = 0
    red = 0
    green = 0
    blue = 0
    name = ""
    name2 = ""
    other_info = ""
    lastKnownY = -1

class Posisitions:
    id = 0
    PosX = 0.0
    PosY = 0.0
    PosZ = 0.0
    Rot1 = 0.0
    Rot2 = 0.0
    Rot3 = 0.0
    Rot4 = 0.0
    Scale1 = 0.0
    Scale2 = 0.0
    Scale3 = 0.0

class Adjacencies:
    IDfrom = 0
    IDto = 0
    adjType = ""
    IDthrough = 0
    commnet = ""
    xStart = 0
    yStart = 0
    xEnd = 0
    yEnd = 0
    leadingComment = False

class Ports:
    landID = 0
    seaID = 0
    xPos = 0
    yPos = 0
    otherInfo = ""

class Areas:
    areaName = ""
    areaIDs = []

def get_province_deff(baseMapDefinition):
    deffMap = baseMapDefinition.read().splitlines()
    deffList = []
    x=0
    for line in deffMap:
        if "province;red;green;blue;x;x" in line:
            continue
        else:
            if x<14000:
                tmpline = line.split(';')
                try:
                    county = ProvinceDefinition()
                    county.red = int(tmpline[1])
                    county.id = int(tmpline[0].lstrip("#"))
                    county.green = int(tmpline[2])
                    county.blue = int(tmpline[3])
                    county.name = tmpline[4]
                    county.other_info = tmpline[5]
                    deffList.append(county)
                except IndexError:
                    pass
        x +=1
    return deffList

def get_adjacencies(baseMapAdjacencies,StartProvicne,EndProvince):
    adjMap = baseMapAdjacencies.read().splitlines()
    adjList = []
    x=0
    for line in adjMap:
        if "From;To;Type;Through;" in line or line.startswith('-1;-1;-1;-1;'):
            continue
        else:
            tmpline = line.split(';')
            try:
                adj = Adjacencies()
                if tmpline[0].startswith('#'):
                    #print(tmpline[0])
                    tmpline[0]=tmpline[0].lstrip('#')
                    adj.leadingComment=True
                adj.IDto = int(tmpline[1])
                adj.IDfrom = int(tmpline[0])
                adj.adjType = tmpline[2]
                adj.IDthrough = int(tmpline[3])
                adj.xStart = int(tmpline[4])
                adj.yStart = int(tmpline[5])
                adj.xEnd = int(tmpline[6])
                adj.yEnd = int(tmpline[7])
                adj.commnet = tmpline[8]
                if (adj.IDfrom >= StartProvicne and adj.IDfrom <= EndProvince) or (adj.IDto >= StartProvicne and adj.IDto <= EndProvince) or (adj.IDthrough >= StartProvicne and adj.IDthrough <= EndProvince):
                    adjList.append(adj)
            except IndexError:
                pass
    return adjList

def get_positions(MapPositions):
    PosLines = MapPositions.read().splitlines()
    countyList = []
    x=0 
    for line in PosLines:
        if "id=" in line:
            county = Posisitions()
            county.id = line.lstrip().lstrip("id=")
            
            p = []
            for t in PosLines[x+1].lstrip().lstrip("position={").rstrip("}").split():
                try:
                    p.append(Decimal(t))
                except ValueError:
                    pass
            county.PosX = p[0]
            county.PosY = p[1]
            county.PosZ = p[2]

            r=[]
            for t in PosLines[x+2].lstrip().lstrip("rotation={").rstrip("}").split():
                try:
                    if "-" in t:
                        r.append(-1*Decimal(t.lstrip("-")))
                    else:
                        r.append(Decimal(t))
                except ValueError:
                    pass
            county.Rot1 = r[0]
            county.Rot2 = r[1]
            county.Rot3 = r[2]
            county.Rot4 = r[3]

            s=[]
            for t in PosLines[x+3].lstrip().lstrip("scale={").rstrip("}").split():
                try:
                    if "-" in t:
                        s.append(-1*Decimal(t.lstrip("-")))
                    else:
                        s.append(Decimal(t))
                except ValueError:
                    pass
            county.Scale1 = s[0]
            county.Scale2 = s[1]
            county.Scale3 = s[2]
            countyList.append(county)
        x+=1 
    return countyList

def threaded_DrawProvinces(x1,x2,y1,y2,z,smallCountyListNames,newSmallCountyListNames,pixMNR,pixNew):
    print("%s - %g / %g"%(smallCountyListNames[z].name,z,len(smallCountyListNames)))
    provinceEnd = False
    for y in  range(y1,y2):
        if provinceEnd:
            break
        else:
            for x in range(x1,x2):
                #print(smallCountyListNames[z].red)
                if pixMNR[x,y] == (smallCountyListNames[z].red, smallCountyListNames[z].green, smallCountyListNames[z].blue):
                    pixNew[x,y] = copy.deepcopy((newSmallCountyListNames[z].red, newSmallCountyListNames[z].green, newSmallCountyListNames[z].blue, 255))
                    #print("%i, %i, %i"%(x,y,z))
                    #print(pixNew[x,y])
                    #print(z)
                    smallCountyListNames[z].lastKnownY = y
                    #print(y)

            if smallCountyListNames[z].lastKnownY > -1 and y > smallCountyListNames[z].lastKnownY + (y2 * 1/256):
                #print("poped:\t%s" %smallCountyListNames[z].name)
                provinceEnd = True
                print("Poped\t %s - %g / %g"%(smallCountyListNames[z].name,z,len(smallCountyListNames)))
                break
    i=0

def draw_UpdatedProvinces(MNRMapProvinces, smallCountyListNames, newSmallCountyListNames, XStart, YStart, XEnd, YEnd, ChropedMap):
    pixMNR = MNRMapProvinces.load()
    img = Image.new(MNRMapProvinces.mode, MNRMapProvinces.size, 'white')
    pixNew = img.load()
    if ChropedMap:
        x1,y1=XStart,YStart
        x2,y2=XEnd,YEnd
    else:
        x1,y1=0,0
        x2,y2=MNRMapProvinces.size[0],MNRMapProvinces.size[1]
    z=0
    #print(len(smallCountyListNames))

    pool_size = 20
    pool = Pool(pool_size)

    while z < len(smallCountyListNames):
        pool.apply_async(threaded_DrawProvinces,(x1,x2,y1,y2,z,smallCountyListNames,newSmallCountyListNames,pixMNR,pixNew,))
        z+=1
    pool.close()
    pool.join()
        

    img.show()
    img.save("OutPut\\map\\province_OutPut.bmp")
    img.close()

def get_portsCSV(portsCSV):
    portMap = portsCSV.read().splitlines()
    portList = []
    
    for line in portMap:
        #print(lin)
        if "LandProvince;SeaZone;x;y;" in line:
            continue
        else:
            tmpline = line.split(';')
            #print(tmpline)
            try:
                port = Ports()
                port.landID = int(tmpline[0])
                port.seaID = int(tmpline[1])
                port.xPos = int(tmpline[2])
                port.yPos = int(tmpline[3])
                port.otherInfo = tmpline[4]
                portList.append(port)
            except ValueError:
                pass
    return portList
    

def write_Adjacencies(adjList,newStartProvicne,newEndProvince):
    outputAdj = open("OutPut\\map\\adjacencies_OutPut.csv", "w",encoding='utf-8',errors='ignore')
    for county in adjList:
        if (county.IDfrom >= newStartProvicne and county.IDfrom <= newEndProvince) or (county.IDto >= newStartProvicne and county.IDto <= newEndProvince) or (county.IDthrough >= newStartProvicne and county.IDthrough <= newEndProvince):
            outputAdj.write("\n")
            if county.leadingComment:
                outputAdj.write("#")
            outputAdj.write("%g;"%county.IDfrom)
            outputAdj.write("%g;"%county.IDto)
            outputAdj.write("%s;"%county.adjType)
            outputAdj.write("%g;"%county.IDthrough)
            outputAdj.write("%g;%g;%g;%g;"%(county.xStart,county.yStart,county.xEnd,county.yEnd))
            outputAdj.write("%s"%county.commnet)


    outputAdj.close()

def write_Definitions(deffList,newStartProvicne,newEndProvince):
    outputDeff = open("OutPut\\map\\definitions_OutPut.csv", "w",encoding='utf-8',errors='ignore')
    for county in deffList:
        
        if county.id >= newStartProvicne and county.id <= newEndProvince:
            #print(county.name)
            outputDeff.write("\n%g;"%county.id)
            outputDeff.write("%g;"%county.red)
            outputDeff.write("%g;"%county.green)
            outputDeff.write("%g;"%county.blue)
            outputDeff.write("%s;"%county.name)
            
            outputDeff.write("%s;;;;;;;;;;;;;;;;;;;,"%county.other_info)
    outputDeff.close()

def write_DefaultMap(updaetdDefaultMapList):
    DefaultMap = open("OutPut\\map\\defalut_OutPut.map", "w",encoding='utf-8',errors='ignore')
    for line in updaetdDefaultMapList:
        for index in line:
            DefaultMap.write("%s "%index)
        DefaultMap.write("\n")
    DefaultMap.close()

def write_Positions(tmpNewPos,file):
    tmpFileString = "OutPut\\" + file.lstrip("INRMap\\").rstrip(".txt")+"_output.txt"
    #print(tmpFileString)
    Positions = open(tmpFileString, "w",encoding='utf-8',errors='ignore')
    for county in tmpNewPos:
        Positions.write("\n\t\t{")
        Positions.write("\n\t\t\tid=%g"%county.id)
        Positions.write("\n\t\t\tposition={ %g %g %g }"%(county.PosX,county.PosY,county.PosZ))
        Positions.write("\n\t\t\trotation={ %g %g %g %g }"%(county.Rot1,county.Rot2,county.Rot3,county.Rot4))
        Positions.write("\n\t\t\tscale={ %g %g %g }"%(county.Scale1,county.Scale2,county.Scale3))
        Positions.write("\n\t\t}")
    Positions.close()

def update_Area(tmpArea,startingDiffrence):
    INRAreaOut = open("Output\\map\\areas.txt", 'w')
    numTabs = 0
    for line in tmpArea:
        commentFound = False
        lineList = line.split()
        if line.strip().startswith("}"):
                numTabs -=1
                if numTabs<0:
                        numTabs=0
        for _ in range(numTabs):
            INRAreaOut.write("\t")
        for element in lineList:
            if "#" in element:
                commentFound = True
            if not commentFound:
                if "{" in element:
                    numTabs += 1
                if "}" in element:
                    numTabs -=1
                    if numTabs<0:
                        numTabs=0
                try:
                    tmpID = int(element)
                    if tmpID >= startProvicne and tmpID <=endProvince:
                        INRAreaOut.write("%i "%(tmpID+startingDiffrence))
                    else:
                        INRAreaOut.write("%s "%element)
                except ValueError:
                    INRAreaOut.write("%s "%element)
            else:
                INRAreaOut.write("%s "%element)
        INRAreaOut.write("\n")

def update_Terrain(tmpHistory, startingDiffrence):
    INRTerrainOut = open("Output\\setup\\provinces\\01_INR_provinces.txt", 'w')
    numTabs = 0
    for line in tmpHistory:
        tmpLine = line.split()
        if line.strip().startswith("}"):
            numTabs -=1
            if numTabs<0:
                numTabs=0
        for _ in range(numTabs):
            INRTerrainOut.write("\t")
        for element in tmpLine:
            if "{" in element:
                    numTabs += 1
            if "}" in element:
                numTabs -=1
                if numTabs<0:
                    numTabs=0
            try:
                tmpID = int(element)
                if tmpID >= startProvicne and tmpID <=endProvince:
                    INRTerrainOut.write("%i "%(tmpID+startingDiffrence))
                else:
                    INRTerrainOut.write("%s "%element)
            except ValueError:
                INRTerrainOut.write("%s "%element)
        INRTerrainOut.write("\n")

def update_ProvinceSetup(startingDiffrence):
    ProvSetup=glob.glob("INRMap/setup/provinces/*.txt")
    for file in ProvSetup:
        #print(file)
        tmpSetup = open(file)
        fileOutput = open("Output%s"%file.lstrip("INRMap"), 'w')
        for line in tmpSetup:
            #print(line)
            tmpline = ""
            for id in range(startProvicne,endProvince+1):
                if line.startswith("%i"%id):
                    tmpline = line.lstrip("%i"%id)
                    line = ("%i%s"%(id+startingDiffrence,tmpline))
                    break
                    #fileOutput.write(line)

            fileOutput.write(line)
        fileOutput.close()
i=0
ts = time.time()
#print(ts)

bUpdateMap = True

INRMapDefinition = open("INRMap\\map\\definition.csv")
INRMapAdjacencies = open("INRMap\\map\\adjacencies.csv")
INRDefaultMap = open("INRMap\\map\\default.map")
try:
    INRProvinces = Image.open("INRMap\\map\\provinces.bmp")
except:
    print("province map missing will not run map updater")
    bUpdateMap = False
#INRTerrainType = open("INRMap\\setup\\provinces\\01_INR_provinces.txt")
INRPortCSV = open("INRMap\\map\\ports.csv", 'r')
INRArea = open("INRMap\\map\\areas.txt", 'r')


adjList = get_adjacencies(INRMapAdjacencies,startProvicne,endProvince)
deffList = get_province_deff(INRMapDefinition)
deffList2 = get_province_deff(INRMapDefinition)


#Grab all provinces that will be effected by change
smallCountyListNames = []
for county in deffList:
    #print("%s, %s"%(county.id,startProvicne))
    if county.id >= startProvicne and county.id <= endProvince:
        smallCountyListNames.append(copy.deepcopy(county))
        #print(county.name)

i=0
#Set province name in new spot
startingDiffrence = newStartProvicne - startProvicne 
newEndProvince = startingDiffrence + endProvince 
newSmallCountyListNames = []
if True:
    for county in deffList:
        if county.id >= newStartProvicne and county.id <= newEndProvince:
            #print("%g, %g, %s"%(i,county.id,county.name))
            #print((smallCountyListNames[i]).name  )
            county.name = (smallCountyListNames[i]).name  
            
            county.other_info = (smallCountyListNames[i]).other_info
            newSmallCountyListNames.append(copy.deepcopy(county))
            i +=1
i=0


#get lines containing province ID in default.map
defaultMapList = []
defaultMap = INRDefaultMap.read().splitlines()
for line in defaultMap:
    j= startProvicne
    newTmpLine = ""
    while j <= endProvince+1:
        if str(j) in line:
            if line not in defaultMapList:
                defaultMapList.append(line)
                #print(line)
        j +=1
i=0
#update lines in default map
updaetdDefaultMapList = []
for line in defaultMapList:
    tmpLine = line.split(" ")
    tmpLineList= []
    for index in tmpLine:
        try:
            tmpID = int(index.lstrip().rstrip())
            if tmpID >= startProvicne and tmpID <= endProvince+1:
                index = int(index.lstrip().rstrip()) + startingDiffrence
            #print(index)
        except ValueError:
            pass
        tmpLineList.append(index)
    #print(tmpLineList)
    updaetdDefaultMapList.append(tmpLineList)


#get and update lines containing province ID in adjancies.csv
for county in adjList:
    if county.IDfrom >= startProvicne and county.IDfrom <= endProvince:
        county.IDfrom += startingDiffrence
    if county.IDto >= startProvicne and county.IDto <= endProvince:
        county.IDto += startingDiffrence
    if county.IDthrough >= startProvicne and county.IDthrough <= endProvince:
        county.IDthrough += startingDiffrence

i=0

#get all river provinces positions that will be effected by change
PositionFiles = glob.glob('INRMap\\gfx\\map\\map_object_data\\*.txt')
for file in PositionFiles:
   tmpPos = get_positions(open(file))
   tmpNewPos = []
   for county in tmpPos:
       if int(county.id) >= startProvicne and int(county.id) <= endProvince:
           county.id = int(county.id) + startingDiffrence
           tmpNewPos.append(county)
   write_Positions(tmpNewPos,file)

LocalizationFiles = glob.glob('INRMap\\localization\\*\\*\\*.yml')
for file in LocalizationFiles:
    #print(file)
    tmpLocal = codecs.open(file, 'r', 'utf-8-sig')
    tmpLocalString = "OutPut\\" + file.lstrip("INRMap\\")
    tmpOutPut = codecs.open(tmpLocalString, 'w', 'utf-8-sig')
    for line in tmpLocal:
        if line.startswith(" PROV"):
            id = re.search('PROV(.*):0 "', line)
            ProvName = re.search(':0 "(.*)"', line)
            if int(id.group(1)) >= startProvicne and int(id.group(1)) <= endProvince:
                tmpOutPut.write(" PROV%g:0 \"%s\"\n"%(int(id.group(1))+startingDiffrence, ProvName.group(1)))
            else:
                tmpOutPut.write(line)
            #print(id.group(1))
        else:
            tmpOutPut.write(line)
    tmpOutPut.close()

#update port provinces
tmpPortCSV = open("OutPut\\map\\ports.csv", "w",encoding='utf-8',errors='ignore')
tmpPortCSV.write("LandProvince;SeaZone;x;y;\n")
portslistCSV = get_portsCSV(INRPortCSV)
for port in portslistCSV:
    if port.seaID >= startProvicne and port.seaID <= endProvince:
        port.seaID = port.seaID + startingDiffrence
    tmpPortCSV.write("%g;%g;%g;%g;%s\n"%(port.landID,port.seaID,port.xPos,port.yPos,port.otherInfo))
i=0
tmpPortCSV.close()


i=0
#change province map color


write_Definitions(newSmallCountyListNames,newStartProvicne,newEndProvince)
write_Adjacencies(adjList,newStartProvicne,newEndProvince)
write_DefaultMap(updaetdDefaultMapList)
update_Area(INRArea, startingDiffrence)
##update_Terrain(INRTerrainType, startingDiffrence) #Depricated use update_ProvinceSetup
update_ProvinceSetup(startingDiffrence)
if bUpdateMap:
    draw_UpdatedProvinces(INRProvinces, smallCountyListNames, newSmallCountyListNames, XStart, YStart, XEnd, YEnd, ChropedMap)
ts2 = time.time()
print("%g Seconds"%(ts2 - ts))
