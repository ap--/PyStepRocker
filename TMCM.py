
import TMCL

class StepRocker(object):
    def __init__(self, port="/dev/ttyACM0", debug=False):
        self.TMCL = TMCL.TMCLDevice(port, debug)

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


if __name__ == "__main__":

    rocker = StepRocker('/dev/ttyACM0')

