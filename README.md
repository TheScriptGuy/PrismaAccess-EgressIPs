# PrismaAccess-EgressIPs
Provide the egress IPs for the Prisma Access service in a formatted context.

# Dependencies
Make sure that you have python's `requests` module installed
```bash
$ pip3 install requests
```

# Help output
If no arguments are specified, the script will not run. The last order of evaluation is checking to see if the --fileName argument has been set/

The logic is such that it follows this order:
1. If no arguments are supplied, exit script.
2. If one of the --all* arguments are supplied, check to see if the API Key exists (either checking the file prisma-access-api.key file or looking at the argument supplied from --apiKey. 
- No API key, exit script. 
- API key exists, then attempt to get the egress IPs based based on argument supplied. 
3. If egress IPs are returned from the API, then display them in tabulated format to stdout. Exit script.
4. If egress IPs are returned from the API, and the `--outputJsonFile` **or** `--outputCsvFile` argument is specified, then send the resulting output to those files in the appropriate format. Exit script.
5. For these 2 options below, the API key does not need to be set.
6. If the `--fileName` argument is used, then display the output to stdout in tabulated format.
7. If the `--fileName` arguement and the `--outputCsvFile` arguments are used in tandem, then the json formatted file is converted to comma separated values.


```bash
$ python3 format-egress-ips.py
usage: format-egress-ips.py [-h] [--fileName FILENAME] [--setAPIKey SETAPIKEY] [--showAPIKey] [--deleteAPIKey] [--apiKey APIKEY] [--environment ENVIRONMENT] [--allEgressIPs]
                            [--allAROnboardedMobileUserLocations] [--allActiveIPOnboardedMobileUserLocations] [--allActiveMobileUserAddresses] [--allRemoteNetworkAddresses]
                            [--allCleanPipeAddresses] [--allExplicitProxyAddresses] [--allLoopbackIPAddresses] [--outputJsonFile OUTPUTJSONFILE] [--outputCsvFile OUTPUTCSVFILE]

Format Egress IPs 0.10

options:
  -h, --help            show this help message and exit
  --fileName FILENAME   List of json formatted egress IPs to convert.
  --setAPIKey SETAPIKEY
                        Sets the API key into prisma-access-api.key file
  --showAPIKey          Shows the Prisma Access API Key from the prisma-access-api.key file.
  --deleteAPIKey        Deletes the Prisma Access API Key from prisma-access-api.key file.
  --apiKey APIKEY       Use stdin to enter API Key
  --environment ENVIRONMENT
                        By default, script queries prod environment.
  --allEgressIPs        Shows all egress IPs for Prisma Access Service
  --allAROnboardedMobileUserLocations
                        Retrieve all the active/reserved IP addresses for Mobile User Locations
  --allActiveIPOnboardedMobileUserLocations
                        Retrieve all the active Mobile Users IP addresses
  --allActiveMobileUserAddresses
                        Shows all Active Mobile User Addresses
  --allRemoteNetworkAddresses
                        Shows all Remote Network Addresses
  --allCleanPipeAddresses
                        Shows all Clean Pipe Addresses
  --allExplicitProxyAddresses
                        Shows all Clean Pipe Addresses
  --allLoopbackIPAddresses
                        Retrieves all the loopback addresses for each location.
  --outputJsonFile OUTPUTJSONFILE
                        Send json output to file.
  --outputCsvFile OUTPUTCSVFILE
                        Convert json output into comma separated values file.
```

# API Keys
- To get the API key:
  - [Panorama](https://docs.paloaltonetworks.com/prisma/prisma-access/preferred/2-2/prisma-access-panorama-admin/prisma-access-overview/retrieve-ip-addresses-for-prisma-access)
  - [Cloud Managed](https://docs.paloaltonetworks.com/prisma/prisma-access/prisma-access-cloud-managed-admin/prisma-access-service-infrastructure/retrieve-ip-addresses-to-allow-for-prisma-access)

## To set API Key
Creates the file prisma-access-api.key and adds the API key into it.

```bash
$ python3 format-egress-ips.py --setAPIKey this_is_my_api_key
Success
$
```

## To show the API key:
```bash
$ python3 format-egress-ips.py --showAPIKey
this_is_my_api_key
```

## To delete the API key:
```bash
$ python3 format-egress-ips.py --deleteAPIKey
Success
$ 
```

# Egress IPs
## To get Egress IPs
First make sure API key is set (see above)
Use the `--allEgressIPs` command.
```bash
$ python3 format-egress-ips.py --allEgressIPs
Location              serviceType         egress IP           Active/Reserved
Singapore             gp_gateway          123.234.123.124     active
Thailand              gp_gateway          119.256.139.101     active
Vietnam               gp_gateway          191.199.280.100     active
US Central            gp_gateway          103.191.878.100     active
```

If you want to leverage the `--apiKey` argument instead of using the options above, repeat the same command with `--apiKey` defined.
```bash
$ python3 format-egress-ips.py --apiKey aldkfjlaksji4u50198u09uef-a9udfb9ausdf --allEgressIPs
Location              serviceType         egress IP           Active/Reserved
Singapore             gp_gateway          123.234.123.124     active
Thailand              gp_gateway          119.256.139.101     active
Vietnam               gp_gateway          191.199.280.100     active
US Central            gp_gateway          103.191.878.100     active
```

## Convert egress IPs into comma separated values (csv) format
No output is displayed, but a file is created based on the argument supplied through --outputCsvFile
```bash
$ python3 format-egress-ips.py --allEgressIPs --outputCsvFile output.csv
```
Similarly as above, if you haven't defined an API key by using the `--setAPIKey`, you can use the `--apiKey` argument and pass it via stdin:
```bash
$ python3 format-egress-ips.py --apiKey aldkfjlaksji4u50198u09uef-a9udfb9ausdf --allEgressIPs --outputCsvFile output.csv
```


## Convert an existing json file into a formatted table
```bash
$ python3 format-egress-ips.py --fileName egress-ips.json
```

Example output:
```
Location              serviceType         egress IP           Active/Reserved
Singapore             gp_gateway          123.234.123.124     active
Thailand              gp_gateway          119.256.139.101     active
Vietnam               gp_gateway          191.199.280.100     active
US Central            gp_gateway          103.191.878.100     active
```

## Convert an existing json file into a csv file
```bash
$ python3 format-egress-ips.py --fileName egress-ips.json --outputCsvFile output.csv
```
