__author__ = 'davis'


def analyzer_factory(arch):
    # for now, ignore everything after the colon
    arch = arch.split(':')[0]
    name = 'odb.bfd.analyzers.' + arch
    try:
        mod = __import__(name)
    except ImportError:
        return analyzer_factory('defaultAnalyzer')

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    initFunc = getattr(mod, arch)
    obj = initFunc()

    return obj
