import requests  # REQUIRES python "requests" install via pip - see https://requests.readthedocs.io/en/latest/
import sys
import os


def get_access_from_refresh(token, client_id, client_sec, shard):
    '''
    This will use the refresh token and other creds to get a new access token for this account
    :param token: string - This is access token or an integration key could be set static and used instead
    :param client_id: string - The ClientI from the oAuth app needed to get new access token
    :param client_sec: string - The "Client Secret" from the oAuth app
    :param shard: string - This is the "geo-shard" on the Sign infrastructure where
    :return: JSON - JSON object containing the access-token and the life-time (normally 3600 seconds)
    '''
    api_url = 'https://api.' + shard + '.adobesign.com/oauth/v2/refresh'
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "User-Agent": "test-script888"
    }
    payload = f'refresh_token={token}&client_id={client_id}&client_secret={client_sec}&grant_type=refresh_token'
    try:
        response_here = requests.request("POST", api_url, headers=headers, data=payload)
        print(response_here.text)
    except:
        response_here = "There was an error with the call or data"

    return response_here


def get_libdoc_fields(token, shard, libdoc_id, xapi_email):
    fields_url = f'https://api.{shard}.adobesign.com/api/rest/v6/libraryDocuments/{libdoc_id}/formFields'
    headers = {
        "User-Agent": "test-script888",
        "Authorization": "Bearer " + token,
        "x-api-user": "email:"+ xapi_email
    }
    try:
        response = requests.request("GET", fields_url, headers=headers)
    except requests.exceptions.HTTPError as e:
        print(" ERROR ".center(80, "-"))
        print(e, file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(e, file=sys.stderr)
    return response


def get_libdoc_active_list(token, shard, xapi_email, pg_sz):
    id_list = []
    next_cursor = 'na'
    ld_url: str = f'https://api.{shard}.adobesign.com/api/rest/v6/libraryDocuments?pageSize={pg_sz}'
    while next_cursor:
        headers = {
            "User-Agent": "test-script888",
            "Authorization": "Bearer " + token,
            "x-api-user": "email:" + xapi_email
        }
        try:
            response = requests.request("GET", ld_url, headers=headers)
        except requests.exceptions.HTTPError as e:
            print(" ERROR ".center(80, "-"))
            print(e, file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(e, file=sys.stderr)

        if 'libraryDocumentList' in response.json():
            for libDoc in response.json()['libraryDocumentList']:
                if libDoc['status'] == 'ACTIVE':
                    ldid = libDoc['id']
                    ldnm = libDoc['name']
                    print(f'adding lib doc {ldid}\n')
                    id_list.append({"id": ldid, "name": ldnm})

        if 'nextCursor' in response.json()['page']:
            next_cursor = response.json()['page']['nextCursor']
            ld_url: str = f'https://api.{shard}.adobesign.com/api/rest/v6/libraryDocuments?pageSize={pg_sz}&cursor={next_cursor}'
        else:
            break

    return id_list

def log_skipped(account_id, template_id, template_name):
    with open(account_id + '_skipped_templates.csv', 'a') as f:
        f.write(f'"{template_id}", "{template_name}", "Found signature field, skipping"\n')

def log_needs_sig(account_id, template_id, template_name, f_text):
    with open(account_id + '_needs_sig_field.csv', 'a') as f:
        f.write(f'"{template_id}", "{template_name}", "{f_text}"\n')






