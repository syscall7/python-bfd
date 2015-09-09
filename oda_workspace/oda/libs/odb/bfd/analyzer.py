__author__ = 'davis'


def analyzer_factory(arch, odb_file):
    # for now, ignore everything after the colon
    arch = arch.split(':')[0]
    name = 'oda.libs.odb.bfd.analyzers.' + arch
    try:
        mod = __import__(name)
    except ImportError as e:
        return analyzer_factory('defaultAnalyzer', odb_file)

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    initFunc = getattr(mod, arch)
    obj = initFunc(odb_file)

    return obj
