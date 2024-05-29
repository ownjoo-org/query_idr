import argparse
import json

from typing import Optional, Union, Generator
from requests import Session, Response

PAGE_SIZE: int = 1000

ORGANIZATIONS_QUERY = '''
query($first: Int!){
  organizations(first: $first){
    edges{ 
        node{
                id
            }
        } 
    }
}
'''

FIRST_QUERY: str = 'query($orgId: String!, $first: Int!)'
FIRST_ASSETS: str = 'assets(first: $first)'
CURSOR_QUERY: str = 'query($orgId: String!, $first: Int!, $cursor: String!)'
CURSOR_ASSETS: str = 'assets(first: $first, after: $cursor)'

ASSETS_QUERY = '''
{query} {{
  organization(id: $orgId) {{
    {assets} {{
      edges {{
        cursor
        node {{
          id
          host {{
            vendor
            description
            hostNames {{
              name
            }}
            primaryAddress {{
              ip
              mac
            }}
            attributes {{
              key
              value
            }}
            isEphemeral
          }}
          publicIpAddress
          platform
          agent {{
            agentStatus
            deployTime
            agentLastUpdateTime
            agentSemanticVersion
          }}
        }}
      }}
    }}
  }}
}}
'''


def list_organizations(session: Session, domain: str) -> Generator[str, None, None]:
    try:
        body_params: dict = {
            'query': ORGANIZATIONS_QUERY,
            'variables': {'first': PAGE_SIZE},
        }
        resp_orgs_query: Response = session.post(
            url=f'https://{domain}/graphql',
            json=body_params,
            proxies=proxies,
        )
        resp_orgs_query.raise_for_status()
        data_query: dict = resp_orgs_query.json()
        edges: list = data_query.get('data').get('organizations').get('edges')
        for edge in edges:
            yield edge.get('node').get('id')
    except Exception as exc_query:
        print(f'{exc_query}')
        raise exc_query


def list_assets_per_org(session: Session, domain: str, org_id: str) -> Optional[dict]:
    cursor: Optional[str] = None
    try:
        # first page with no cursor
        body_params: dict = {
            'query': ASSETS_QUERY.format(query=FIRST_QUERY, assets=FIRST_ASSETS),
            'variables': {
                'first': PAGE_SIZE,
                'orgId': org_id
            },
        }

        is_done: bool = False
        while not is_done:
            resp_asset_query: Response = session.post(
                url=f'https://{domain}/graphql',
                json=body_params,
                proxies=proxies,
            )
            resp_asset_query.raise_for_status()
            data_query: dict = resp_asset_query.json()
            edges = data_query.get('data').get('organizations').get('assets').get('edges')
            for edge in edges:
                cursor = edge.get('cursor')
                yield edge.get('node')
            is_done = len(edges) < PAGE_SIZE
            body_params['query'] = ASSETS_QUERY.format(query=CURSOR_QUERY, assets=CURSOR_ASSETS)
            body_params['variables']['cursor'] = cursor

    except Exception as exc_query:
        print(f'{exc_query}')
        raise exc_query


def main(
        domain: str,
        api_key: str,
        proxies: Optional[dict] = None,
) -> Union[None, str, list, dict]:
    session = Session()

    headers: dict = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; Charset=UTF-8',
        'Accept-Version': 'kratos',
        'X-Api-Key': api_key,
    }
    session.headers = headers
    session.proxies = proxies

    try:
        for org_id in list_organizations(session=session, domain=domain):
            if org_id:
                yield from list_assets_per_org(session=session, domain=domain, org_id=org_id)
    except Exception as exc_all:
        print(exc_all)
        raise exc_all


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--domain',
        type=str,
        required=False,
        help="The FQDN/IP for your InsightVM host (not full URL)",
        default='us.api.insight.rapid7.com'
    )
    parser.add_argument(
        '--api-key',
        default=None,
        type=str,
        required=True,
        help='The API key for you Insight IDR account',
    )
    parser.add_argument(
        '--proxies',
        type=str,
        required=False,
        help="JSON structure specifying 'http' and 'https' proxy URLs",
    )

    args = parser.parse_args()

    proxies: Optional[dict] = None
    if proxies:
        try:
            proxies: dict = json.loads(args.proxies)
        except Exception as exc_json:
            print(f'WARNING: failure parsing proxies: {exc_json}: proxies provided: {proxies}')

    result = main(
        domain=args.domain,
        api_key=args.password,
        proxies=proxies,
    )

    if result:
        print(json.dumps(result, indent=4))
    else:
        print('No results found')
