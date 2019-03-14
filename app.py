import csv
import requests
from datetime import datetime, timedelta

from flask import Flask, render_template, request
from whitenoise import WhiteNoise
from werkzeug.contrib.cache import SimpleCache

import settings


app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

cache = SimpleCache()
hubstaff_auth_endpoint = '/auth'
hubstaff_team_report_endpoint = '/custom/by_date/team'
AUTH_TOKEN_CACHE_KEY = 'auth-token-cache-key-{0}/{1}'.format(
    settings.HUBSTAFF_EMAIL, settings.HUBSTAFF_PASSWORD)


def get_auth_token():
    auth_token = cache.get(AUTH_TOKEN_CACHE_KEY)
    if auth_token is None:
        hubstaff_auth_headers = {'App-Token': settings.HUBSTAFF_APP_TOKEN}
        hubstaff_auth_params = {
            'email': settings.HUBSTAFF_EMAIL,
            'password': settings.HUBSTAFF_PASSWORD
        }
        hubstaff_auth_url = '{0}{1}'.format(
            settings.HUBSTAFF_API_BASE_ENDPOINT, hubstaff_auth_endpoint)
        print hubstaff_auth_url
        api_hubstaff_response = requests.post(
            hubstaff_auth_url,
            data=hubstaff_auth_params,
            headers=hubstaff_auth_headers)
        assert(api_hubstaff_response.status_code != 401)
        assert(api_hubstaff_response.status_code != 403)

        context = api_hubstaff_response.json()
        auth_token = context['user']['auth_token']
        cache.set(AUTH_TOKEN_CACHE_KEY, auth_token)
    return auth_token


@app.route('/', methods=['GET'])
def fetch_data_view():
    auth_token = get_auth_token()
    yesterday_date = datetime.now() - timedelta(days=1)
    yesterday_date_str = yesterday_date.strftime('%Y-%m-%d')

    date_request = request.args.get('date', yesterday_date_str)
    date_param = {
        'start_date': date_request,
        'end_date': date_request
    }

    hubstaff_team_report_url = '{0}{1}'.format(
        settings.HUBSTAFF_API_BASE_ENDPOINT, hubstaff_team_report_endpoint)
    hubstaff_auth_headers = {
        'App-Token': settings.HUBSTAFF_APP_TOKEN,
        'Auth-Token': auth_token
    }

    response = requests.get(
        hubstaff_team_report_url,
        data=date_param,
        headers=hubstaff_auth_headers)
    organizations = response.json()

    results = []
    if len(organizations['organizations']) > 0:
        context = organizations['organizations'][0]
        project_users = context['dates'][0]
        hubstaff_projects = {}
        user_names = []
        for user in project_users['users']:
            user_name = user['name']
            user_names.append(user_name)
            for project in user['projects']:
                project_name = project['name']
                if project_name not in hubstaff_projects:
                    hubstaff_projects[project_name] = {}
                hubstaff_projects[project_name][user_name] =\
                    project['duration']

        results = [[''] + user_names]
        for user_name in user_names:
            for project in hubstaff_projects:
                user_times = [project] +\
                    [hubstaff_projects[project].get(user_name, '-')]
                results.append(user_times)

    with open('static/{}.csv'.format(date_request), mode='w') as csv_file:
        writer = csv.writer(
            csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        [
            writer.writerow(item)
            for item in results
        ]
    return render_template(
        'index.html', context=results, date_request=date_request)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
