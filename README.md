# PrismaAccess-EgressIPs
Provide the egress IPs for the Prisma Access service in a formatted context

By default the file the script looks for is `egress-ips.json`.

I've only tested this with Mobile Users.

```bash
$ python3 format-egress-ips.py -h
usage: format-egress-ips.py [-h] [--fileName FILENAME]

Format Egress IPs 0.01

optional arguments:
  -h, --help           show this help message and exit
  --fileName FILENAME  List of json formatted egress IPs
```


Example output:
```
Location              serviceType         egress IP           Active/Reserved
Singapore             gp_gateway          123.234.123.124     active
Thailand              gp_gateway          119.256.139.101     active
Vietnam               gp_gateway          191.199.280.100     active
US Central            gp_gateway          103.191.878.100     active
```
