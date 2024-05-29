# query_idr
query Rapid7 IDR API with graphql

# usage
```
$ python main.py --help
usage: query_idr.py [-h] --api-key APIKEY [--domain DOMAIN] [--proxies PROXIES]

options:
  -h, --help                     show this help message and exit
  --domain DOMAIN                The FQDN/IP for your InsightVM server (not full URL)
  --api-key APIKEY               The password for the username
  --proxies PROXIES              JSON structure specifying 'http' and 'https' proxy URLs
```


# example: look up host with vulnerability details
`python3 query_idr.py --api-key MyApiKey`
`python3 query_idr.py --api-key MyApiKey --domain us.api.insight.rapid7.com`

# references: 
https://us.api.insight.rapid7.com/graphql
