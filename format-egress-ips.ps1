param (
    [string]$api_key = $null,
    [string]$environment = $null,
    [string]$dataType = "EgressIPs",
    [string]$outputFile
)

# Check if api_key parameter is empty
if ([string]::IsNullOrEmpty($api_key)) {
    # Prompt user for api key input
    $api_key = Read-Host "Enter API Key"
    if ([string]::IsNullOrWhiteSpace($api_key)) {
        Write-Host "Please enter a valid API key."
        exit
    }
}

# Check if environment parameter is empty
if ([string]::IsNullOrEmpty($environment)) {
    # Prompt user for environment input
    $environment = Read-Host "Environment (defaults to prod)"
    if ([string]::IsNullOrWhiteSpace($environment)) {
        $environment = "prod"  # Set default value if user input is empty
    }
}

# Function to send API Request
function Send-APIRequest($uri, $method, $body, $headers) {
    try {
        $response = Invoke-RestMethod -Uri $uri -Method $method -Body $body -Headers $headers -ContentType "application/json"
        return $response
    } catch {
        Write-Error "Error: $_"
        exit
    }
}

$addressType = "loopback_ip"

# API Headers
$headers = @{
    "header-api-key" = $api_key
}

# Data type payloads
$dataPayloads = @{
    "EgressIPs" = '{"serviceType": "all", "addrType": "all", "location": "all"}'
    "ActiveReservedOnboardedMobileUserLocations" = '{"serviceType": "gp_gateway", "addrType": "all", "location": "deployed"}'
    "ActiveIPOnboardedMobileUserLocations" = '{"serviceType": "gp_gateway", "addrType": "active", "location": "deployed"}'
    "ActiveMobileUserAddresses" = '{"serviceType": "gp_gateway", "addrType": "all", "location": "all"}'

    # Remote Network IP addresses
    "RemoteNetworkAddresses" = '{"serviceType": "remote_network", "addrType": "all", "location": "all"}'

    # Clean Pipe IP addresses
    "CleanPipeAddresses" = '{"serviceType": "clean_pipe", "addrType": "all", "location": "all"}'

    # Explicit Proxy IP addresses
    "ExplicitProxyAddresses" = '{"serviceType": "swg_proxy", "location": "deployed", "addrType": "auth_cache_service"}'
}

# Loopback types
$fwTypes = @('gpcs_gp_gw', 'gpcs_gp_portal', 'gpcs_remote_network')

function ConvertTo-CustomJson($resultData) {
    $jsonOutput = @()
    foreach ($item in $resultData) {
        foreach ($detail in $item.address_details) {
            $jsonObj = @{
                Zone        = $item.zone
                ServiceType = $detail.serviceType
                Address     = $detail.address
                AddressType = $detail.addressType
            }
            $jsonOutput += $jsonObj
        }
    }
    return $jsonOutput | ConvertTo-Json -Depth 10
}

function Display-FormattedResult($result) {
    $outputTable = @()
    foreach ($item in $result) {
        $zone = $item.zone
        # Assuming address_details is an array of objects
        foreach ($detail in $item.address_details) {
            $row = New-Object PSObject -Property @{
                Zone        = $zone
                ServiceType = $detail.serviceType
                Address     = $detail.address
                AddressType = $detail.addressType
            }
            $outputTable += $row
        }
    }
    $outputTable | Format-Table -Property Zone, ServiceType, Address, AddressType -AutoSize
}

function Display-LoopbackIps($result) {
    $outputTable = @()
    foreach ($item in $result) {
        $fwType = $item.result.fwType
        foreach ($addr in $item.result.addrList) {
            $splitAddr = $addr -split ':'
            $location = $splitAddr[0]
            $ipAddress = $splitAddr[1]
            $row = New-Object PSObject -Property @{
                Type = $fwType
                Location = $location
                "Loopback IP" = $ipAddress
            }
            $outputTable += $row
        }
    }
    return $outputTable
}

# Main Logic
if ($dataType -eq "loopback_ip") {
    $loopbackResults = @()
    foreach ($fwType in $fwTypes) {
        $loopbackUri = "https://api.$environment.datapath.prismaaccess.com/getAddrList/latest?fwType=$fwType&addrType=loopback_ip"
        $result = Send-APIRequest -uri $loopbackUri -method 'GET' -headers $headers
        $loopbackResults += $result
    }
    if ($outputFile) {
        $ext = [System.IO.Path]::GetExtension($outputFile)
        switch ($ext) {
            ".json" {
                $loopbackResults | ConvertTo-Json -Depth 10 | Out-File $outputFile
            }
            ".csv"  {
                $csvOutput = Display-LoopbackIps -result $loopbackResults
                $csvOutput | ConvertTo-Csv -NoTypeInformation | Out-File $outputFile
            }
            ".txt"  {
                # Extracting only the IP addresses for text file output
                $txtOutput = $loopbackResults | ForEach-Object {
                    $_.result.addrList | ForEach-Object {
                        ($_ -split ':')[1]
                    }
                }
                $txtOutput -join "`r`n" | Out-File $outputFile
            }
            default { 
                Write-Error "Unsupported file extension." 
            }
        }
    } else {
        Display-LoopbackIps -result $loopbackResults | Format-Table -AutoSize
    }
} else {
    $apiUri = "https://api.$environment.datapath.prismaaccess.com/getPrismaAccessIP/v2"
    $body = $dataPayloads[$dataType]
    $result = Send-APIRequest -uri $apiUri -method 'POST' -body $body -headers $headers

    # Extract only the 'result' part of the response
    $resultData = $result.result

    # Output Handling based on file extension
    if ($outputFile) {
        $ext = [System.IO.Path]::GetExtension($outputFile)
        switch ($ext) {
            ".json" {
                # Directly write the raw JSON response to the file
                $result | ConvertTo-Json -Depth 10 | Out-File $outputFile
            }
            ".csv"  { 
                $csvOutput = foreach ($item in $resultData) {
                    foreach ($detail in $item.address_details) {
                        [PSCustomObject]@{
                            Zone        = $item.zone
                            ServiceType = $detail.serviceType
                            Address     = $detail.address
                            AddressType = $detail.addressType
                        }
                    }
                }
                $csvOutput | Export-Csv -Path $outputFile -NoTypeInformation
            }
            ".txt"  { 
                $txtOutput = $resultData | ForEach-Object {
                    $_.address_details | ForEach-Object { $_.address }
                }
                $txtOutput -join "`r`n" | Out-File $outputFile
            }
            default { 
                Write-Error "Unsupported file extension." 
            }
        }
    }
    else {
        Display-FormattedResult -result $resultData
    }
}
