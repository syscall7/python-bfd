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

odaApplication.run(function (odbFile) {

    odbFile.on(ODB_EVENTS.DISPLAY_UNITS_LOADED, function (e) {

        // Create a new directed graph
        var g = new dagreD3.graphlib.Graph().setGraph({});

        var duGroups = partition(e.displayUnits, 5);

        var renderer = new Oda.Renderer(odbFile);

        var num = 0;
        duGroups.forEach(function (group) {

            var label = '<table class="graph-node">';
            var template = Handlebars.compile("<tr><td>{{section_name}}:{{hex offset}}</td><td class='insn'>{{{instStr}}}</td><td class='comment'>{{comment.comment}}</td></tr>");
            for (var i = 0; i < group.length; i++) {
                var instruction = $.extend({
                    comment: odbFile.comments[group[i].offset]
                }, group[i]);
                label += template(instruction);
            }
            label += "</table>";

            g.setNode(num, {
                label: label,
                labelType: 'html'
            });
            num += 1;
        });

        for (var i = 0; i < duGroups.length - 1; i++) {
            g.setEdge(i, i + 1, {label: i + "," + (i + 1)})
        }
        g.setEdge(0, duGroups.length-1, {label:'HERE'});

        var svg = d3.select("svg"),
            inner = svg.select("g");

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
        svg.attr('height', "800");

    });

});