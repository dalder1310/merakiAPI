import socket
import meraki
import time

dashboard = meraki.DashboardAPI(suppress_logging=True)
domains = [".com",".net",".org"]

# UnComment the below line if you want to hardcode the APIKey.
# You'll also need to pass the variable into the API call on line 38
# API_KEY = ''

####################################
# The below function has the logic to do a look up of the S2S name and return the IP result
# It gets passed in the S2S name that should be in the form of a Dynamic Domain
# It then runs a lookup on that Dynamic Domain and either returns the IP if resolvable or just 'none'. 
# The result of the lookup is passed back to the for loop
###################################

def comparetoDDNS(vpnTagReceived):
    print("S2S Peers Name - " + vpnTagReceived)
    try:
        print('Resolving : ' + vpnTagReceived)
        returnedIP = socket.gethostbyname(vpnTagReceived)
    except:
        print('Unable to resolve: ' + vpnTagReceived)
        returnedIP = "None"
    print("This is the S2S Name " + vpnTagReceived + " - This is the corresponding checked IP = " + returnedIP)
    return(returnedIP)


####################################
# Manually set the Org ID in the code. 
# We then use the Meraki SDK to return the ThirdPartyVpn details needed
###################################

while(True):
    # Add the orgID for your organisation below.
    orgId = 'ORGIDHere'
    apiResponse = dashboard.appliance.getOrganizationApplianceVpnThirdPartyVPNPeers(orgId)

# If in the below for loop there is an IP that changes this boolean will get set to true
    peerIpChange = False


####################################
# The for loop runs through the VPN peers in the API response 
# It will then check if the name field is a domain using the variable declared at the top. 
# If it is it will get passed to the comparetoDDNS function
# If the returned result is an IP it will write that back to the API response and move onto the next peer
###################################

    for net in apiResponse["peers"]:
        vpnName = net["name"]
        vpnIp = net["publicIp"]

        if any(domain in vpnName for domain in domains):
                checkedIp = comparetoDDNS(vpnName)
                print(isinstance(checkedIp, str))
                if checkedIp == "None":
                    print("Invalid DDNS Tag")
                elif checkedIp != vpnIp:
                    net["publicIp"] = checkedIp
                    peerIpChange = True
                    print("Changed Json IP Address")
                else:
                    print("Match Found")


####################################
# Once all the the peers have been run through above, the below checks if peerIpChange is set to True 
# which would only happen if there is a change in public IP for a peer
#
# If true, then it will use the update third party VPN peers API Put to updated the peers
# You must pass in the orgId and a variable that holds the peers information in Json format

#If peerIpChange is false because there hasn't been any IP changes, then nothing happens
###################################

    if peerIpChange:
        print("Ready to send API Update to S2SVPN")
        print("There has been a change to the S2S VPN Public Ip List!!!")
        print("")
        print("Sending API Put.......")
        peers = apiResponse["peers"]
        putApiResponse = dashboard.appliance.updateOrganizationApplianceVpnThirdPartyVPNPeers(orgId, peers)
        print(putApiResponse)
        time.sleep(300)
    else:
        print("No Updates to the S2S List")
        time.sleep(300)

