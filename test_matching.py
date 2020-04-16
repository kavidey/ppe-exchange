from app.matching_algorithm.ford_fulkerson import FlowNetwork

participants = {
    "1": "Jim",
    "2": "Mike",
    "3": "Kathy"
}

sku = {
    "a": "type a",
    "b": "type b",
    "c": "type c"
}

want = {
    "1": [
            {
                "sku": "b",
                "count": 125
            },
            {
                "sku": "c",
                "count": 125
            }
    ],
    "2": [
            {
                "sku": "a",
                "count": 125
            },
            {
                "sku": "c",
                "count": 125
            }
    ],
    "3": [
            {
                "sku": "a",
                "count": 125
            },
            {
                "sku": "b",
                "count": 125
            }
    ]
}

has = {
    "1": [
            {
                "sku": "a",
                "count": 250
            }
    ],
    "2": [
            {
                "sku": "b",
                "count": 250
            }
    ],
    "3": [
            {
                "sku": "c",
                "count": 250
            }
    ]
}


fn = FlowNetwork()
fn.addVertex('s', True, False)
fn.addVertex('t', False, True)

new_vertices = []
for p in participants:
    for s in sku:
        for w in want[p]:
            if w["sku"] == s:
                #print(participants[p], "wants", sku[s])
                v_name = p+"-"+s+"-w"
                new_vertices.append([v_name, w["count"]])
                fn.addVertex(v_name)
                fn.addEdge('s', v_name, w["count"])
for p in participants:
    for s in sku:
        for h in has[p]:
            if h["sku"] == s:
                #print(participants[p], "has", sku[s])
                v_name = p+"-"+s+"-h"
                fn.addVertex(v_name)
                fn.addEdge(v_name, 't', h["count"])
                for nv in new_vertices:
                    nv_sku = nv[0].split("-")[1]
                    if nv_sku == s:
                        fn.addEdge(nv[0], v_name, h["count"])

print(fn.calculateMaxFlow())

# Display all connections
for e in fn.getEdges():
    if e.capacity > 0:
        print('{} -> {} {}/{}'.format(e.start, e.end, e.flow, e.capacity))


# Display transactions
for e in fn.getEdges():
    if e.capacity > 0:
        if e.start != "s" and e.end != "t":
            start = e.start.split("-")
            end = e.end.split("-")
            print(participants[end[0]], "gives", e.flow, start[1], "to", participants[start[0]])

'''
fn = FlowNetwork()
fn.addVertex('s', True, False)
fn.addVertex('t', False, True)
for v in ['a', 'b','c','d']:
    fn.addVertex(v)
fn.addEdge('s', 'a', 4)
fn.addEdge('a', 'b', 4)
fn.addEdge('b', 't', 2)
fn.addEdge('s', 'c', 3)
fn.addEdge('c', 'd', 6)
fn.addEdge('d', 't', 6)

print(fn.calculateMaxFlow())

for e in fn.getEdges():
    if e.flow > 0:
        print('{} -> {} {}/{}'.format(e.start, e.end, e.flow, e.capacity))
'''