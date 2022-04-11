# Formats the json output to get all the egress IPs

import sys
import json
import argparse
from os import path

scriptVersion = "0.01"

def parseArguments():
    """
    Create argument options and parse through them to determine what to do with script.
    """

    # Instantiate the parser
    global scriptVersion
    parser = argparse.ArgumentParser(description='Format Egress IPs ' + scriptVersion)

    # Optional arguments
    parser.add_argument('--fileName', default="egress-ips.json",
                        help='List of json formatted egress IPs')
    
    global args    
    args = parser.parse_args()

def main():
    parseArguments()
    if args.fileName:
        if not path.exists(args.fileName):
            print('I cannot find file ' + args.fileName)
            sys.exit(1)
        else:
            f = open(args.fileName)

            egressIps = json.load(f)

            # Print Headers
            print('{: <20}{: <18}{: <18}{: <18}'.format("Location", "serviceType", "egress IP", "Active/Reserved"))
            for objEgressIps in egressIps["result"]:
                for obj in objEgressIps["address_details"]:
                    print('{: <20}{: <18}{: <18}{: <18}'.format(objEgressIps["zone"], obj["serviceType"], obj["address"], obj["addressType"] ))


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

