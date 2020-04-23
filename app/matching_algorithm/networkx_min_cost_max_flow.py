import networkx as nx
import matplotlib.pyplot as plt

kCredits = 1
kNormalizationFactor = 1
participants = {
    "1": {
        "name": "Jim",
        "credits": 0,
        "normalization_factor": 1
    },
    "2": {
        "name": "Mike",
        "credits": 0,
        "normalization_factor": 1
    },
    "3": {
        "name": "Cathy",
        "credits": 0,
        "normalization_factor": 1
    }
}

# Test1
want = [
    {
        "hospital": "2",
        "sku": "b",
        "count": 125
    },
    {
        "hospital": "3",
        "sku": "b",
        "count": 125
    }
]

has = [
    {
        "hospital": "1",
        "sku": "b",
        "count": 200
    }
]

# Test2

want = [
    {
        "hospital": "1",
        "sku": "b",
        "count": 125
    },
    {
        "hospital": "1",
        "sku": "c",
        "count": 125
    },
    {
        "hospital": "2",
        "sku": "a",
        "count": 125
    },
    {
        "hospital": "2",
        "sku": "c",
        "count": 125
    },
    {
        "hospital": "3",
        "sku": "a",
        "count": 125
    },
    {
        "hospital": "3",
        "sku": "b",
        "count": 125
    }
]

has = [
    {
        "hospital": "1",
        "sku": "a",
        "count": 250
    },
    {
        "hospital": "2",
        "sku": "b",
        "count": 250
    },
    {
        "hospital": "3",
        "sku": "c",
        "count": 250
    }
]


sku_supply_demand = {}
node_id = 2
for w in want:
    if w["sku"] not in sku_supply_demand:
        sku_supply_demand[w["sku"]] = {}
    if "want" not in sku_supply_demand[w["sku"]]:
        sku_supply_demand[w["sku"]]["want"] = []
    w["node_id"] = node_id
    sku_supply_demand[w["sku"]]["want"].append(w)
    node_id += 1
for h in has:
    if h["sku"] not in sku_supply_demand:
        sku_supply_demand[h["sku"]] = {}
    if "has" not in sku_supply_demand[h["sku"]]:
        sku_supply_demand[h["sku"]]["has"] = []
    h["node_id"] = node_id
    sku_supply_demand[h["sku"]]["has"].append(h)
    node_id += 1

# hospital1_id (giving), hospital2_id (recieveing), count, ppe_id
exchanges = []

for sku in sku_supply_demand:
    edges = []
    for h in sku_supply_demand[sku]["has"]:
        edges.append(
            ("0", str(h["node_id"]), {'capacity': h["count"], 'weight': 0})
        )
        for w in sku_supply_demand[sku]["want"]:
            hospital = participants[w["hospital"]]
            weight = int(-hospital["credits"]*kCredits / hospital["normalization_factor"]*kNormalizationFactor)
            edges.append(
                (str(h["node_id"]), str(w["node_id"]), {'capacity': h["count"], 'weight': weight})
            )
    for w in sku_supply_demand[sku]["want"]:
        edges.append(
            (str(w["node_id"]), "1", {'capacity': w["count"], 'weight': 0})
        )
    
    print()
    print("---------------- "+sku+" ----------------")
    print(edges)
    
    G = nx.DiGraph()

    G.add_edges_from(edges)

    nx.draw(G,with_labels=True)
    plt.savefig(sku+".png")

    print(nx.max_flow_min_cost(G, '0', '1'))

    '''
    if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
        print('Minimum cost:', min_cost_flow.OptimalCost())
        print('')
        print('  Arc    Flow / Capacity  Cost')
        for i in range(min_cost_flow.NumArcs()):
            cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
            print('%1s -> %1s   %3s  / %3s       %3s' % (
                min_cost_flow.Tail(i),
                min_cost_flow.Head(i),
                min_cost_flow.Flow(i),
                min_cost_flow.Capacity(i),
                cost))
            
            # Format exchanges for database
            have_id = ''
            for h in sku_supply_demand[sku]["has"]:
                if h["node_id"] == min_cost_flow.Tail(i):
                    have_id = h["hospital"]
            
            want_id = ''
            for w in sku_supply_demand[sku]["want"]:
                if w["node_id"] == min_cost_flow.Head(i):
                    want_id = w["hospital"]
            
            exchanges.append([{
                "hospital1": have_id,
                "hospital2": want_id,
                "count": min_cost_flow.Flow(i),
                "ppe": sku
            }])
    else:
        print('There was an issue with the min cost flow input.')
    

print("\n\nResult:")
print(exchanges)
'''