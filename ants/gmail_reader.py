from google.oauth2 import service_account

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
credentials = service_account.Credentials.from_service_account_file(
    './gmail.key')

scoped_credentials = credentials.with_scopes(
    [SCOPES])

# from __future__ import print_function
# from googleapiclient.discovery import build
# from httplib2 import Http
# from oauth2client import file, client, tools

# # If modifying these scopes, delete the file token.json.
# SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

# def main():
#     """Shows basic usage of the Gmail API.
#     Lists the user's Gmail labels.
#     """
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     store = file.Storage('token.json')
#     creds = store.get()
#     if not creds or creds.invalid:
#         flow = client.flow_from_clientsecrets('gmail.key', SCOPES)
#         creds = tools.run_flow(flow, store)
#     service = build('gmail', 'v1', http=creds.authorize(Http()))

#     # Call the Gmail API
#     results = service.users().labels().list(userId='me').execute()
#     labels = results.get('labels', [])

#     if not labels:
#         print('No labels found.')
#     else:
#         print('Labels:')
#         for label in labels:
#             print(label['name'])

# if __name__ == '__main__':
#     main()