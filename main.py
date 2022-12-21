# This script was written and tested using python 3.9
from _setvars import *  # script to set/get needed creds etc
from _func import *  # My functions script
import json

# run call to get a fresh access token from the refresh token for this account
get_new_token = get_access_from_refresh(refr_token, cli_id, cli_sec, shard)

# set new access token var from last
if get_new_token.status_code == 200:
    cur_acc_token = get_new_token.json()['access_token']
    print('Got new access token!')
else:
    print('There was a problem getting an access token. Please check the info for this account and re-try!')

# run call to get all ACTIVE libDoc Templates into a list of objects
list_all = get_libdoc_active_list(cur_acc_token, shard, xapi_user_email, pg_sz)

# This section will check each libDoc for signatures, log and add to new array if there are no existing signatures
needs_sig_added = []

for doc_obj in list_all:
    # run function that returns lields JSON for this template
    fields_list = get_libdoc_fields(cur_acc_token, shard, doc_obj['id'], xapi_user_email)
    #check if there are any fields at all
    if 'fields' in fields_list.json():
        has_sig = 0
        this_obj = fields_list.json()['fields']
        # loop through existing fields for a signature field
        for field in this_obj:
            if 'contentType' in field and field['contentType'] == 'SIGNATURE':
                has_sig = 1
                print(f'Found signature in {doc_obj["id"]}, skipping this lib-Doc')
                log_skipped(account_identifier, doc_obj["id"], doc_obj["name"])
        if has_sig == 0:
            print(f'************* MISSING SIG - found no signature field in "{doc_obj["name"]}" with ID: {doc_obj["id"]}.')
            log_needs_sig(account_identifier,  doc_obj["id"], doc_obj["name"], "NO-SIG was found but template has fields")
            needs_sig_added.append({"libDocName": doc_obj["name"], "id": doc_obj["id"], "fields": this_obj})
    else:
        print(f'************* NO-FIELDS - Lib-Doc "{doc_obj["name"]}" with ID: {doc_obj["id"]} has NO fields')
        log_needs_sig(account_identifier, doc_obj["id"], doc_obj["name"], "NO-FIELDS were found at all")
        needs_sig_added.append({"libDocName": doc_obj["name"], "id": doc_obj["id"], "fields": []})


