
function chart(data) {
    //define levels
    var levels = data

    // precompute level depth - each node (n) in each array (forEach, l) in the specified array (forEach, levels) is assigned an int as their level value that corresponds to the array in which they're contained (n.level = i). 
    //levels, which was until now nested json arrays, now has clear stratification. Without this line, the nodes are on the same x-axis.
    levels.forEach((l, i) => l.forEach(n => n.level = i))

    // begin to define "nodes" separately from their levels (var nodes =) by regathering the json objects that had just been separated (levels.reduce).
    var nodes = levels.reduce(((a, x) => a.concat(x)), [])
    //create an object (nodes_index)
    var nodes_index = {}
    console.log("levels", levels)
    console.log("nodes_index", nodes_index)
    // that object (nodes_index) consists of nodes objects (d); each object goes through a function in which the object is named in accordance with its id value (nodes_index[d.id])
    nodes.forEach(d => nodes_index[d.id] = d)
    console.log("nodes", nodes)
    // objectification
    nodes.forEach(d => {
        // create new array (.map) inside "nodes_index", the objects of which (p) are either an empty array or the "parents" array ([] : d.parents) for each node (d), depending on whether there is a parents array (d.parents === undefined ?).
        d.parents = (d.parents === undefined ? [] : d.parents).map(p => nodes_index[p])
    })

    // precompute bundles
    levels.forEach((l, i) => {
        var index = {}
        // for each level (l) in "levels",
        l.forEach(n => {
            // "name" value is node's name
            var name = n.name
            var url = n.url
            // if there are no parents, pass.
            if (n.parents.length == 0) {
                return
            }
            // otherwise, make a var (id) that consists of all parents of a node separated by "--"
            var id = n.parents.map(d => d.id).sort().join('--')
            //if the id is already in the index...
            if (id in index) {
                // (concat ids??)
                index[id].parents = index[id].parents.concat(n.parents)
            }
            //if "id" not in "index", add it as an object named after "id" which consists of values for "id, "parents", and "level".
            else {
                //return the selected elements in an array. Parents are returned as new array objects (.slice)
                index[id] = { id: id, name: name, url: url, parents: n.parents.slice(), level: i }
            }
            n.bundle = index[id]
        })
        l.bundles = Object.keys(index).map(k => index[k])
        // Deleting THIS line disappears lines between nodes
        l.bundles.forEach((b, i) => b.i = i)
    })

    var links = []
    //for each object (n) in nodes, perform a function...
    nodes.forEach(d => {
        d.parents.forEach(p => links.push({ source: d, bundle: d.bundle, target: p }))
    })

    var bundles = levels.reduce(((a, x) => a.concat(x.bundles)), [])

    // reverse pointer from parent to bundles
    bundles.forEach(b => b.parents.forEach(p => {
        if (p.bundles_index === undefined) {
            p.bundles_index = {}
        }
        if (!(b.id in p.bundles_index)) {
            p.bundles_index[b.id] = []
        }
        p.bundles_index[b.id].push(b)
    }))

    //for each object (n) in nodes, perform a function...
    nodes.forEach(n => {
        //if the node has an accompanying bundles_index, 
        if (n.bundles_index !== undefined) {
            n.bundles = Object.keys(n.bundles_index).map(k => n.bundles_index[k])
        }
        else {
            n.bundles_index = {}
            n.bundles = []
        }
        n.bundles.forEach((b, i) => b.i = i)
    })

    links.forEach(l => {
        if (l.bundle.links === undefined) {
            l.bundle.links = []
        }
        l.bundle.links.push(l)
    })

    // layout
    const padding = 10
    const node_height = 22
    const node_width = 145
    const bundle_width = 14
    const level_y_padding = 16
    const metro_d = 4
    const c = 16
    const min_family_height = 16

    // THIS relates to size and placement of nodes

    nodes.forEach(n => n.height = (Math.max(1, n.bundles.length) - 1) * metro_d)

    var x_offset = padding
    var y_offset = padding
    levels.forEach(l => {
        x_offset += l.bundles.length * bundle_width
        y_offset += level_y_padding
        l.forEach((n, i) => {
            n.x = n.level * node_width + x_offset
            n.y = node_height + y_offset + n.height / 2
            y_offset += node_height + n.height
        })
    })

    var i = 0
    levels.forEach(l => {
        l.bundles.forEach(b => {
            b.x = b.parents[0].x + node_width + (l.bundles.length - 1 - b.i) * bundle_width
            b.y = i * node_height
        })
        i += l.length
    })

    links.forEach(l => {
        l.xt = l.target.x
        l.yt = l.target.y + l.target.bundles_index[l.bundle.id].i * metro_d - l.target.bundles.length * metro_d / 2 + metro_d / 2
        l.xb = l.bundle.x
        l.xs = l.source.x
        l.ys = l.source.y
    })

    // compress vertical space
    var y_negative_offset = 0
    levels.forEach(l => {
        y_negative_offset += -min_family_height + d3.min(l.bundles, b => d3.min(b.links, link => (link.ys - c) - (link.yt + c))) || 0
        l.forEach(n => n.y -= y_negative_offset)
    })

    // add curvature
    links.forEach(l => {
        l.yt = l.target.y + l.target.bundles_index[l.bundle.id].i * metro_d - l.target.bundles.length * metro_d / 2 + metro_d / 2
        l.ys = l.source.y
        l.c1 = l.source.level - l.target.level > 1 ? node_width + c : c
        l.c2 = c
    })

    var layout = {
        height: d3.max(nodes, n => n.y) + node_height / 2 + 2 * padding,
        node_height,
        node_width,
        bundle_width,
        level_y_padding,
        metro_d
    }

    return { levels, nodes, nodes_index, links, bundles, layout, }

}
