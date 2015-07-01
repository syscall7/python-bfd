"use strict";

function partition(items, size) {
    var result = _.groupBy(items, function (item, i) {
        return Math.floor(i / size);
    });
    return _.values(result);
}

function createData(duList) {
    var duGroups = partition(duList, 5);

    var nodes = $.map(duGroups, function(group, key) {
        return {
            id: key,
            instructions: group
        };
    });

    var links = [];
    for (var i = 0; i < duGroups.length - 1; i++) {
        links.push({
            from: i,
            to: i+1,
            type: (i%2==0) ? 'unconditional' : 'notTaken'
        });
    }
    links.push({
        from: 0,
        to: duGroups.length - 1,
        type: 'taken'
    });

    return {
        nodes: nodes,
        links: links
    }
}

function DrawGraph(odbFile, graph) {

    $('.ui-layout-east svg').remove();
    $('.ui-layout-east').append('<svg><g/></svg>');

    // Create a new directed graph
    var g = new dagreD3.graphlib.Graph().setGraph({});

    var offsets = [];

    graph.nodes.forEach(function(node){
        var label = '<table class="graph-node">';
        var template = Handlebars.compile("<tr data-addr='{{offset}}'><td>{{section_name}}:{{hex offset}}</td><td class='insn'>{{{instStr}}}</td><td class='comment'>{{comment.comment}}</td></tr>");
        for (var i = 0; i < node.instructions.length; i++) {
            var instruction = $.extend({
                comment: odbFile.comments[node.instructions[i].offset]
            }, node.instructions[i]);
            label += template(instruction);

            offsets.push(instruction.offset);
        }
        label += "</table>";

        g.setNode(node.id, {
            label: label,
            labelType: 'html'
        });
    });

    graph.links.forEach(function(link){
        g.setEdge(link.from, link.to, {
            //label: link.from + ' ' + link.to,
            style: LINK_STYLE[link.type],
        });
    });

    var svg = d3.select("svg");

    var inner = svg.select("g");

    // Set up zoom support
    var zoom = d3.behavior.zoom().on("zoom", function () {
        inner.attr("transform", "translate(" + d3.event.translate + ")" +
            "scale(" + d3.event.scale + ")");
    });
    svg.call(zoom);

    // Create the renderer
    var render = new dagreD3.render();

    // Run the renderer. This is what draws the final graph.
    render(inner, g);

    // Center the graph
    var initialScale = 1.0;
    zoom
        .translate([(svg.attr("width") + 0) / 2, 20])
        .scale(initialScale)
        .event(svg);

    svg.attr('width', '100%');
    svg.attr('height', $(window).height()-150);


    return offsets;

}

var LINK_STYLE = {
    notTaken: "stroke: #f00; stroke-width: 2px; fill: none;",
    taken: "stroke: #0f0; stroke-width: 2px; fill: none;",
    unconditional: "stroke: #00f; stroke-width: 2px; fill: none;"
};

odaApplication.run(function (odbFile, editor) {

    /* List of loaded offsets, check this list to see if we need to reload */
    var loadedOffsets = [];

    editor.activeAddressChanged.subscribe(function(e, args) {
        $('.graph-active').removeClass('graph-active');
        $("tr[data-addr='" + args.offset + "']").addClass('graph-active');

        for (var i=0; i<loadedOffsets.length; i++) {
            if (loadedOffsets[i] == args.offset) {
                return;
            }
        }
        odbFile.graph(args.offset).success(function(graph){
            loadedOffsets = DrawGraph(odbFile, graph);
        });
    });

   /* odbFile.on(ODB_EVENTS.DISPLAY_UNITS_LOADED, function (e) {

        odbFile.graph(0).success(function(graph){
            DrawGraph(odbFile, graph);
        });

    });*/

});