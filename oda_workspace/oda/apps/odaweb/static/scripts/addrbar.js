/*
<html>
  <head>
    <title>Address Bar</title>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.6.0/underscore-min.js"></script>
    <script type="text/javascript">

        $(document).ready(function(){
/*

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
function ArrowStyle(r, g, b, a) {

    this.r = r;
    this.g = g;
    this.b = b;
    this.a = a;
}

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
function Location(posX, vma, style) {

    /* The X pixel offset on the navigation bar */
    this.posX = posX;

    /* The virtual memory address */
    this.vma = vma;

    /* The arrow styling */
    this.style = style;
}

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
function AddressNavBar(canvasId, sections) {

    /* -------------------------------------------------------------- *
     *              P R I V A T E   P R O P E R T I E S
     * -------------------------------------------------------------- */
    var ARROW_YOFFSET;
    var ARROW_HEIGHT;
    var ARROW_WIDTH;

    var BAR_WIDTH;
    var BAR_YOFFSET;
    var BAR_HEIGHT;

    var TEXT_YOFFSET;
    var TEXT_WIDTH;
    var TEXT_HEIGHT;

    var CANVAS_WIDTH;
    var CANVAS_HEIGHT;
    var INTER_SECTION_GAP = 2;

    var EFFECTIVE_BAR_WIDTH;
    var RUNT_PIXEL_THRESHOLD = 3;
    var RUNT_MIN_WIDTH = 3;

    /* our current position */
    var curArrow = new Location(0, undefined, new ArrowStyle(0, 0, 0, 1.0));

    /* our roaming position */
    var roamArrow = new Location(-1, 0, new ArrowStyle(0, 0, 0, 0.40));

    /* the current position of our collaborating users */
    var userArrows = {};

    // get the canvas and context
    var c = $('#addr-bar-canvas');
    var canvas = c.get(0);
    var ctx = canvas.getContext('2d');

    var sections;
    var sumAddrRanges;

    var dragging = false;

    var onChangeHandlers = [];
    var onDragHandlers = [];
    var onRoamHandlers = [];

    setSections(sections);

    // force an initial drawing
    resize();

    // register to re-draw ourselves when browser resizes
    $(window).resize(resize);

    /* -------------------------------------------------------------- *
     *              P R I V A T E   M E T H O D S
     * -------------------------------------------------------------- */

    /* Get the canvas X,Y position */
    function getMousePosition(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        var coords = {
          x: evt.clientX - rect.left,
          y: evt.clientY - rect.top
        };

        // snap to the nearest section boundary if in between sections
        var posX = Math.floor(coords.x);
        if (!sections) { return null;}

        for (var i = 0; i < sections.length; i++)
        {
            var secWidth = sections[i].width;
            var secPosX = sections[i].posX;

            // if we're clearly in a section
            if (posX < (secPosX + secWidth)) {
                break;
            // else, if we're in the dead space between sections
            } else if (posX < (secPosX + secWidth + INTER_SECTION_GAP)) {
                var leaning = posX - (secPosX + secWidth);

                // snap to whichever side we're closest to
                if (leaning < INTER_SECTION_GAP/2) {
                    coords.x = secPosX + secWidth - 1;
                } else if (i < (sections.length - 1)){
                    coords.x = secPosX + secWidth + INTER_SECTION_GAP;
                } else {
                    // extending beyond last section?
                }
                break;
            }
        }

        return coords;
    }

    /* Convert an X pixel location to an address */
    function pixelToAddr(posX) {

        posX = Math.floor(posX);
        for (var i = 0; i < sections.length; i++)
        {
            var secWidth = sections[i].width;
            var secPosX = sections[i].posX;

            // if we're clearly in a section
            if (posX < (secPosX + secWidth)) {
                var addr = Math.floor(sections[i].vma + ((posX - secPosX) / secWidth)*sections[i].size);
                return addr;
            // else, if we're in the dead space between sections
            } else if (posX < (secPosX + secWidth + INTER_SECTION_GAP)) {
                var leaning = posX - (secPosX + secWidth);

                // snap to whichever side we're closest to
                if (leaning < INTER_SECTION_GAP/2) {
                    return sections[i].vma + sections[i].size - 1;
                } else if (i < (sections.length - 1)){
                    return sections[i+1].vma;
                } else {
                    return -1;
                }
            }
        }
        return -1;
    }

    /* Convert an address to the X pixel location */
    function addrToPixel(addr) {

        var posX = -1;

        for (var i = 0; i < sections.length; i++)
        {
            if ((addr >= sections[i].vma) &&
                (addr < (sections[i].vma + sections[i].size)))
            {
                posX = (addr - sections[i].vma) /
                       sections[i].size *
                       sections[i].width +
                       sections[i].posX;
                break;
            }
        }

        return posX;
    }

    /* Internal function called when current position changes */
    function doCurArrowCallbacks() {

        if (dragging) {
            for (var i = 0; i < onDragHandlers.length; i++) {
                onDragHandlers[i](curArrow.vma);
            }

        } else {
            for (var i = 0; i < onChangeHandlers.length; i++) {
                onChangeHandlers[i](curArrow.vma);
            }
        }
    }

    /* Internal function called when current position changes via setting the address */
    function curArrowVmaChanged(newAddr) {

        var xpos = addrToPixel(newAddr);

        if ((0 > xpos) || (newAddr == curArrow.vma)) {
            return;
        }

        curArrow.posX = xpos;
        curArrow.vma = newAddr;

        /* Don't do callbacks when position changes by address, because it means we are being notified via the
           odaapi position broadcast.  Anybody else who cares about our current position will get that broadcast too,
           so we don't have to bother calling them back.

           doCurArrowCallbacks();
         */
    }

    /* Internal function called when current position changes via setting the slider position */
    function curArrowXChanged(newPosX) {

        var addr = pixelToAddr(newPosX);

        if ((0 > addr) || (addr == curArrow.vma)) {
            return;
        }

        curArrow.posX = newPosX;
        curArrow.vma = addr;
        doCurArrowCallbacks();
    }

    canvas.addEventListener('mousedown', function(evt) {
        var pos = getMousePosition(canvas, evt);
        var addr = pixelToAddr(pos.x);

        // we only start a drag if we click on the existing arrow location
        if (addr == curArrow.vma) {
            dragging = true;
        }
        curArrowXChanged(pos.x);
        draw();
    });

    canvas.addEventListener('mouseup', function(evt) {
        var pos = getMousePosition(canvas, evt);
        dragging = false;
        curArrowXChanged(pos.x);
        draw();
    });

    canvas.addEventListener('mouseout', function(evt) {
        var pos = getMousePosition(canvas, evt);
        roamArrow.posX = -1;
        draw();
    });

    canvas.addEventListener('mousemove', function(evt) {
        var pos = getMousePosition(canvas, evt);
        if (!pos) { return; }
        var addr = pixelToAddr(pos.x);

        if ((addr >= 0) && (roamArrow.vma != addr)) {

            for (var i = 0; i < onRoamHandlers.length; i++) {
                onRoamHandlers[i](addr);
            }

            roamArrow.posX = pos.x;
            roamArrow.vma = addr;
            draw();

            if (dragging) {
                curArrowXChanged(pos.x);
                draw();
            }
        }
    });

    /* Runt section calculations - needs to be done on resize or adding sections */
    function calcRuntSectionSizes() {
        var runtPadding = 0;

        if (undefined != sections) {
            // calculate how much space we need for runt padding
            for (var i = 0; i < sections.length; i++) {
                var width = Math.floor(sections[i].size / sumAddrRanges * BAR_WIDTH);
                if (width < RUNT_PIXEL_THRESHOLD) {
                    runtPadding += RUNT_MIN_WIDTH - width;
                }
            }

            // calculate how much BAR_WIDTH we really have to work with for scaling purposes
            EFFECTIVE_BAR_WIDTH = BAR_WIDTH - runtPadding - (sections.length-1)*INTER_SECTION_GAP;
        } else {
            EFFECTIVE_BAR_WIDTH = BAR_WIDTH;
        }
    }

    function resize() {

        // get the parent container
        var container = $(c).parent();

        // calculate canvas and object dimensions (for when window is resized)
        CANVAS_WIDTH = $(container).width() // use width of parent
        ARROW_WIDTH = 10;
        BAR_WIDTH = CANVAS_WIDTH;
        TEXT_WIDTH = BAR_WIDTH;

        ARROW_YOFFSET = 0;
        ARROW_HEIGHT = 6;

        BAR_YOFFSET = ARROW_YOFFSET + ARROW_HEIGHT;
        BAR_HEIGHT = 17;

        TEXT_YOFFSET = BAR_YOFFSET + BAR_HEIGHT;
        TEXT_HEIGHT = 15;

        CANVAS_HEIGHT = TEXT_YOFFSET + TEXT_HEIGHT;

        // set canvas height and width
        c.attr('width', CANVAS_WIDTH);
        c.attr('height', CANVAS_HEIGHT);

        calcRuntSectionSizes();

        // redraw now that size has changed
        draw();
    }

    function draw() {
        var x = 0;

        // tabula rasa
        ctx.clearRect (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        /*
         * draw the sections
         */
        if (undefined == sections) {
            return;
        }

        // make a second pass to assign widths to each section
        for (var i = 0; i < sections.length; i++) {
            var width = Math.floor(sections[i].size / sumAddrRanges * (EFFECTIVE_BAR_WIDTH));

            if (width < RUNT_PIXEL_THRESHOLD) {
                width = RUNT_MIN_WIDTH;
            }

            // draw section
            ctx.fillStyle = "rgb(0,110,255)";
            ctx.fillRect (x, BAR_YOFFSET, width, BAR_HEIGHT);

            // store some info with each section
            sections[i].width = width;
            sections[i].posX = x;

            x += width + INTER_SECTION_GAP;
        }

        // draw the arrows
        function drawArrow(arrow) {
            var ARROW_BOX_WIDTH = 20;

            var x = arrow.posX;
            var opacityFactor = arrow.style.a;

            // draw the yellow box below the arrow
            ctx.beginPath();
            ctx.rect(x - ARROW_BOX_WIDTH/2, BAR_YOFFSET-1, ARROW_BOX_WIDTH, BAR_HEIGHT+2);
            ctx.fillStyle = "rgba(255,255,0, " + 0.40*opacityFactor + ")";
            ctx.fill();
            ctx.strokeStyle = "rgba(255,255,0, " + 1.0*opacityFactor + ")";
            ctx.stroke();

            // draw the yellow line centered in the box
            ctx.moveTo(x, BAR_YOFFSET);
            ctx.lineTo(x, BAR_YOFFSET+BAR_HEIGHT);
            ctx.strokeStyle = "rgba(255,255,0, " + 1.0*opacityFactor + ")";
            ctx.stroke();

            // draw the arrow itself
            var rgba = "" + arrow.style.r + "," + arrow.style.g + "," + arrow.style.b + "," + arrow.style.a;
            ctx.fillStyle = "rgba(" + rgba + ")";
            ctx.beginPath();
            ctx.moveTo(x, BAR_YOFFSET);
            ctx.lineTo(x+ARROW_WIDTH/2, BAR_YOFFSET-ARROW_HEIGHT);
            ctx.lineTo(x-ARROW_WIDTH/2, BAR_YOFFSET-ARROW_HEIGHT);
            ctx.lineTo(x, BAR_YOFFSET);
            ctx.fill();
            ctx.closePath();

        };

        // first draw the user arrows
        $.each(userArrows, function(uid, arrow) {
            drawArrow(arrow);
        });

        // draw the roaming arrow and roaming text
        if (roamArrow.posX >= 0) {

            // draw roaming arrow that is slightly transparent
            drawArrow(roamArrow);

            // draw address text
            ctx.fillStyle = "rgb(0,0,0)";
            ctx.font = TEXT_HEIGHT.toString() + "px Monospace";
            ctx.fillText('0x' + roamArrow.vma.toString(16), roamArrow.posX, TEXT_YOFFSET + TEXT_HEIGHT);
        }

        // draw the current position indicator
        drawArrow(curArrow);
    }

    /* -------------------------------------------------------------- *
     *                  P U B L I C   M E T H O D S
     * -------------------------------------------------------------- */

    /* Update the sections represented in this navigation bar */
    function setSections(s) {
        sections = s;
        sumAddrRanges = _.reduce(sections, function(memo, section) {return memo+section.size}, 0);

        if ((sections != undefined) && (curArrow.vma == undefined)) {
            curArrow.vma = _.min(sections, function(section){ return section.vma; }).vma;
            roamArrow.vma = curArrow.vma;
        }

        calcRuntSectionSizes();
        draw();
    }
    this.setSections = setSections;

    /* Set the current address */
    function setAddress(a) {

        if (a != curArrow.vma) {
            var posX = addrToPixel(a);

            if (posX < 0) {
                return false;
            }

            curArrowVmaChanged(a);
            draw();
        }

        return true;
    }
    this.setAddress = setAddress;

    /* Allow event handler registration for onChange of address */
    function onChange(handler) {
        onChangeHandlers.push(handler);
    }
    this.onChange = onChange;

    /* Allow event handler registration for onRoam of address */
    function onRoam(handler) {
        onRoamHandlers.push(handler);
    }
    this.onDrag = onDrag;

    /* Allow event handler registration for onDrag of address */
    function onDrag(handler) {
        onDragHandlers.push(handler);
    }
    this.onRoam = onRoam;

    /* Add a new user whose position we wish to track */
    function addUser(uid) {
        if (userArrows[uid] == undefined) {
            var userCount = 0;
            getNewArrowStyle = function () {
                // TODO: Make a pretty color pallette here */
                return new ArrowStyle(200, 100, 50, 0.40);
            };

            userArrows[uid] = new Location(0,0, getNewArrowStyle());
        }
    }
    this.addUser = addUser;

    /* Remove a user whose position we no longer wish to track */
    function removeUser(uid) {
        delete userArrows[uid]
    }
    this.removeUser = removeUser;

    /* Update a user's current position by virtual memory address */
    function updateUser(uid, vma) {

        /* if nothing changed */
        if (vma == curArrow.vma) {
            return;
        }

        /* convert to pixel offset */
        var x = addrToPixel(vma);

        /* if this is an invalid vma, ignore it */
        if (0 > x) {
            return;
        }

        userArrows[uid].vma = vma;
        userArrows[uid].posX = x;

        draw();
    }
    this.updateUser = updateUser;
}

/* ------------------------------------------------------------------ *
 *                           E X A M P L E
 * ------------------------------------------------------------------ */

/*
// define some sections
var sections = [
    {
        'name' : '.small0',
        'vma' : 0x300000,
        'size' : 0x5,
    },
    {
        'name' : '.small1',
        'vma' : 0x300100,
        'size' : 0x5,
    },
    {
        'name' : '.plt',
        'vma' : 0x400000,
        'size' : 0x500,
    },
    {
        'name' : '.text',
        'vma' : 0x500000,
        'size' : 0x40000,
    },
    {
        'name' : '.text_small',
        'vma' : 0x540000,
        'size' : 0x00050,
    },
    {
        'name' : '.data',
        'vma' : 0x550000,
        'size' : 0x80000,
    },
    {
        'name' : '.small2',
        'vma' : 0x600000,
        'size' : 0x5,
    },
    {
        'name' : '.small3',
        'vma' : 0x800100,
        'size' : 0x5,
    }
];

// instantiate the address nav bar
addrBar = new AddressNavBar('#addr-bar-canvas', sections);
addrBar.onChange(function(a) {
    console.log('My change handler: ' + a.toString(16));
});
addrBar.onDrag(function(a) {
    console.log('My drag handler: ' + a.toString(16));
});
addrBar.setAddress(0x520000);

addrBar.addUser('anthony');
addrBar.updateUser('anthony', 0x560000);

    });
    </script>
    <style type="text/css">canvas { border: 0px solid black; }</style>
  </head>
  <body>
    <div>
        <canvas id="addr-bar-canvas">You need to upgrade your browser to see this!</canvas>
    <div>
  </body>
</html>
*/
