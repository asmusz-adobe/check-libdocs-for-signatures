import os
# ********
cli_sec = 'YbIG*** Your oAuth app cli_sec ***FAd5'
# cli_sec = os.environ.get('SIGN_CLI_SEC')

cli_id = 'CBJG*** Your oAuth app cli ID ***_9D'
# cli_id = os.environ.get('SIGN_CLI_ID')

account_identifier = '*** someString to identify the account ***'
# account_identifier = os.environ.get('SIGN_ACCOUNT_IDENT')

refr_token = '3AAAG*** Your account\'s oAuth app refresh token ***Ww*'
# refr_token = os.environ.get('SIGN_REFR_TOKEN')

pg_sz = 100  # Sets page size for bathes of libDoc IDs

shard = 'na4' # the geo-shard where your account lives
# shard = os.environ.get('SIGN_SHARD')

xapi_user_email = '*** libDoc creators email address ***'
# xapi_user_email = os.environ.get('SIGN_XAPI_EMAIL')

admin_user_email = '*** not used but might be needed later ***'
# admin_user_email = os.environ.get('SIGN_ADMIN_EMAIL')
