# query_idr
query Rapid7 IDR API with graphql

# NOTE:
The executables provided here were built with a nifty python package https://nuitka.net/. 

While I have no indication that there are security risks with the tool, I have not security tested them
and cannot assure you that they are safe.  USE AT YOUR OWN RISK!! 

# usage
```
$ python main.py --help
usage: query_idr.py [-h] --apikey APIKEY [--domain DOMAIN] [--proxies PROXIES]

options:
  -h, --help                     show this help message and exit
  --domain DOMAIN                The FQDN/IP for your InsightVM server (not full URL)
  --apikey APIKEY                The password for the username
  --proxies PROXIES              JSON structure specifying 'http' and 'https' proxy URLs
```


# example: look up host with vulnerability details
`python3 query_idr.py --api-key MyApiKey`<br>
`python3 query_idr.py --api-key MyApiKey --domain us.api.insight.rapid7.com`<br>

# references: 
https://us.api.insight.rapid7.com/graphql<br>

# related curl commands:
## GET THE ORGS:
curl -LkX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Accept-Version: kratos' -H 'X-Api-Key: MY_API_KEY' https://us.api.insight.rapid7.com/graphql -d '{"query": "query($first: Int!){organizations(first: $first){edges{node{id name}}}}", "variables": {"first": 10000}'

## GET THE FIRST PAGE:
curl -LkX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Accept-Version: kratos' -H 'X-Api-Key: MY_API_KEY' https://us.api.insight.rapid7.com/graphql -d '{"query": "query($orgId: String!, $first: Int!) {organization(id: $orgId) {assets(first: $first) {edges {cursor node {id host {vendor
description hostNames {name} primaryAddress {ip mac} attributes {key value} isEphemeral} publicIpAddress platform agent {agentStatus deployTime agentLastUpdateTime agentSemanticVersion}}}}}}", "variables": {"first": 10000, "orgId": "MY_ORG_ID"}}'

## GET SUBSEQUENT PAGES:
curl -LkX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Accept-Version: kratos' -H 'X-Api-Key: MY_API_KEY' https://us.api.insight.rapid7.com/graphql -d '{"query": "query($orgId: String!, $first: Int!, $cursor: String!) {organization(id: $orgId) {assets(first: $first, after: $cursor) {edges {cursor node {id host {vendor description hostNames {name} primaryAddress {ip mac} attributes {key value} isEphemeral } publicIpAddress platform agent { agentStatus deployTime agentLastUpdateTime agentSemanticVersion}}}}}}", "variables": {"first": 10000, "orgId": "MY_ORG_ID", "cursor": "MY_LAST_CURSOR"}}'
