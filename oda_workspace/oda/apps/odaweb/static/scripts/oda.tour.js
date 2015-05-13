odaApplication.run(function (odbFile) {

    var master = odbFile.oda_master;
    if (master.binary.liveMode) {
        // Instance the tour
        debugger;
        var tour = new Tour({
            name: 'live-mode-tour-v1',
            steps: [
                {
                    element: "#platform-btn",
                    title: "Step 1: Select the Platform",
                    content: "Select the machine architecture to target and relevant machine options."
                },
                {
                    element: "#hex",
                    title: "Step 2: Enter Bytes",
                    content: "Enter some bytes to disassemble in Live View."
                },
                {
                    element: "#oda-tabs li:first",
                    title: "Step 3: View Disassembly Listing",
                    content: "The bytes will be disassembled into readable instructions for the target architecture."
                },
                {
                    element: "#open-btn",
                    title: "Step 4: Upload a File",
                    content: "You can also upload a file to disassemble, including raw binaries and many common object formats (ELF, PE, COFF, Mach-O, etc.)."
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
            name: 'file-mode-tour-v1',
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