import json

def analyze(data: dict):
    maxx = 0
    ans = {}
    maxes = []
    for key, metrics in data.items():
        try:
            profit = metrics['Long']['abs_profit'] + metrics['Short']['abs_profit']
            if profit > maxx:
                ans['profit'] = profit
                ans['data'] = metrics
                ans['settings'] = key 
                maxx = profit
                maxes.append([profit, ans])
        except TypeError:
            print(metrics)
    print(ans)
    return maxes

with open('delta_deals_hilbert.json') as f:
    data = dict(json.load(f))
    maxes = analyze(data=data)
    total = sorted(maxes, key=lambda x: x[0])
    print(total[0], total[1], total[2], total[3], sep='\n')