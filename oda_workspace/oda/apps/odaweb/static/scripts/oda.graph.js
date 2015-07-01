"use strict";

function DrawGraph(odbFile, graph) {
    var template = Handlebars.compile("<tr data-addr='{{offset}}'><td>{{section_name}}:{{hex offset}}</td><td class='insn'>{{{instStr}}}</td><td class='comment'>{{comment.comment}}</td></tr>");

    $('.ui-layout-east svg').remove();
    $('.ui-layout-east div').remove();
    $('.ui-layout-east').append('<svg><g/></svg>');

    // Create a new directed graph
    var g = new dagreD3.graphlib.Graph().setGraph({});

    var offsets = [];

    graph.nodes.forEach(function(node){
        var label = '<table class="graph-node">';
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

    editor.activeAddressChanged.subscribe(_.debounce(function(e, args) {
        $('.graph-active').removeClass('graph-active');
        $("tr[data-addr='" + args.offset + "']").addClass('graph-active');

        for (var i=0; i<loadedOffsets.length; i++) {
            if (loadedOffsets[i] == args.offset) {
                return;
            }
        }

        loadedOffsets = [];
        $('.ui-layout-east svg').remove();
        $('.ui-layout-east div').remove();

        odbFile.graph(args.offset).success(function(graph){
            loadedOffsets = DrawGraph(odbFile, graph);
        }).error(function(data){
            $('.ui-layout-east').append('<div class="alert alert-warning">Instruction graph not available for address 0x' + args.offset.toString(16) + '</div>');
        });
    }));

});