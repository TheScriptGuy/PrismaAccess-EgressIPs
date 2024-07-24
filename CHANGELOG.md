# PrismaAccess-Egress IPs Changelog
## 2024-07-24 - 0.16
* Added capabilities to powershell script to ask for API key and prod environment if they are not set from the command line arguments.

## 2024-07-19 - 0.15
* Fixed a powershell [bug](https://github.com/TheScriptGuy/PrismaAccess-EgressIPs/issues/10) as identified by [sm-palo](https://github.com/sm-palo)

## 2024-01-17
* Added Windows powershell script to get public egress IPs. Powershell usage available [here](https://github.com/TheScriptGuy/PrismaAccess-EgressIPs/blob/main/README-powershell.md)

## 2023-04-20 - 0.13
* Added better handling for [unauthorized messages](https://github.com/TheScriptGuy/PrismaAccess-EgressIPs/issues/7) from API.

## 2023-01-30 - 0.12
* Found the pesky stdout formatting [bug](https://github.com/TheScriptGuy/PrismaAccess-EgressIPs/issues/4) and squashed it.

## 2023-01-30 - 0.11
## New feature
* added `--outputEdlFile` argument to send IP's only directly to file.

## 2022-12-14 - 0.10
## New feature
* added `--allLoopbackIPAddresses` to show the loopback IP addresses of your environment.

## 2022-09-23 - 0.09
## New feature
* Added `--apiKey` argument to allow the API key to be passed via stdin. See [README.md](https://github.com/TheScriptGuy/PrismaAccess-EgressIPs/blob/main/README-python.md) for usage.

## 2022-04-28 - 0.08
## Fixes
* Added some better error handling in case a json object is not returned.

## 2022-04-27 - 0.07
## Fixes
* Rewriting code to align with best practices.

## 2022-04-25 - 0.06
## Changes
* Added `--environment` argument to help querying between different environments. By default it queries the prod environment.


## 2022-04-22 - 0.05
## Fixes
* Added better handling for URL requests
* Fixed bug with Prisma Access API Prod URL

## 2022-04-21 - 0.04
## Fixes
* Fixed issue relating to csv argument.


## 2022-04-20
## Changes
* Added ability to query API to get IP addresses from Prisma Access.
* Added API key management arguments.
