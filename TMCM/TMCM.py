
import TMCL

class StepRocker(object):
    def __init__(self, N0, N1=None, N2=None, port="/dev/ttyACM0", debug=False):
        self._N0 = int(N0)
        self._N1 = None if (N1 is None) else int(N1)
        self._N2 = None if (N2 is None) else int(N2)
        self.TMCL = TMCL.Device(port, debug)

    @property
    def N0(self):
        return self._N0
    
    @property
    def N1(self):
        if self._N1 is None:
            raise RuntimeError('Please set number of steps for this Motor')
        return self._N1

    @property
    def N2(self):
        if self._N2 is None:
            raise RuntimeError('Please set number of steps for this Motor')
        return self._N2

    def set_motor_steps(self, N0=None, N1=None, N2=None):
        if not (N0 is None):
            self._N0 = int(N0)
        if not (N1 is None):
            self._N1 = int(N1)
        if not (N2 is None):
            self._N2 = int(N2)

    def get_globals(self):
        ret = {}
        for key, value in TMCL.GLOBAL_PARAMETER.iteritems():
            #print "GGP:",key+value
            bank, par, name, _, _ = key+value
            ret[name] = self.TMCL.ggp(bank, par)
        return ret

    def get_parameters(self):
        retmotor = [{}, {}, {}]
        retsingle = {}
        for mn in range(3):
            for key, value in TMCL.AXIS_PARAMETER.iteritems():
                par, name, _, _ = (key,)+value
                #print "GAP:", mn, (key,)+value
                if par not in TMCL.SINGLE_AXIS_PARAMETERS:
                    retmotor[mn][name] = self.TMCL.gap(mn, par)
                elif mn == 0:
                    retsingle[name] = self.TMCL.gap(mn, par)
        return retmotor, retsingle

    def set_important_parameters(self, maxspeed=2000, maxaccel=2000,
                                maxcurrent=72, standbycurrent=32, 
                                microstep_resolution=1,store=False):
        self.TMCL.sap(0, 140, int(microstep_resolution))
        for mn in range(3):
            self.TMCL.sap(mn, 4, int(maxspeed))
            self.TMCL.sap(mn, 5, int(maxaccel))
            self.TMCL.sap(mn, 6, int(maxcurrent))
            self.TMCL.sap(mn, 7, int(standbycurrent))
        if not bool(store):
            return
        self.TMCL.stap(0, 140)
        for mn in range(3):
            self.TMCL.stap(mn, 4)
            self.TMCL.stap(mn, 5)
            self.TMCL.stap(mn, 6)
            self.TMCL.stap(mn, 7)

    def rotate(self, frequency, motor=0, direction='cw'):
        microstep_resolution = self.TMCL.gap(0, 140)
        vel = int(frequency * self.N0 * microstep_resolution)
        mn = int(motor)
        if str(direction) == 'cw':
            self.TMCL.ror(mn, vel)
        elif str(direction) == 'ccw':
            self.TMCL.rol(mn, vel)
        else:
            raise ValueError('direction needs to be either "cw" or "ccw"')
        return vel / float( self.N0 * microstep_resolution )


    def stop(self, motor=0):
        mn = int(motor)
        self.TMCL.mst(mn)


