# Powershell Arguments
## Mandatory argument:
* `-api_key` this is the API key used to authenticate.
  - To get the API key:
    - [Panorama](https://docs.paloaltonetworks.com/prisma/prisma-access/preferred/2-2/prisma-access-panorama-admin/prisma-access-overview/retrieve-ip-addresses-for-prisma-access)
    - [Cloud Managed](https://docs.paloaltonetworks.com/prisma/prisma-access/prisma-access-cloud-managed-admin/prisma-access-service-infrastructure/retrieve-ip-addresses-to-allow-for-prisma-access) 

## Default Argument:
* `-dataType EgressIPs`. This will show all the public egress IP addresses for the Prisma Access tenant.

## Alternate outputs for `-dataType`:
* `ActiveIPOnboardedMobileUserLocations` - Shows all the public egress IPs for mobile users.
* `ActiveMobileUserAddresses` - Shows all the public egress IPs for mobile users.
* `RemoteNetworkAddresses` - Shows all public egress IPs for Remote Networks
* `CleanPipeAddresses` - Shows all public egress IPs for Clean Pipe
* `ExplicitProxyAddresses` - Shows all public egress IPs for Explicit Proxy

## Optional Argument
* `-environment` - This defaults to prod. Adust to the correct environment where applicable.

# Example Usage
## All egress IPs for Prisma Access
```powershell
PS1 C:\>.\format-egress-ips.ps1 -api_key <api_key>

Zone              ServiceType    Address         AddressType
----              -----------    -------         -----------
US Northwest      remote_network 123.264.123.112 active
US Northwest      gp_gateway     123.264.123.113 active
US Northwest      gp_gateway     123.264.123.114 active
US Northwest      swg_proxy      123.264.123.116 active
...
```

## Loopback IP addresses
```powershell
PS1 C:\>.\format-egress-ips.ps1 -api_key <api_key> -dataType loopback_ip

Location          Type                Loopback IP
--------          ----                -----------
US Northwest      gpcs_gp_gw          192.168.0.10
US East           gpcs_gp_portal      192.168.0.11
US West           gpcs_gp_portal      192.168.0.2
CloudGenix_Branch gpcs_remote_network 192.168.0.3
```
