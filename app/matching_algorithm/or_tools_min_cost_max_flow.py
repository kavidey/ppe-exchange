from ortools.graph import pywrapgraph

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
        "count": 250
    }
]

sku_supply_demand = {}
node_id = 0
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
    start_nodes = []
    end_nodes   = []
    capacities  = []
    unit_costs  = []
    supplies = [0]*(node_id+1)

    for h in sku_supply_demand[sku]["has"]:
        supplies[h["node_id"]] = h["count"]
        for w in sku_supply_demand[sku]["want"]:
            supplies[w["node_id"]] = -w["count"]
            start_nodes.append(h["node_id"])
            end_nodes.append(w["node_id"])
            capacities.append(h["count"])
            hospital = participants[w["hospital"]]
            weight = -hospital["credits"]*kCredits / hospital["normalization_factor"]*kNormalizationFactor
            unit_costs.append(int(weight))
    
    print()
    print("---------------- "+sku+" ----------------")
    print(start_nodes)
    print(end_nodes)
    print(capacities)
    print(unit_costs)
    print(supplies)
    
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    for i in range(0, len(start_nodes)):
        min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i],
                                                capacities[i], unit_costs[i])

    for i in range(0, len(supplies)):
        min_cost_flow.SetNodeSupply(i, supplies[i])

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