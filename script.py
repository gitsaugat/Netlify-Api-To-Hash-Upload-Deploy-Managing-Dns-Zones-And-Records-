import requests
import json
import os
import zipfile
from hashlib import sha256, sha1
import random
import time

ACCESS_TOKEN = ""
URLS = {
    "all_urls_and_auth_check": "https://api.netlify.com/api/v1/",
    "get_and_create_site":  "https://api.netlify.com/api/v1/sites",
}


def create_site(url: str, auth_token: str, site_name: str):

    response = requests.post(
        url=url, headers={"Authorization": auth_token, 'name': site_name})
    if response.status_code != 201:
        print(response.json())
    else:
        data = response.json()
        return data


def update_site(auth_token: str, www_domain: str, domain: str, site_id: str):
    response = requests.patch(f'https://api.netlify.com/api/v1/sites/{site_id}', headers={
        'Authorization': auth_token
    }, json={
        "custom_domain": www_domain,
        "domain_aliases": [
            domain
        ],
        'managed_dns': True
    })

    configure_dns_for_site = requests.put(f'https://api.netlify.com/api/v1/sites/{site_id}/dns',
                                          headers={
                                              'Authorization': auth_token
                                          },
                                          json={
                                              "dns_servers": [
                                                  "dns1.p03.nsone.net",
                                                  "dns2.p03.nsone.net",
                                                  "dns3.p03.nsone.net",
                                                  "dns4.p03.nsone.net",
                                              ]
                                          }
                                          )
    return {
        "update_site": {
            "status_code": response.status_code,
            "response": response.json()
        },
        "configure_dns_for_site": {
            "status_code": configure_dns_for_site.status_code,
            "response": configure_dns_for_site.json()
        }
    }


def check_and_pass_authorization(url: str, auth_token: str):
    response = requests.get(
        url=url, headers={"Authorization": auth_token})
    if response.status_code == 200:
        return True
    else:
        return False


def list_sites(url: str, auth_token: str):
    # url 'https://api.netlify.com/api/v1/sites'
    response = requests.get(url, headers={"Authorization": auth_token})
    data = response.json()
    sites = {

    }
    for d in data:
        sites[d['name']] = d['id']

    return sites


def hash_files():
    data = {'files': {}}
    path = os.path.join('assets')
    files_to_hash = os.listdir(path=path)

    for f in files_to_hash:
        filname = f'{f}'
        with open(f'{path}/{f}', 'rb') as stream:
            content = stream.read()
            hashed = sha1(content).hexdigest()
            data['files'][filname] = hashed

    return data


def upload_hashed_files(url: str, auth_token: str, data: dict):
    upload_url = url
    res = requests.post(url, headers={'Authorization': auth_token}, json=data)
    if res.status_code != 200:
        print(res.json())
    else:
        data = res.json()
        deploy_id = data['id']
        path = os.path.join('assets')
        files_to_hash = os.listdir(path=path)

        for f in files_to_hash:
            url = f'https://api.netlify.com/api/v1/deploys/{deploy_id}/files/{f}'
            hahshed = sha1(f.encode()).hexdigest()
            content_type = 'application/octet-stream'
            filepath = os.path.join(path, f)
            with open(filepath, 'rb') as stream:
                file_data = stream.read()
                res = requests.put(url, headers={
                                   'Authorization': auth_token, 'content-type': content_type}, data=file_data)
                if res.status_code != 200:
                    raise ValueError(res.json())


def upload_zipped_file(url: str, auth_token: str):
    headers = {}
    headers['Content-Type'] = 'application/zip'
    url = f'https://api.netlify.com/api/v1/{site_id}/deploys'
    domain_dir = os.path.join('assets')
    name = f'{str(random.random())}.zip'
    with zipfile.ZipFile(name, 'w') as ZipMe:
        for f in os.listdir(domain_dir):
            filepath = os.path.join(domain_dir, f)
            ZipMe.write(filepath)

    res = requests.post(url, headers=headers,
                        data='')
    print(res.content)


def get_dns_for_site(site_id: str, auth_token: str):
    url = f'https://api.netlify.com/api/v1/sites/{site_id}/dns'
    response = requests.get(url, headers={'Authorization': auth_token})
    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def configure_dns_for_site(site_id: str, auth_token: str):
    url = f'https://api.netlify.com/api/v1/sites/{site_id}/dns'
    response = requests.put(url, headers={'Authorization': auth_token})
    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def get_dns_zones(auth_token: str):
    response = requests.get(
        "https://api.netlify.com/api/v1/dns_zones", headers={'Authorization': auth_token})
    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def get_dns_zone(auth_token: str, zone_id: str):
    response = requests.get(f"https://api.netlify.com/api/v1/dns_zones/{zone_id}",
                            headers={
                                'Authorization': auth_token
                            },
                            )
    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def delete_dns_zone(auth_token: str, zone_id: str):
    response = requests.delete(f"https://api.netlify.com/api/v1/dns_zones/{zone_id}",
                               headers={
                                   'Authorization': auth_token
                               },
                               )

    return{
        "status_code": response.status_code,
        "body": response.json()
    }


def create_dns_zons(auth_token: str, site_id: str, name: str, account_slug: str):
    response = requests.post("https://api.netlify.com/api/v1/dns_zones", headers={
        'Authorization': auth_token,
    }, json={
        "account_slug": account_slug,
        "site_id": site_id,
        "name": name,
    })
    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def get_dns_records(auth_token: str, zone_id: str):
    response = requests.get(f'https://api.netlify.com/api/v1/dns_zones/{zone_id}/dns_records',
                            headers={
                                'Authorization': auth_token,
                            }
                            )

    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def create_dns_record(auth_token: str, zone_id: str, hostname: str, value: str, record_type: str):
    response = requests.post(f'https://api.netlify.com/api/v1/dns_zones/{zone_id}/dns_records',
                             headers={
                                 'Authorization': auth_token
                             },
                             json={
                                 "type": record_type,
                                 "hostname": hostname,
                                 "value": value,
                                 "ttl": 3600,
                             }

                             )
    return {
        "status_code": response.status_code,
        "response": response.json()
    }


def delete_dns_record(access_token: str, zone_id: str, dns_record_id: str):
    response = requests.delete(f'https://api.netlify.com/api/v1/dns_zones/{zone_id}/dns_records/{dns_record_id}',
                               headers={
                                   'Authorization': access_token
                               }
                               )
    return {
        'status_code': response.status_code,
        'response': response.json()
    }


is_authorized = check_and_pass_authorization(
    URLS["all_urls_and_auth_check"], ACCESS_TOKEN)


if is_authorized:
    pass
    # every function calls and variable declaration goes here
