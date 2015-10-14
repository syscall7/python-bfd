#include <nc/config.h>
#include <nc/core/Context.h>
#include <nc/core/Driver.h>
#include <nc/core/likec/Tree.h>
#include <nc/core/likec/Declaration.h>
#include <nc/core/likec/PrintContext.h>

extern "C" int
snowman_decompile(char *filename, char *function)
{
    int found = -1;
    QTextStream qout(stdout, QIODevice::WriteOnly);

    nc::core::Context context;
    nc::core::Driver::parse(context, filename);
    nc::core::Driver::disassemble(context);
    nc::core::Driver::decompile(context);
    nc::core::likec::CompilationUnit *root = context.tree()->root();

    for ( auto &declaration: root->declarations()) {
        if ( !declaration->identifier().compare(function) &&
             (nc::core::likec::Declaration::FUNCTION_DEFINITION == declaration->declarationKind())) {
            nc::core::likec::PrintContext pc(qout, NULL);
            declaration->print(pc);
            qout << endl;
            found = 0;
        }
    }

    return found;
}

/* vim:set et sts=4 sw=4: */
