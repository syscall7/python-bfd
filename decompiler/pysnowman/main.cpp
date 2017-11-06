#include <nc/config.h>
#include <nc/core/Context.h>
#include <nc/core/Driver.h>
#include <nc/core/likec/Tree.h>
#include <nc/core/likec/Declaration.h>
#include <stdio.h>

#define MAX_OUTPUT      2*1024*1024

char output[MAX_OUTPUT] = { '\0' };

extern "C" const char*
snowman_decompile(char *filename, char *function)
{
    nc::core::Context context;
    nc::core::Driver::parse(context, filename);
    nc::core::Driver::disassemble(context);
    nc::core::Driver::decompile(context);
    nc::core::likec::CompilationUnit *root = context.tree()->root();

    for ( auto &declaration: root->declarations()) {
        if ( !declaration->identifier().compare(function) &&
             (nc::core::likec::Declaration::FUNCTION_DEFINITION == declaration->declarationKind())) {
            QString out;
            QTextStream qout(&out, QIODevice::ReadWrite);
            declaration->print(qout);
            qout.flush();
            snprintf(output, sizeof(output), "%s", qout.readAll().toStdString().c_str());
        }
    }

    return output;
}

/* vim:set et sts=4 sw=4: */
