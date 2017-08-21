
import TMCL

class StepRocker(object):
    def __init__(self, *args, **kwargs):
        self.TMCL = TMCL.Device(*args, **kwargs)
        self.motors = range(self.TMCL.num_motors)

    def get_globals(self):
        ret = {}
        for key, value in TMCL.GLOBAL_PARAMETER.iteritems():
#            print "GGP:", key + value
            bank, par, name, _, _ = key + value
            ret[name] = self.TMCL.ggp(bank, par)
        return ret

    def get_parameters(self):
        retmotor = [{} for _ in self.motors]
        retsingle = {}
        for mn in self.motors:
            for key, value in TMCL.AXIS_PARAMETER.iteritems():
#                print "GAP:", mn, (key,) + value
                par, name, _, _ = (key,) + value
                if par not in TMCL.SINGLE_AXIS_PARAMETERS:
                    retmotor[mn][name] = self.TMCL.gap(mn, par)
                elif mn == 0:
                    retsingle[name] = self.TMCL.gap(mn, par)
        return retmotor, retsingle

    def set_important_parameters(self,
                                 max_speed=2000, max_accel=2000,
                                 max_current=72, standbycurrent=32,
                                 microstep_resolution=1, store=False):
        for mn in self.motors:
            self.TMCL.sap(mn, 4, max_speed)
            self.TMCL.sap(mn, 5, max_accel)
            self.TMCL.sap(mn, 6, max_current)
            self.TMCL.sap(mn, 7, standbycurrent)
            self.TMCL.sap(mn, 140, microstep_resolution)
            if store:
                self.TMCL.stap(mn, 4)
                self.TMCL.stap(mn, 5)
                self.TMCL.stap(mn, 6)
                self.TMCL.stap(mn, 7)
                self.TMCL.stap(mn, 140)

    def rotate(self, frequency, motor=0, steps=1, direction='cw'):
        microstep_resolution = self.TMCL.gap(motor, 140)
        vel = frequency * steps * microstep_resolution
        if direction == 'cw':
            self.TMCL.ror(motor, vel)
        elif direction == 'ccw':
            self.TMCL.rol(motor, vel)
        else:
            raise ValueError('direction needs to be either "cw" or "ccw"')

    def stop(self, motor=0):
        self.TMCL.mst(motor)


