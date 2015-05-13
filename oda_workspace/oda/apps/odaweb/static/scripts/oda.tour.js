odaApplication.run(function (odbFile) {

    var master = odbFile.oda_master;
    if (master.binary.liveMode) {
        // Instance the tour
        var tour = new Tour({
            name: 'live-mode-tour',
            steps: [{
                element: "#oda-tabs li:first",
                title: "Title of my step",
                content: "Content of my step"
            },
                {
                    element: "#hex-sidebar-scroll",
                    title: "Title of my step",
                    content: "Content of my step"
                }],
            storage: false
        });

        // Initialize the tour
        tour.init();

        // Start the tour
        tour.start();
    } else {
        // Instance the tour
        var tour = new Tour({
            name: 'file-mode-tour',
            steps: [{
                element: "#oda-tabs li:first",
                title: "Title of my FILE step2",
                content: "Content of my step2"
            },
                {
                    element: "#hex-sidebar-scroll",
                    title: "Title of my FILE step2",
                    content: "Content of my step2"
                }],
            storage: false
        });

        // Initialize the tour
        tour.init();

        // Start the tour
        tour.start();
    }

});