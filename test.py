import requests

headers = {'Authorization': "Basic NTg1YjNjNTc4OTM1NDcxMzhkMDA4YmU2YjYzMjFiZTk6"}
resp = requests.post('https://bhttq3cj-splash.scrapinghub.com/render.html', headers=headers, json={
    'url': 'https://www.trulia.com/p/tx/arlington/2420-sutton-dr-arlington-tx-76018--2067248102',
    'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0', }
})
print(resp.text)
