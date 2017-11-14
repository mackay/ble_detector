
import cProfile as profiler
import pstats


def start_profiler():
    profile = profiler.Profile(timeunit=100)
    profile.enable()

    return profile


def stop_profiler(profiler, filename=None):
    filename = filename or "./profile.pf"
    profiler.disable()

    sortby = 'cumulative'
    ps = pstats.Stats(profiler).sort_stats(sortby)

    ps.print_stats(0.25)
    ps.dump_stats(filename)
