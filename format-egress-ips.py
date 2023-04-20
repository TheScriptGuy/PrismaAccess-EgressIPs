# Formats the json output to get all the egress IPs
# Author:          TheScriptGuy
# Last modified:   2023-04-20
# Version:         0.13
# Changelog:
#   Added some better error handling in case a json object is not returned.

import sys
import json
import argparse
from os import path
import os.path
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


scriptVersion = "0.13"

API_KEY_FILE = 'prisma-access-api.key'

# All Public IP addresses
EgressIPs = {"serviceType": "all", "addrType": "all", "location": "all"}

# Mobile Users IP Addresses
ActiveReservedOnboardedMobileUserLocations = {"serviceType": "gp_gateway", "addrType": "all", "location": "deployed"}
ActiveIPOnboardedMobileUserLocations = {"serviceType": "gp_gateway", "addrType": "active", "location": "deployed"}
ActiveMobileUserAddresses = {"serviceType": "gp_gateway", "addrType": "all", "location": "all"}

# Remote Network IP addresses
RemoteNetworkAddresses = {"serviceType": "remote_network", "addrType": "all", "location": "all"}

# Clean Pipe IP addresses
CleanPipeAddresses = {"serviceType": "clean_pipe", "addrType": "all", "location": "all"}

# Explicit Proxy IP addresses
ExplicitProxyAddresses = {"serviceType": "swg_proxy", "location": "deployed", "addrType": "auth_cache_service"}

# Loopback IP
addressType = "loopback_ip"


def parseArguments():
    """Create argument options and parse through them to determine what to do with script."""
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

    parser.add_argument('--apiKey', default='',
                        help='Use stdin to enter API Key')

    parser.add_argument('--environment', default='prod',
                        help='By default, script queries prod environment.')

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

    parser.add_argument('--allLoopbackIPAddresses', action='store_true',
                        help='Retrieves all the loopback addresses for each location.')

    parser.add_argument('--outputJsonFile', default='',
                        help='Send json output to file.')

    parser.add_argument('--outputCsvFile', default='',
                        help='Convert json output into comma separated values file.')

    parser.add_argument('--outputEdlFile', default='',
                        help='Convert json into external dynamic list file.')

    global args
    args = parser.parse_args()


def setAPIKey(__APIKey):
    """This will set the API key to be used by the script."""
    with open(API_KEY_FILE, 'w') as f_apikey:
        f_apikey.write(__APIKey)
    print('Success')
    sys.exit(0)


def delAPIKey():
    """Delete the API key."""
    if path.exists(API_KEY_FILE):
        os.remove(API_KEY_FILE)
        print('Success')
    else:
        print('API Key file does not exist.')
        sys.exit(1)


def getAPIKey():
    """Get the API key from the API_KEY_FILE file."""
    if args.apiKey:
        __APIKey = args.apiKey
    else:
        if path.exists(API_KEY_FILE):
            with open(API_KEY_FILE) as f_apikey:
                __APIKey = f_apikey.readline().rstrip('\n')
        else:
            print('Cannot find key file. Please define with the --setAPIKey argument or use --apiKey argument and pass through stdin.')
            sys.exit(1)
    return __APIKey


def jsonConvert2Csv(__csvFile, __dataObject):
    """Convert Json object to into csv file format."""

    __myDataObject = __dataObject

    if not isinstance(__myDataObject, list):
        # __dataObject is not a list (legacy loopback IP addresses)
        if "status" in __myDataObject and __myDataObject["status"] == "success":
            # Open the csv file name
            # file contents will be overwritten.
            with open(__csvFile, 'w') as csv:
                # CSV headers
                csvHeaders = ["Location", "serviceType", "egress IP", "Active/Reserved"]

                # Write the CSV headers to the file.
                csv.write(','.join(f'"{w}"' for w in csvHeaders) + '\n')
                # Iterate through the json object and write the output into the csv file
                for objEgressIps in __myDataObject["result"]:
                    for obj in objEgressIps["address_details"]:
                        strToWrite = [objEgressIps["zone"], obj["serviceType"], obj["address"], obj["addressType"]]
                        csv.write(','.join(f'"{w}"' for w in strToWrite) + '\n')
        else:
            print("This is not a valid json object to convert.")
            sys.exit(1)
    else:
        # __myDataObject is a list (legacy loopback IP addresses)
        with open(__csvFile, 'w') as csv:
            # CSV Headers
            csvHeaders = ["Type", "Location", "Loopback IP"]
            csv.write(','.join(f'"{w}"' for w in csvHeaders) + '\n')

            while len(__myDataObject) != 0:
                dataItem = __myDataObject.pop()
                print(dataItem)
                if "status" in dataItem and dataItem["status"] == "success":
                    # Iterate through the json object and write the output to csv file.
                    for loopbackItem in dataItem["result"]["addrList"]:
                        locationInfo = loopbackItem.split(":")
                        strToWrite = [dataItem["result"]["fwType"], locationInfo[0], locationInfo[1]]
                        print(strToWrite)
                        csv.write(','.join(f'"{w}"' for w in strToWrite) + '\n')


def printJsonObject(__jsonObject):
    """Output the Json object in a tabulated format to stdout"""
    try:
        if isinstance(__jsonObject, list):
            if "message" in __jsonObject[0] and __jsonObject[0]["message"] == "Unauthorized":
                print("Unauthorized API usage. Using wrong environment or API key perhaps?")
                sys.exit(1)

            # Table looks a little different for loopback_ips
            tableString = '{: <15}{: <20}{: <15}'

            # Print headers
            print(tableString.format("Type", "Location", "Loopback IP"))

            # Iterate through the json object and print accordingly.
            while len(__jsonObject) != 0:
                jsonItem = __jsonObject.pop()
                if "status" in jsonItem and jsonItem["status"] != "error":
                    for item in jsonItem["result"]["addrList"]:
                        locationInfo = item.split(":")
                        print(tableString.format(jsonItem["result"]["fwType"], locationInfo[0], locationInfo[1]))
        else:
            if "status" in __jsonObject and __jsonObject["status"] != "error":
                # Set the table string format.
                tableString = '{: <20}{: <18}{: <18}{: <18}'
                print(tableString.format("Location", "serviceType", "egress IP", "Active/Reserved"))

                # Iterate through the json object and print accordingly.
                for objEgressIps in __jsonObject["result"]:
                    for obj in objEgressIps["address_details"]:
                        print(tableString.format(objEgressIps["zone"], obj["serviceType"], obj["address"], obj["addressType"]))
            else:
                # First check to see if the __jsonObject has an unauthorized message.
                if "message" in __jsonObject and __jsonObject["message"] == "Unauthorized":
                    print("Unauthorized API usage. Using wrong environment or API key perhaps?")
                    sys.exit(1)

    except TypeError:
        print("Are you sure this is the right JSON object?")
        print(__jsonObject)
        sys.exit(1)


def getJsonObject(__jsonFile):
    """Get the json object from the __jsonFile object."""
    if not path.exists(__jsonFile):
        print('I cannot find file ' + __jsonFile)
        sys.exit(1)
    else:
        f = open(__jsonFile)
        egressIps = json.load(f)
        f.close()

        return egressIps


def getJsonObjectFromUrl(__jsonurl, __uriheaders, __uribody):
    """Disable certificate checks when establishing a connection."""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    try:
        if not args.allLoopbackIPAddresses:
            # Json POST request
            __jsonRequest = requests.post(__jsonurl, headers=__uriheaders, data=json.dumps(__uribody), verify=False)

            # Convert result into a JSON object
            __jsonObject = json.loads(__jsonRequest.text)
        else: 
            __legacyPrismaAccessURI = __jsonurl + f'fwType={__uribody}&addrType={addressType}'

            # Json GET request
            __jsonRequest = requests.get(__legacyPrismaAccessURI, headers=__uriheaders, verify=False)

            # Convert result into a JSON object
            __jsonObject = json.loads(__jsonRequest.text)

        return __jsonObject

    except requests.exceptions.Timeout:
        print('Timeout while retrieving URL.')
        sys.exit(1)
    except requests.exceptions.TooManyRedirects:
        print('Too many redirects while accessing the URL.')
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print('Could not connect to URL - ' + __jsonurl + '\n')
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        print('Not a valid json object returned.')
        sys.exit(1)


def outputJsonFile(__jsonFileName, __jsonObject):
    """Write the JSON object into the __jsonFileName file."""
    with open(__jsonFileName, 'w') as jsonFile:
        jsonFile.write(json.dumps(__jsonObject))


def outputEdlFile(__edlFileName, __jsonObject):
    """Write the IP addresses from the jsonObject into the __edlFileName"""
    # Create the ipEdl list
    ipEdl = []

    # First iterate through __jsonObject to find IP addresses
    try:
        if isinstance(__jsonObject, list):
            # Table looks a little different for loopback_ips
            # Iterate through the json object and append IP address to ipEdl.
            while len(__jsonObject) != 0:
                jsonItem = __jsonObject.pop()
                if "status" in jsonItem and jsonItem["status"] != "error":
                    for item in jsonItem["result"]["addrList"]:
                        locationInfo = item.split(":")
                        ipEdl.append(locationInfo[1])
        else:
            if "status" in __jsonObject and \
                    __jsonObject["status"] == "success":

                # Iterate through the json object and append IP address to ipEdl.
                for objEgressIps in __jsonObject["result"]:
                    for obj in objEgressIps["address_details"]:
                        ipEdl.append(obj["address"])
            else:
                print(__jsonObject)
                sys.exit(1)

    except TypeError:
        print("Are you sure this is the right JSON object?")
        print(__jsonObject)
        sys.exit(1)

    # Write contents of ipEdl to __edlFileName
    with open(__edlFileName, 'w') as edlFile:
        edlFile.write('\n'.join(ipEdl))


def checkArgsJsonCsvEdl(__dataObject):
    """Check to see if the outputCsvFile is defined."""
    if args.outputCsvFile:
        # Convert the Json object into CSV format.
        jsonConvert2Csv(args.outputCsvFile, __dataObject)
        sys.exit(0)

    if args.outputJsonFile:
        # Write the Json object into json file.
        outputJsonFile(args.outputJsonFile, __dataObject)
        sys.exit(0)

    if args.outputEdlFile:
        # Write the IP addresses into the edl file.
        outputEdlFile(args.outputEdlFile, __dataObject)
        sys.exit(0)


def showAllEgressIps(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all egress IPs used in the Prisma Access Service."""
    __AllEgressIps = getJsonObjectFromUrl(__getPrismaAccessURI,
                                          __PrismaAccessHeaders,
                                          EgressIPs)

    checkArgsJsonCsvEdl(__AllEgressIps)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__AllEgressIps)


def showAllActiveMobileUserAddresses(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all Active Mobile User Addresses used in the Prisma Access Service."""
    __AllActiveMobileUserAddresses = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                          __PrismaAccessHeaders,
                                                          ActiveMobileUserAddresses)

    checkArgsJsonCsvEdl(__AllActiveMobileUserAddresses)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__AllActiveMobileUserAddresses)


def showAllActiveReservedOnboardedMobileUserLocations(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all Active/Reserved for Onboarded Mobile User Locations IPs used in the Prisma Access Service."""
    __AllActiveReservedOnboardedMobileUserLocations = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                                           __PrismaAccessHeaders,
                                                                           ActiveReservedOnboardedMobileUserLocations)

    checkArgsJsonCsvEdl(__AllActiveReservedOnboardedMobileUserLocations)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__AllActiveReservedOnboardedMobileUserLocations)


def showActiveIPOnboardedMobileUserLocations(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all Active for Onboarded Mobile User Locations IPs used in the Prisma Access Service."""
    __ActiveIPOnboardedMobileUserLocations = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                                  __PrismaAccessHeaders,
                                                                  ActiveIPOnboardedMobileUserLocations)

    checkArgsJsonCsvEdl(__ActiveIPOnboardedMobileUserLocations)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__ActiveIPOnboardedMobileUserLocations)


def showRemoteNetworkAddresses(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all Remote Network IPs used in the Prisma Access Service."""
    __RemoteNetworkAddresses = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                    __PrismaAccessHeaders,
                                                    RemoteNetworkAddresses)

    checkArgsJsonCsvEdl(__RemoteNetworkAddresses)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__RemoteNetworkAddresses)


def showCleanPipeAddresses(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all Clean Pipe IPs used in the Prisma Access Service."""
    __CleanPipeAddresses = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                __PrismaAccessHeaders,
                                                CleanPipeAddresses)

    checkArgsJsonCsvEdl(__CleanPipeAddresses)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__CleanPipeAddresses)


def showExplicitProxyAddresses(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all Explicit Proxy IPs used in the Prisma Access Service."""
    __ExplicitProxyAddresses = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                    __PrismaAccessHeaders,
                                                    ExplicitProxyAddresses)

    checkArgsJsonCsvEdl(__ExplicitProxyAddresses)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(__ExplicitProxyAddresses)


def showLoopbackIPAddresses(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Shows all the loopback IP addresses of the tenant."""
    fwTypes = ['gpcs_gp_gw', 'gpcs_gp_portal', 'gpcs_remote_network', 'gpcs_clean_pipe']
    uriBody = ""

    loopbackItems = []

    for item in fwTypes:
        uriBody = item
        __LoopbackIPAddresses = getJsonObjectFromUrl(__getPrismaAccessURI,
                                                     __PrismaAccessHeaders,
                                                     uriBody)
        loopbackItems.append(__LoopbackIPAddresses)

    checkArgsJsonCsvEdl(loopbackItems)

    # Only reaches this stage if the outputJsonFile or outputCsvFile is not defined.
    printJsonObject(loopbackItems)


def argsMobileUsers(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Parse through Mobile user arguments"""
    if args.allActiveMobileUserAddresses:
        showAllActiveMobileUserAddresses(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)

    if args.allAROnboardedMobileUserLocations:
        showAllActiveReservedOnboardedMobileUserLocations(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)

    if args.allActiveIPOnboardedMobileUserLocations:
        showActiveIPOnboardedMobileUserLocations(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)


def argsRemoteNetworks(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Show the Remote Network Addresses"""
    if args.allRemoteNetworkAddresses:
        showRemoteNetworkAddresses(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)


def argsCleanPipe(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Show the Clean Pipe Addresses"""
    if args.allCleanPipeAddresses:
        showCleanPipeAddresses(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)


def argsExplicitProxy(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Show the Explicit Proxy Addresses"""
    if args.allExplicitProxyAddresses:
        showExplicitProxyAddresses(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)


def argsLoopbackIPAddresses(__getPrismaAccessURI, __PrismaAccessHeaders):
    """Checks to see if the --allLoopbackIPAddresses argument is set."""
    if args.allLoopbackIPAddresses:
        showLoopbackIPAddresses(__getPrismaAccessURI, __PrismaAccessHeaders)
        sys.exit(0)


def apiArguments():
    """Parse through the API arguments"""
    if args.setAPIKey:
        setAPIKey(args.setAPIKey)

    if args.showAPIKey:
        print(getAPIKey())
        sys.exit(0)

    if args.deleteAPIKey:
        delAPIKey()
        sys.exit(0)


def apiQueryArguments(__getPrismaAccessURI):
    """Check to see if the API Key file is defined."""
    API_KEY = getAPIKey()
    PrismaAccessHeaders = {"header-api-key": API_KEY}

    argsLoopbackIPAddresses(__getPrismaAccessURI, PrismaAccessHeaders)

    if args.allEgressIPs:
        showAllEgressIps(__getPrismaAccessURI, PrismaAccessHeaders)
        sys.exit(0)

    argsMobileUsers(__getPrismaAccessURI, PrismaAccessHeaders)
    argsRemoteNetworks(__getPrismaAccessURI, PrismaAccessHeaders)
    argsCleanPipe(__getPrismaAccessURI, PrismaAccessHeaders)
    argsExplicitProxy(__getPrismaAccessURI, PrismaAccessHeaders)


def main():
    """Parse all the arguments for the script"""
    parseArguments()

    # Define the URL to query
    getPrismaAccessURI = f'https://api.{args.environment}.datapath.prismaaccess.com/getPrismaAccessIP/v2'

    # Check to see if the API arguments are defined.
    apiArguments()

    if args.allLoopbackIPAddresses:
        legacyPrismaAccessURI = f'https://api.{args.environment}.datapath.prismaaccess.com/getAddrList/latest?'
        apiQueryArguments(legacyPrismaAccessURI)

    if (args.allEgressIPs or
       args.allAROnboardedMobileUserLocations or
       args.allActiveIPOnboardedMobileUserLocations or
       args.allActiveMobileUserAddresses or
       args.allRemoteNetworkAddresses or
       args.allCleanPipeAddresses or
       args.allExplicitProxyAddresses) and not args.allLoopbackIPAddresses:
        apiQueryArguments(getPrismaAccessURI)

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
        print()
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
