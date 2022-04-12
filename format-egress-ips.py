# Formats the json output to get all the egress IPs
# Author:          TheScriptGuy
# Last modified:   2022-04-12
# Version:         0.02
# Changelog:
#   * Added ability for creating a csv output.

import sys
import json
import argparse
from os import path

scriptVersion = "0.02"

def parseArguments():
    """
    Create argument options and parse through them to determine what to do with script.
    """

    # Instantiate the parser
    global scriptVersion
    parser = argparse.ArgumentParser(description='Format Egress IPs ' + scriptVersion)

    # Optional arguments
    parser.add_argument('--fileName', default='egress-ips.json',
                        help='List of json formatted egress IPs')
    
    parser.add_argument('--csv', default='',
                        help='Convert the json formatted egress IPs into comma separate values (CSV). Does not display formatted table.') 

    global args    
    args = parser.parse_args()

def output2Csv(__csvFile,__jsonObject):
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

def printJsonObject(__jsonObject):
    # Print Headers
    print('{: <20}{: <18}{: <18}{: <18}'.format("Location", "serviceType", "egress IP", "Active/Reserved"))

    # Iterate through the json object and print accordingly.
    for objEgressIps in __jsonObject["result"]:
        for obj in objEgressIps["address_details"]:
            print('{: <20}{: <18}{: <18}{: <18}'.format(objEgressIps["zone"], obj["serviceType"], obj["address"], obj["addressType"] ))


def getJsonObject(__jsonFile):
    if not path.exists(__jsonFile):
            print('I cannot find file ' + __jsonFile)
            sys.exit(1)
    else:
        f = open(__jsonFile)
        egressIps = json.load(f)
        f.close()

        return egressIps

def main():
    parseArguments()
    myEgressIps = getJsonObject(args.fileName)

    if args.csv:
        # Convert json into csv format.
        output2Csv(args.csv, myEgressIps)
        sys.exit(0)

    if args.fileName:
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
            os._exit(0)