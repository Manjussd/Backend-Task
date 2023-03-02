import urllib.parse
import json
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from google.oauth2.credentials import Credentials
from google.oauth2.client import OAuth2WebServerFlow
from googleapiclient.discovery import build

# Define your Google API credentials and scopes
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'YOUR_REDIRECT_URI'
SCOPE = 'https://www.googleapis.com/auth/calendar.readonly'

class GoogleCalendarInitView(View):
    def get(self, request):
        # Create the OAuth flow object
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        # Generate the authorization URL and redirect to it
        authorization_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorization_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Obtain the authorization code from the request
        authorization_code = request.GET.get('code')

        # Exchange the authorization code for an access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = urllib.parse.urlencode({
            'code': authorization_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }).encode('utf-8')
        token_request = urllib.request.Request(token_url, data=token_data)
        token_response = urllib.request.urlopen(token_request).read().decode('utf-8')
        token_json = json.loads(token_response)
        access_token = token_json['access_token']

        # Build the Google Calendar API client and fetch the list of events
        service = build('calendar', 'v3', credentials=Credentials(access_token))
        events_result = service.events().list(calendarId='primary', timeMin=datetime.utcnow().isoformat() + 'Z',
                                              maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        # Render the events in a template or return the events as a JSON response
        return HttpResponse(json.dumps({'events': events}), content_type='application/json')
