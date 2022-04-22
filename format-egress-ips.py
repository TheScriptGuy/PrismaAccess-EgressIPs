# Formats the json output to get all the egress IPs
# Author:          TheScriptGuy
# Last modified:   2022-04-21
# Version:         0.05
# Changelog:
#   Added better handling for URL requests.
#   Fixed bug with prod URL.

import sys
import json
import argparse
from os import path
import os.path
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


scriptVersion = "0.05"

PrismaAccessHeaders = { "header-api-key": "" } 

API_KEY_FILE = 'prisma-access-api.key'

getPrismaAccessURI ='https://api.prod.datapath.prismaaccess.com/getPrismaAccessIP/v2'


# All Public IP addresses
EgressIPs = { "serviceType": "all", "addrType": "all", "location": "all" }

# Mobile Users IP Addresses
ActiveReservedOnboardedMobileUserLocations = { "serviceType": "gp_gateway", "addrType": "all", "location": "deployed" }
ActiveIPOnboardedMobileUserLocations = { "serviceType": "gp_gateway", "addrType": "active", "location": "deployed" }
ActiveMobileUserAddresses = { "serviceType": "gp_gateway", "addrType": "all", "location": "all" }

# Remote Network IP addresses
RemoteNetworkAddresses = { "serviceType": "remote_network", "addrType": "all", "location": "all" }

# Clean Pipe IP addresses
CleanPipeAddresses = { "serviceType": "clean_pipe", "addrType": "all", "location": "all" }

# Explicit Proxy IP addresses
ExplicitProxyAddresses = { "serviceType": "swg_proxy", "location": "deployed", "addrType": "auth_cache_service" }

def parseArguments():
    """
    Create argument options and parse through them to determine what to do with script.
    """

    # Instantiate the parser
    global scriptVersion
    parser = argparse.ArgumentParser(description='Format Egress IPs ' + scriptVersion)

    # Optional arguments
    parser.add_argument('--fileName', default='',
                        help='List of json formatted egress IPs to convert.')
    
    parser.add_argument('--setAPIKey', default='',
                        help='Sets the API key into prisma-access-api.key file')

    parser.add_argument('--showAPIKey', action='store_true',
                        help='Shows the Prisma Access API Key from the prisma-access-api.key file.')

    parser.add_argument('--deleteAPIKey', action='store_true',
                        help='Deletes the Prisma Access API Key from prisma-access-api.key file.')

    parser.add_argument('--allEgressIPs', action='store_true',
                        help='Shows all egress IPs for Prisma Access Service')

    parser.add_argument('--allAROnboardedMobileUserLocations', action='store_true',
                        help='Retrieve all the active/reserved IP addresses for Mobile User Locations')

    parser.add_argument('--allActiveIPOnboardedMobileUserLocations', action='store_true',
                        help='Retrieve all the active Mobile Users IP addresses')

    parser.add_argument('--allActiveMobileUserAddresses', action='store_true',
                        help='Shows all Active Mobile User Addresses')

    parser.add_argument('--allRemoteNetworkAddresses', action='store_true',
                        help='Shows all Remote Network Addresses')

    parser.add_argument('--allCleanPipeAddresses', action='store_true',
                        help='Shows all Clean Pipe Addresses')

    parser.add_argument('--allExplicitProxyAddresses', action='store_true',
                        help='Shows all Clean Pipe Addresses')

    parser.add_argument('--outputJsonFile', default='',
                        help='Send json output to file.')

    parser.add_argument('--outputCsvFile', default='',
                        help='Convert json output into comma separated values file.')

    global args    
    args = parser.parse_args()

def setAPIKey(__APIKey):
    f_apikey = open(API_KEY_FILE,'w')
    f_apikey.write(__APIKey)
    f_apikey.close()
    print('Success')
    sys.exit(0)

def delAPIKey():
    if path.exists(API_KEY_FILE):
        os.remove(API_KEY_FILE)
        print('Success')
    else:
        print('API Key file does not exist.')
        sys.exit(1)

def getAPIKey():
    if path.exists(API_KEY_FILE):
        f_apikey = open(API_KEY_FILE,'r')
        __APIKey = f_apikey.readline().rstrip('\n')
        f_apikey.close()
        return __APIKey
    else:
        print('Cannot find key file. Please define with the --setAPIKey argument.')
        sys.exit(1)



def jsonConvert2Csv(__csvFile,__jsonObject):
    if "status" in __jsonObject:
        if __jsonObject["status"] == "success":
            # Open the csv file name
            # file contents will be overwritten.
            csv = open(__csvFile,"w")

            # CSV headers
            csvHeaders = ["Location","serviceType","egress IP","Active/Reserved"]

            # Write the CSV headers to the file.
            csv.write(','.join(f'"{w}"' for w in csvHeaders) + '\n')
            # Iterate through the json object and write the output into the csv file
            for objEgressIps in __jsonObject["result"]:
                for obj in objEgressIps["address_details"]:
                    strToWrite = [objEgressIps["zone"], obj["serviceType"], obj["address"], obj["addressType"]]
                    csv.write(','.join(f'"{w}"' for w in strToWrite) + '\n')

            # Close the file
            csv.close()
        else:
            print("This is not a valid json object to convert.")
            sys.exit(1)

def printJsonObject(__jsonObject):
    # Print Headers
    print('{: <20}{: <18}{: <18}{: <18}'.format("Location", "serviceType", "egress IP", "Active/Reserved"))
    try:
        if "status" in __jsonObject:
            if __jsonObject["status"] == "success":
                # Iterate through the json object and print accordingly.
                for objEgressIps in __jsonObject["result"]:
                    for obj in objEgressIps["address_details"]:
                        print('{: <20}{: <18}{: <18}{: <18}'.format(objEgressIps["zone"], obj["serviceType"], obj["address"], obj["addressType"] ))
            else:
                print(__jsonObject["result"])
                sys.exit(1)
        else:
            print(__jsonObject)

    except TypeError:
        print("Are you sure this is the right JSON object?")
        sys.exit(1)

def getJsonObject(__jsonFile):
    if not path.exists(__jsonFile):
            print('I cannot find file ' + __jsonFile)
            sys.exit(1)
    else:
        f = open(__jsonFile)
        egressIps = json.load(f)
        f.close()

        return egressIps

def getJsonObjectFromUrl(__jsonurl, __uriheaders, __uribody):
    # Disable certificate checks when establishing a connection

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    try:
    

        # Json POST request
        __jsonRequest = requests.post(__jsonurl,headers=__uriheaders,data=json.dumps(__uribody),verify=False)

        # Convert result into a JSON object
        __jsonObject = json.loads(__jsonRequest.text)
        return __jsonObject

    except requests.exceptions.Timeout:
        print('Timeout while retrieving URL.')
        sys.exit(1)
    except requests.exceptions.TooManyRedirects:
        print('Too many redirects while accessing the URL')
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print('Could not connect to URL - ' + __jsonurl + '\n')
        sys.exit(1)
    except urllib3.exceptions.MaxRetryError:
        print('Maximum number of retries exceeded.')
        sys.exit(1)

def outputJsonFile(__jsonFileName,__jsonObject):
    # Write the JSON object into the __jsonFileName file.
    jsonFile = open(__jsonFileName, "w")
    jsonFile.write(json.dumps(__jsonObject))
    jsonFile.close()

def checkArgsJsonCsv(__jsonObject):
    # Check to see if the outputCsvFile is defined.

    if args.outputCsvFile:
        # Convert the Json object into CSV format.
        jsonConvert2Csv(args.outputCsvFile,__jsonObject)
        sys.exit(0)

    if args.outputJsonFile:
        # Write the Json object into json file.
        outputJsonFile(args.outputJsonFile,__jsonObject)
        sys.exit(0)

def showAllEgressIps(__PrismaAccessHeaders):
    # Shows all egress IPs used in the Prisma Access Service.
    __AllEgressIps = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,EgressIPs)
    
    checkArgsJsonCsv(__AllEgressIps)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__AllEgressIps)

def showAllActiveMobileUserAddresses(__PrismaAccessHeaders):
    # Shows all Active Mobile User Addresses used in the Prisma Access Service.
    __AllActiveMobileUserAddresses = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,ActiveMobileUserAddresses)

    checkArgsJsonCsv(__AllActiveMobileUserAddresses)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__AllActiveMobileUserAddresses)

def showAllActiveReservedOnboardedMobileUserLocations(__PrismaAccessHeaders):
    # Shows all Active/Reserved for Onboarded Mobile User Locations IPs used in the Prisma Access Service.
    __AllActiveReservedOnboardedMobileUserLocations = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,ActiveReservedOnboardedMobileUserLocations)

    checkArgsJsonCsv(__AllActiveReservedOnboardedMobileUserLocations)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__AllActiveReservedOnboardedMobileUserLocations)

def showActiveIPOnboardedMobileUserLocations(__PrismaAccessHeaders):
    # Shows all Active for Onboarded Mobile User Locations IPs used in the Prisma Access Service.
    __ActiveIPOnboardedMobileUserLocations = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,ActiveIPOnboardedMobileUserLocations)

    checkArgsJsonCsv(__ActiveIPOnboardedMobileUserLocations)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__ActiveIPOnboardedMobileUserLocations)

def showRemoteNetworkAddresses(__PrismaAccessHeaders):
    # Shows all Remote Network IPs used in the Prisma Access Service.
    __RemoteNetworkAddresses = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,RemoteNetworkAddresses)

    checkArgsJsonCsv(__RemoteNetworkAddresses)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__RemoteNetworkAddresses)

def showCleanPipeAddresses(__PrismaAccessHeaders):
    # Shows all Clean Pipe IPs used in the Prisma Access Service.
    __CleanPipeAddresses = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,CleanPipeAddresses)

    checkArgsJsonCsv(__CleanPipeAddresses)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__CleanPipeAddresses)

def showExplicitProxyAddresses(__PrismaAccessHeaders):
    # Shows all Explicit Proxy IPs used in the Prisma Access Service.
    __ExplicitProxyAddresses = getJsonObjectFromUrl(getPrismaAccessURI,__PrismaAccessHeaders,ExplicitProxyAddresses)

    checkArgsJsonCsv(__ExplicitProxyAddresses)
    
    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__ExplicitProxyAddresses)

def argsMobileUsers(__PrismaAccessHeaders):
    if args.allActiveMobileUserAddresses:
        showAllActiveMobileUserAddresses(__PrismaAccessHeaders)
        sys.exit(0)

    if args.allAROnboardedMobileUserLocations:
        showAllActiveReservedOnboardedMobileUserLocations(__PrismaAccessHeaders)
        sys.exit(0)

    if args.allActiveIPOnboardedMobileUserLocations:
        showActiveIPOnboardedMobileUserLocations(__PrismaAccessHeaders)
        sys.exit(0)

def argsRemoteNetworks(__PrismaAccessHeaders):
    if args.allRemoteNetworkAddresses:
        showRemoteNetworkAddresses(__PrismaAccessHeaders)
        sys.exit(0)

def argsCleanPipe(__PrismaAccessHeaders):
    if args.allCleanPipeAddresses:
        showCleanPipeAddresses(__PrismaAccessHeaders)
        sys.exit(0)

def argsExplicitProxy(__PrismaAccessHeaders):
    if args.allExplicitProxyAddresses:
        showExplicitProxyAddresses(__PrismaAccessHeaders)
        sys.exit(0)

def apiArguments():
    if args.setAPIKey:
        setAPIKey(args.setAPIKey)

    if args.showAPIKey:
        print(getAPIKey())
        sys.exit(0)

    if args.deleteAPIKey:
        delAPIKey()
        sys.exit(0)

def apiQueryArguments():
    # Check to see if the API Key file is defined.
    API_KEY = getAPIKey()
    PrismaAccessHeaders = { "header-api-key": API_KEY } 

    if args.allEgressIPs:
        showAllEgressIps(PrismaAccessHeaders)
        sys.exit(0)


    argsMobileUsers(PrismaAccessHeaders)
    argsRemoteNetworks(PrismaAccessHeaders)
    argsCleanPipe(PrismaAccessHeaders)
    argsExplicitProxy(PrismaAccessHeaders)


def main():
    # Parse all the arguments for the script
    parseArguments()

    # Check to see if the API arguments are defined.
    apiArguments()

    if args.allEgressIPs or args.allAROnboardedMobileUserLocations or args.allActiveMobileUserAddresses or args.allRemoteNetworkAddresses or args.allCleanPipeAddresses or args.allExplicitProxyAddresses:
        apiQueryArguments()

    if args.fileName:
        # If the --fileName argument is specified, the script will
        # import the json object in the file.
        myEgressIps = getJsonObject(args.fileName)

        if args.outputCsvFile:
            # Convert json into csv format.
            jsonConvert2Csv(args.outputCsvFile, myEgressIps)
            sys.exit(0)

        # By default print the json object in tabulated form.
        printJsonObject(myEgressIps)
        sys.exit(0)


if __name__ == '__main__':
    try:
        
        main()

    except KeyboardInterrupt:
        print('Interrupted')
        print
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
