

var OdaScriptApi = new Object;

odaApplication.run(function(odbFile, editor){
    function OdaScriptApiContainer(odbFile, editor) {
        this.find = function(bytes, onSuccess)  {
            odbFile.find(bytes).success(onSuccess).error(function(data, status){
                console.log("Find failed: " + status);
            });
        };

        function getData(address, numUnits, onSuccess) {
            odbFile.loadDu(address, numUnits, false).success(onSuccess).error(function(data, status){
                console.log("loadDu failed: " + status);
            });
        };


        this.codeRefsToAddr = function(addr, onSuccess) {
            getData(addr, 1, function(data) {
                onSuccess(addr, data[0].crossRef);
            });
        };

        this.codeRefsFromAddr = function(addr, onSuccess) {
            getData(addr, 1, function(data) {
                onSuccess(addr, data[0].targetRef);
            });
        };

        //this.getSections = function() {
        //    return odbFile.sections;
        //};

        this.getSectionStartAddr = function(addr){
            for (var i = 0; i < odbFile.sections.length; i++){
                var section = odbFile.sections[i];
                if (section.vma <= addr && ((section.vma + section.size) >= addr)){
                    return section.vma;
                }
            }

            console.log("Section containing 0x" + addr.toString(16) + " not found" );
        };

        this.getSectionEndAddr = function(addr){
            for (var i = 0; i < odbFile.sections.length; i++){
                var section = odbFile.sections[i];
                if (section.vma <= addr && ((section.vma + section.size) >= addr)){
                    return section.vma + section.size;
                }
            }

            console.log("Section containing 0x" + addr.toString(16) + " not found" );
        };

        this.isFunction = function(addr){
            return (!(undefined == odbFile.functions[addr]));
        };

        this.getFunctionName = function(funcAddr) {
            console.log(odbFile.functions[funcAddr]);
            return odbFile.functions[funcAddr].name;
        };

        this.getFunctionReturnValue = function(funcAddr) {
            return odbFile.functions[funcAddr].retval;
        };

        this.getFunctionArgs = function(funcAddr) {
            return odbFile.functions[funcAddr].args;
        };

        this.setFunctionName = function(funcAddr, name) {
            if (! this.isFunction(funcAddr))
            {
                console.log(funcAddr.toString(16) + " is not a function");
                return;
            }

            var func = odbFile.functions[funcAddr];
            odbFile.updateFunction(funcAddr, name, func.retval, func.args);
        };

        this.setFunctionReturnValue = function(funcAddr, retval) {
            if (! this.isFunction(funcAddr))
            {
                console.log(funcAddr.toString(16) + " is not a function");
                return;
            }

            var func = odbFile.functions[funcAddr];
            odbFile.updateFunction(funcAddr, func.name, retval, func.args);
        };

        this.setFunctionArgs = function(funcAddr, args) {
            if (! this.isFunction(funcAddr))
            {
                console.log(funcAddr.toString(16) + " is not a function");
                return;
            }

            var func = odbFile.functions[funcAddr];
            odbFile.updateFunction(funcAddr, func.name, func.retval, args);
        };

        this.createFunction = function(funcAddr, name, retval, args) {
            if (this.isFunction(funcAddr))
            {
                console.log(funcAddr.toString(16) + " is already a function");
                return;
            }

            odbFile.createFunction(funcAddr, name, retval, args);
        };

        this.getFunctions = function(startAddr, endAddr){
            var funcArr = [];
            for (var i = startAddr; i <= endAddr; i++)
            {
                if (odbFile.functions[i])
                {
                    funcArr.push(i);
                }
            }
            return funcArr;
        };

        this.addComment = function(addr, comment) {
            odbFile.addComment(addr, comment);
        };

        //this.findUndefinedFunctions = function(resultObject) {
        //    odbFile.find("554889e5").success(function(findResults) {
        //        var len = findResults.length;
        //        var potentials = [];
        //        for (var i = 0; i < len; i++)
        //        {
        //            //odbFile.loadDu(findResults[i].addr, 1, false).success(function(data) {
        //                if (null == odbFile.functions[findResults[i].addr])
        //                {
        //                    console.log("potential function at: " + findResults[i].addr);
        //                    potentials.push(findResults[i]);
        //                }
        //                else
        //                {
        //                    console.log("already a function at: " + findResults[i].addr);
        //                }
        //            //});
        //        }
        //        resultObject.potentials = potentials;
        //    });
        //};

        this.gotoAddress = function(address) {
          editor.gotoAddress(address);
        };
    }

    OdaScriptApi =  new OdaScriptApiContainer(odbFile, editor);
});