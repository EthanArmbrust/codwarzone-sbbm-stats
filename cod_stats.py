import json
import csv
import sys
import requests
import urllib.parse


def read_json(path):
    with open(path) as f:
        data = json.load(f)
    return data


def json_to_csv(data, csv_output, playerDataRows, prune=True, ignoreNonSoloMatches=True):
    with open(csv_output, 'w', newline='') as csvfile:
        codwriter = csv.writer(csvfile, delimiter = ',', quotechar ='\"', quoting=csv.QUOTE_MINIMAL)
        codwriter.writerow(['MatchID', 'placement', 'username', 'platform', *playerDataRows])
        for match in data['data']['matches']:
            matchID = match['matchID']
            if ignoreNonSoloMatches and match['mode'] == "br_25":
                pass
            else:
                for team in match['rankedTeams']:
                    placement = team['placement']
                    for player in team['players']:
                        username = player['username']
                        platform = player['platform']
                        writeList = [matchID, placement, username, platform]
                        skipLine = False
                        for param in playerDataRows:
                            try:
                                writeList.append(player['playerStats'][param])
                            except KeyError:
                                skipLine = True
                                writeList.append('-')
                        #Prune bad data
                        #Harcoding this as 16 is bad, if playerDataRows changes, please fix
                        if writeList[16] == 0: #Remove any people with distanceTraveled == 0, obivously bad data
                            skipLine = True
                        if not skipLine or not prune:
                            codwriter.writerow(writeList)
    print("Wrote to {}".format(csv_output))


def get_player_overall_stats(platform, username):
    url = "https://my.callofduty.com/api/papi-client/stats/cod/v1/title/mw/platform/{}/gamer/{}/profile/type/mp".format(platform, urllib.parse.quote(username))
    response = requests.request("GET", url, headers={}, data={})
    return response.json()


def remove_clan_tag(username):
    cursor = 0
    if username[cursor] == '[':
        while not username[cursor] == ']':
            cursor += 1
        return username[cursor+1:]
    else:
        return username


def get_players_in_match(data, match_num):
    match = data['data']['matches'][match_num]
    players = []
    for team in match['rankedTeams']:
        for player in team['players']:
            players.append({'username': player['username'], 'platform': player['platform']})
    return players
                        

def main():

    # cookie from https://github.com/Lierrmm/Node-CallOfDuty/blob/master/index.js

    cookie = "check=true; s_dfa=activision.prd; AMCVS_0FB367C2524450B90A490D4C%40AdobeOrg=1; _gcl_au=1.1.1054704054.1553245601; _fbp=fb.1.1553245601500.2028367329; AMCV_0FB367C2524450B90A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C17978%7CMCMID%7C61818798060188250940415165245687586980%7CMCAAMLH-1553850401%7C6%7CMCAAMB-1553850401%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1553252801s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0; s_ppvl=https%253A%2F%2Fwww.callofduty.com%2Fuk%2Fen%2F%2C100%2C100%2C979%2C1122%2C979%2C1920%2C1080%2C1%2CL; s_cc=true; AAMC_activisionblizzardin_0=REGION%7C6; mbox=session#a5a96a6fc4104b5d9d27124b428b9e7b#1553247575|PC#a5a96a6fc4104b5d9d27124b428b9e7b.26_10#1616490402; XSRF-TOKEN=68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041; new_SiteId=cod; comid=cod; gpv_c8=callofduty%3Ahub%3Ahome; ACT_SSO_LOCALE=en_US; s_ppv=callofduty%253Ahub%253Ahome%2C30%2C31%2C979%2C1346%2C979%2C1920%2C1080%2C1%2CL; s_nr=1553245754054-New; s_sq=activision.prd%3D%2526c.%2526a.%2526activitymap.%2526page%253Dcallofduty%25253Ahub%25253Ahome%2526link%253DMY%252520CALL%252520OF%252520DUTY%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dcallofduty%25253Ahub%25253Ahome%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fmy.callofduty.com%25252Fuk%25252Fen%2526ot%253DA; SSO_REDIRECTED_AT_LOGIN=https://my.callofduty.com/uk/en/dashboard; ACT_SSO_COOKIE=MTQ0OTE2NTk5NDg2MjE1ODcwMDI6MTU1NDQ1NTM1NjMwNjo2NmM3OTkzNTlhYTk0ODQ0OWQ2ODE3OTQ1ZjdkNWQyYw; s_ACT_SSO_COOKIE=00; atkn=eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkExMjhDQkMtSFMyNTYiLCAia2lkIjogInVub18xIn0.PqqRf9LvYpg7blrqSIhl5Ijt7lSOOaiDDjHMx1an1Q5eRjXrsn2biO3844D9WuDroVwZOLW-QgCpy91RENYrAyeTgb6igFqXXDZzdFFBAjCuNU923kwTxGS6KGh2bUHk3toYBiW8vUmGMQCv0X5d8FAMmhImOgC5IJBullAugAE.LWdQYIZGxB5FJvbut27b1w.Xk_F5I4RIgTTQxE9KR9FvnwoRALIfG_QCtqgIbEF1mPe9W6m5F_M0E7YEhB9_u0zW1biIJ1gfjOcUKkqD6YwjKnojqI3bBDBQvHl9QmWdDKi1RLcMxlaa03Umb0aFeWdKxcX3lG7Je09FaLxPpiK_Ot1En39T6RACd6GUhmAXckZILTOtUKK4pbUjI6GBy_QKD0xRNGLi3ZQPCANEOSgL2qA-LcQNP5aa3BVbphBREUdaF-ONqa3cGx9Qrj6zi1tf0X3m6bgRyzeEiJyZhSZoPopumaE0uc6bJkjK07XIrP1gPH2sqxSh6oBL2Ize6H_STfyFn3GyOtaqxbhM0t-3tRg47a1NlyBqjUGpzbj20KfvVJdO1fpd1XiDzzFqj1yeegPGv6FLgfcPoyva8vL2v40vwmjmf-EWmUSHhq8oqoICvSsRYCKgvsb-M3bdD0Et9loa112UR169lc2w9xvljbCODh780jkFw4L6sMogVvUiGJu8vj0OGMxZnwwofG4dKAXeXGinMTH5i6JF_Sl7k9KrCjG3Ij9rA3UFylZ76U.aTc-58SN1wfbXhH1vZQRzg; rtkn=eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkExMjhDQkMtSFMyNTYiLCAia2lkIjogInVub18xIn0.H_RFSOIclb7gNZ8UwQYFk3KsGB_kIjb12ernpheOIoSZlHkKjVfDdvKGWzZnQbMi5f_98fCRoQl_5GQPOKdpJdFbIrtUrESb-0udhuc0JNfApRDocb06ZOOD1EKelh1xoab6aCAG-KyY5muyL2RG3aGowENWsRsiMpaIznMchpc.a7RTG86crE72z4aXpUjLvg.3MXYDWiEsL52YeKovMvwzLftviEL2f69YRyp0z-mNWbYvWYuzJS5rSaFd1W6ZdDiqA7XgIphfR1MpiFaqfweii0-vVNpW-WtiZvD8BNQcObMpNM7DO6wjBCavra12USmEgv7jYx2FhEEz8KkmtRUgfFQA5iJCnzoUptkvPPECxJlSxf4aBUjrmeHTk662PAU82LUhWt8kUFmtDfzqnQiNlZdc5gFTJsI3mq52bke_FfxLwj3IAMyAfzh53FyeAhM5lH12EFcvBc-GiUxc3TuIbu5fTAEvsHiqwsEYcy_HoKZ-giDwN1SrKeTKX2Gb398A6b-pYUO9SO0WFulQic7F40bH_8FQdBB93iZ5aDOMLshqTAcoCZvPkUdd_xiXbpuXu4lcNCyGcQlnsjKYXsUor8uQcRffi8ARO0q9LA-iOKJ00JYkWV8SMojef5j-6Di_liOACkbOPbBw0Xx8W3ZOmGeX098aniBM54S55cDdZDveMFZcpDtuQYcAfnDglAxBxFnx62WY8vR9a-8foWVKJeVB68Xm6pCaPp6s6KHdPRLEduJq2-T_3DWoEwtSS-_hm8-5oYZTaN52rTjtw-CIA.SvXszntJbbi7ZyCTahr_8g; ACT_SSO_REMEMBER_ME=MTQ0OTE2NTk5NDg2MjE1ODcwMDI6JDJhJDEwJGxNY2kvNVFDT2JWNkVWYk55RGxIdE83WnN1TDRrYzlsdVdPc3oxRWNHRlBtMVZnLzhOcGVp; ACT_SSO_EVENT=LOGIN_SUCCESS:1553245756744; pgacct=psn; CRM_BLOB=eyJ2ZXIiOjEsInBsYXQiOnt9fQ; agegate=; country=GB; umbrellaId=14046028513701392872; facebookId=true; psnId=true; twitchId=true; twitterId=true; youTubeId=true"
    # dat = read_json('data.json')

    if len(sys.argv) == 2:
        output_file = sys.argv[1]
    else:
        output_file = "output.csv"

    print("username test:")

    print('Enter user\'s platform (battle, psn, xbl):')
    platforms = ['battle', 'psn', 'xbl']
    platform = input()
    while platform not in platforms:
        print('Invalid platform. Enter user\'s platform (battle, psn, xbl):')
        platform = input()

    print('Enter username:')
    if platform == 'battle':
        print('Add #Battle.net-Number to username. Ex. for user Interslice -> Interslice#11454')
    username = input()

    url_username = username
    if platform == 'battle':
        url_username = username.replace("#", '%23')
    start_time = 0
    end_time = 0
    url = "https://my.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/{}/gamer/{}/matches/wz/start/{:n}/end/{:n}/details".format(platform, url_username, start_time, end_time)
    payload = {}
    headers = {
        'Cookie': cookie
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.json()['status'] == "success":
        print("Found user data")
        desiredParams = ['kills', 'kdRatio', 'score', 'timePlayed', 'headshots', 'executions', 'assists',
                         'percentTimeMoving', 'rank', 'longestStreak', 'scorePerMinute', 'damageDone',
                         'distanceTraveled', 'deaths', 'damageTaken']
        json_to_csv(response.json(), output_file, desiredParams)
        players = get_players_in_match(response.json(), 2)
        battlenet = 0
        xb3 = 0
        ps4 = 0
        for p in players:
            if p["platform"] == "battlenet":
                battlenet += 1
            elif p["platform"] == "xb3":
                xb3 += 1
                player_info = get_player_overall_stats('xbl', remove_clan_tag(p['username']))
                if player_info['status'] == 'success':
                    print("got data for {} on xbox".format(p['username']))
                    print("skipping data for {} on pc".format(p['username']))
                else:
                    print("could not get data for {} on xbox".format(p['username']))
            elif p["platform"] == "ps4":
                player_info = get_player_overall_stats('psn', remove_clan_tag(p['username']))
                if player_info['status'] == 'success':
                    print("got data for {} on ps4".format(p['username']))
                else:
                    print("could not get data for {} on ps4".format(p['username']))
                ps4 += 1


        print("PC players: {}".format(battlenet))
        print("PS4 players: {}".format(ps4))
        print("Xbox players: {}".format(xb3))
    else:
        print("Data not found")


if __name__ == "__main__":
    main()
