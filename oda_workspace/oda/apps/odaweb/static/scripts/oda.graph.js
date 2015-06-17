"use strict";

function partition(items, size) {
    var result = _.groupBy(items, function (item, i) {
        return Math.floor(i / size);
    });
    return _.values(result);
}


/* Green Red Blue */
// Blue Unconditional Branch
// Green Taken
// Red Not Taken

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
            type: 'notTaken'
        });
    }
    links.push({
        from: 0,
        to: duGroups.length - 1,
        type: 'notTaken'
    });

    return {
        nodes: nodes,
        links: links
    }
}

odaApplication.run(function (odbFile, editor) {

    odbFile.on(ODB_EVENTS.DISPLAY_UNITS_LOADED, function (e) {
        $('.ui-layout-east svg').remove();
        $('.ui-layout-east').append('<svg><g/></svg>');

        // Create a new directed graph
        var g = new dagreD3.graphlib.Graph().setGraph({});

        var renderer = new Oda.Renderer(odbFile);

        var graph = createData(e.displayUnits);

        graph.nodes.forEach(function(node){
            var label = '<table class="graph-node">';
            var template = Handlebars.compile("<tr data-addr='{{offset}}'><td>{{section_name}}:{{hex offset}}</td><td class='insn'>{{{instStr}}}</td><td class='comment'>{{comment.comment}}</td></tr>");
            for (var i = 0; i < node.instructions.length; i++) {
                var instruction = $.extend({
                    comment: odbFile.comments[node.instructions[i].offset]
                }, node.instructions[i]);
                label += template(instruction);
            }
            label += "</table>";

            g.setNode(node.id, {
                label: label,
                labelType: 'html'
            });
        });

        graph.links.forEach(function(link){
            g.setEdge(link.from, link.to, {label: link.from + ' ' + link.to});
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
        var initialScale = 0.75;
        zoom
            .translate([(svg.attr("width") - g.graph().width * initialScale) / 2, 20])
            .scale(initialScale)
            .event(svg);

        svg.attr('width', '100%');
        svg.attr('height', $(window).height()-150);



        editor.activeAddressChanged.subscribe(function(e, args) {
            $('.graph-active').removeClass('graph-active');
            $("tr[data-addr='" + args.offset + "']").addClass('graph-active');
        });

    });

});