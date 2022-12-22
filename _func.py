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
        
        

def add_sig_to_last_page(token, shard, xapi_email, template_id, coord_x, coord_y, testit=1):
    '''
    This function does a few things.  It checks the "docs" in the library template to find the last page for this 
    template. It gets the existing fields if there are any, as well as the current ETag value needed for the PUT. It
    then adds the new signature field to the last page of the template at the X,Y coordinates specified.
    :param token: string - This is access token or an integration key could be set static and used instead
    :param shard: string - This is the "geo-shard" on the Sign infrastructure where
    :param xapi_email: email address - the email of the person whos the owner/creator of the libarary template being edited
    :param template_id: string - the library template ID being edited
    :param coord_x: integer - pixels from the top of the page measured top to bottom
    :param coord_y: integer - pixels from the left of the page measured from left to right
    :param testit: bool 1 or 0 - will this be a test run or should this call actually change the template
    :return: 
    '''
    tot_pages = 0
    docs_url = f'https://api.{shard}.adobesign.com/api/rest/v6/libraryDocuments/{template_id}/documents'
    headers = {
        "User-Agent": "test-script888",
        "Authorization": "Bearer " + token,
        "x-api-user": "email:" + xapi_email
    }
    try:
        response = requests.request("GET", docs_url, headers=headers)
    except requests.exceptions.HTTPError as e:
        print(" ERROR ".center(80, "-"))
        print(e, file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(e, file=sys.stderr)

    if 'documents' in response.json():
        docs_list = response.json()['documents']
        for doc in docs_list:
            tot_pages = tot_pages + int(doc["numPages"])
        fields_url = f'https://api.{shard}.adobesign.com/api/rest/v6/libraryDocuments/{template_id}/formFields'

        print('#################################')
        print(f'templateID = {template_id}')
        # print(response.text)
        print(f'This lib-doc has {len(docs_list)} items with {tot_pages} total page/s.')
        try:
            response = requests.request("GET", fields_url, headers=headers)
            print(response.json())
        except requests.exceptions.HTTPError as e:
            print(" ERROR ".center(80, "-"))
            print(e, file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(e, file=sys.stderr)
        if 'code' not in response.json():
            e_tag = response.headers["Etag"]
            fields_obj = []
            if 'fields' in response.json():
                print('found some fields in template, getting existing into fields object.')
                for field in response.json()['fields']:
                    fields_obj.append(field)
                print(fields_obj)
            print('Adding field to end of template.')
            new_sig_field = {
                "borderStyle": "SOLID",
                "visible": True,
                "inputType": "SIGNATURE",
                "fontSize": 12.0,
                "alignment": "LEFT",
                "displayFormatType": "DEFAULT",
                "masked": False,
                "contentType": "SIGNATURE",
                "required": True,
                "minLength": -1,
                "maxLength": 40,
                "minValue": -1.0,
                "maxValue": -1.0,
                "name": "SignatureNew1",
                "locations": [
                    {
                        "pageNumber": int(tot_pages),
                        "top": coord_x,
                        "left": coord_y,
                        "width": 225,
                        "height": 46
                    }
                ],
                "assignee": "recipient0"
            }
            fields_obj.append(new_sig_field)
            new_put_body = json.dumps({
                'fields': fields_obj
            })

    if testit == 1:
        print(f'##########   TEST ######### Since this is a test ')
        print("This will not be calling the PUT to add the signature fields to this template's last page.")
        print("If it was not a test it would have used the below to add-append the new field.")
        print('NEW - PUT ----- Body -----')
        print(new_put_body)
    if testit == 0:
        headers = {
            "User-Agent": "test-script888",
            "Authorization": "Bearer " + token,
            "x-api-user": "email:" + xapi_email,
            "Content-Type": "application/json",
            "If-None-Match": e_tag,
        }
        fields_url = f'https://api.{shard}.adobesign.com/api/rest/v6/libraryDocuments/{template_id}/formFields'
        try:
            response = requests.request("PUT", fields_url, headers=headers, data=new_put_body)
            print(response.json())
        except requests.exceptions.HTTPError as e:
            print(" ERROR ".center(80, "-"))
            print(e, file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(e, file=sys.stderr)
        if response.status_code == 200:
            print(f'PUT was success. it got a code of {response.status_code}')
        else:
            print(f'There was a problem!')
            print(f'{response.text}')






