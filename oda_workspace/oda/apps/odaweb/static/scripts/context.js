odaApplication.run(function($rootScope, editor, odbFile){
    //http://lab.jakiestfu.com/contextjs/
    context.init({preventDoubleContext: false});

    context.show.add(function(menu){
        console.log(menu)

        var shortcuts = menu.find('.shortcut-text');
        shortcuts.removeClass('shortcut-text-disabled')

        /*
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);

        var section = odbFile.getSection(line.data.section_name);
        */

        /*if (section.isData()) {
            shortcuts.addClass('shortcut-text-disabled');
        }*/
    });

    var createAction = function(f) {

        return function(e) {
            if ($(e.target).hasClass('shortcut-text-disabled')) {
                //diasbled?
                return;
            }

            var activeRowData = editor.getActiveRowData();

            /*var session = editor.getSession();

            var cursor = session.getSelection().getCursor();
            var line = session.getDocument().getLineData(cursor.row);*/

            f(activeRowData);
        };
    };

    context.attach('#editor', [

		{header: 'ODA Commands'},
		/*{text: 'The Author', subMenu: [
			{header: '@jakiestfu'},
			{text: 'Website', href: 'http://jakiestfu.com/', target: '_blank'},
			{text: 'Forrst', href: 'http://forrst.com/people/jakiestfu', target: '_blank'},
			{text: 'Twitter', href: 'http://twitter.com/jakiestfu', target: '_blank'},
			{text: 'Donate?', action: function(e){
				e.preventDefault();
				$('#donate').submit();
			}}
		]},*/
        {
            text: '<span class="shortcut-text">Comment</span><span class="shortcut-key">;</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.comment', data); })
        },
        {
            text: '<span class="shortcut-text">Code -> Data</span><span class="shortcut-key">c</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.codeToData', data); })
        },
        {
            text: '<span class="shortcut-text">Data -> Code</span><span class="shortcut-key">d</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.dataToCode', data); })
        },
        {
            text: '<span class="shortcut-text">Create/Edit Function</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.makeFunction', data); })
        }
        /*,
        {divider: true}


		{text: 'Hmm?', subMenu: [
			{header: 'Well, thats lovely.'},
			{text: '2nd Level', subMenu: [
				{header: 'You like?'},
				{text: '3rd Level!?', subMenu: [
					{header: 'Of course you do'},
					{text: 'MENUCEPTION', subMenu: [
						{header:'FUCK'},
						{text: 'MAKE IT STOP!', subMenu: [
							{header: 'NEVAH!'},
							{text: 'Shieeet', subMenu: [
								{header: 'WIN'},
								{text: 'Dont Click Me', href: 'http://bit.ly/1dH1Zh1', target:'_blank', action: function(){
									_gaq.push(['_trackEvent', 'ContextJS Weezy Click', this.pathname, this.innerHTML]);
								}}
							]}
						]}
					]}
				]}
			]}
		]}*/
	]);

});
