# parse_logs.py
import os
import json
import csv
from glob import glob

LOGDIR = "logs"
OUTCSV = "players_extracted.csv"

def extract_candidate(data):
    # Fonction heuristique pour extraire champs communs
    out = {}
    # cherche récursivement 'id', 'playerId', 'player_id'
    def find_key(d, keys):
        if isinstance(d, dict):
            for k,v in d.items():
                if k in keys:
                    return v
                else:
                    res = find_key(v, keys)
                    if res is not None:
                        return res
        elif isinstance(d, list):
            for item in d:
                res = find_key(item, keys)
                if res is not None:
                    return res
        return None

    out['id'] = find_key(data, ['id','playerId','player_id','uid'])
    out['name'] = find_key(data, ['name','nickname','playerName'])
    out['power'] = find_key(data, ['power','battle_power','playerPower'])
    out['alliance'] = find_key(data, ['alliance','guild','allianceName','alliance_id'])
    return out

rows = []
files = glob(os.path.join(LOGDIR, "*.response.json"))
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fh:
            j = json.load(fh)
        candidate = extract_candidate(j)
        candidate['_source_file'] = f
        rows.append(candidate)
    except Exception as e:
        print("Erreur parsing", f, e)

# write CSV
if rows:
    keys = ['id','name','power','alliance','_source_file']
    with open(OUTCSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in keys})
    print("CSV écrit:", OUTCSV)
else:
    print("Aucune donnée JSON trouvée.")
