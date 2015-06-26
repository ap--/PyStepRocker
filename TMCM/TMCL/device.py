
import serial

import codec
from consts import *
from error import *



class Device(object):
    """Abstraction of a Device that understands TMCL via a serial port"""

    def __init__(self, port="/dev/ttyACM0", debug=False,
                 MAX_MOTOR=3, MAX_BANK=4, MAX_OUTPUT=(4, 3, 5),
                 MAX_VELOCITY=2048, MAX_COORDINATE=21, MAX_POSITION=2**23):
        self._port = port
        self._debug = debug
        self._ser = serial.Serial(port)
        self.MAX_MOTOR = MAX_MOTOR
        self.MAX_BANK = MAX_BANK
        self.MAX_OUTPUT = MAX_OUTPUT
        self.MAX_VELOCITY = MAX_VELOCITY
        self.MAX_COORDINATE = MAX_COORDINATE
        self.MAX_POSITION = MAX_POSITION

    def _query(self, request):
        """Encode and send a query. Recieve, decode, and return reply"""
        req = codec.encodeRequestCommand(*request)
        if self._debug:
            print "send to TMCL:  ", req
        self._ser.write(req)
        rep = codec.decodeReplyCommand(self._ser.read(9))
        if self._debug:
            print "got from TMCL: ", rep
        return rep['status'], rep['value']

    def _pn_checkrange(self, parameter_number, value, prefix):
        """Check if value is valid for given parameter_number"""
        pn = int(parameter_number)
        v = int(value)
        DICT = AXIS_PARAMETER if type(pn) == int else GLOBAL_PARAMETER
        if not pn in DICT:
            raise TMCLKeyError(prefix, "parameter number", pn, DICT)
        name, ranges, _ = DICT[parameter_number]
        NOTINRANGE = False
        for (l, h) in ranges:
            if not (l <= v < h):
                NOTINRANGE = True
        if NOTINRANGE:
            raise TMCLMissingElement(prefix, "parameter", repr(name),
                                      " + ".join(["range({}, {})".format(l, h)
                                      for l, h in ranges]))
        return pn, v

    def ror(self, motor_number, velocity):
        """
        tmcl_ror(motor_number, velocity) --> None

        Rotate Right:
        -------------
        The motor will be instructed to rotate with a specified velocity
        in right direction (increasing the position counter).

        TMCL-Mnemonic: ROR <motor number>, <velocity>
        """
        c = 'ROR'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        v = int(velocity)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if not 0 <= v < self.MAX_VELOCITY:
            raise TMCLRangeError(c, "velocity", v, self.MAX_VELOCITY)
        status, value = self._query((0x01, cn, 0x00, mn, v))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def rol(self, motor_number, velocity):
        """
        tmcl_rol(motor_number, velocity) --> None

        Rotate Left:
        ------------
        With this command the motor will be instructed to rotate with a
        specified velocity (opposite direction compared to tmcl_rol,
        decreasing the position counter).

        TMCL-Mnemonic: ROL <motor number>, <velocity>
        """
        c = 'ROL'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        v = int(velocity)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if not 0 <= v < self.MAX_VELOCITY:
            raise TMCLRangeError(c, "velocity", v, self.MAX_VELOCITY)
        status, value = self._query((0x01, cn, 0x00, mn, v))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def mst(self, motor_number):
        """
        tmcl_mst(motor_number) --> None

        Motor Stop:
        -----------
        The motor will be instructed to stop.

        TMCL-Mnemonic: MST <motor number>
        """
        c = 'MST'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        status, value = self._query((0x01, cn, 0x00, mn, 0x00))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def mvp(self, motor_number, cmdtype, value):
        """
        tmcl_mvp(motor_number, type, value) --> None

        Move to Position:
        -----------------
        The motor will be instructed to move to a specified relative or
        absolute position or a pre-programmed coordinate. It will use
        the acceleration/deceleration ramp and the positioning speed
        programmed into the unit. This command is non-blocking: that is,
        a reply will be sent immediately after command interpretation
        and initialization of the motion controller. Further commands
        may follow without waiting for the motor reaching its end
        position. The maximum velocity and acceleration are defined by
        axis parameters #4 and #5.

        Three operation types are available:
            * Moving to an absolute position in the range from
              -8388608 to +8388607 (-2**23 to +2**23-1).
            * Starting a relative movement by means of an offset to the
              actual position. In this case, the new resulting position
              value must not exceed the above mentioned limits, too.
            * Moving the motor to a (previously stored) coordinate
              (refer to SCO for details).

        TMCL-Mnemonic: MVP <ABS|REL|COORD>, <motor number>,
                           <position|offset|coordinate number>
        """
        c = 'MVP'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        t = str(cmdtype)
        v = int(value)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if t not in CMD_MVP_TYPES:
            raise TMCLKeyError(c, "type", t, CMD_MVP_TYPES)
        if t == 'ABS' and not -self.MAX_POSITION <= v < self.MAX_POSITION:
            raise TMCLRangeError(c, t + ": value", v, -self.MAX_POSITION, self.MAX_POSITION)
        # pass 'REL' because we dont know the current pos here
        if t == 'COORDS' and not 0 <= v < self.MAX_COORDINATE:
            raise TMCLRangeError(c, t + ": value", v, self.MAX_COORDINATE)
        t = codec.byte(CMD_MVP_TYPES[t])
        status, value = self._query((0x01, cn, t, mn, v))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def rfs(self, motor_number, cmdtype):
        """
        tmcl_rfs(motor_number, cmdtype) --> int

        Reference Search:
        -----------------
        The TMCM-1110 has a built-in reference search algorithm which
        can be used. The reference search algorithm provides switching
        point calibration and three switch modes. The status of the
        reference search can also be queried to see if it has already
        finished. (In a TMCLTM program it is better to use the WAIT
        command to wait for the end of a reference search.) Please see
        the appropriate parameters in the axis parameter table to
        configure the reference search algorithm to meet your needs
        (chapter 6). The reference search can be started, stopped, and
        the actual status of the reference search can be checked.

        if cmdtype in ['START', 'STOP']:
            return 0
        if cmdtype == 'STATUS':
            return 0 if "ref-search is active" else "other values"

        TMCL-Mnemonic: RFS <START|STOP|STATUS>, <motor number>
        """
        c = 'RFS'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        t = str(cmdtype)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if t not in CMD_RFS_TYPES:
            raise TMCLKeyError(c, "type", t, CMD_RFS_TYPES)
        t = codec.byte(CMD_RFS_TYPES[t])
        status, value = self._query((0x01, cn, t, mn, 0x0000))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return value if t == CMD_RFS_TYPES['STATUS'] else 0

    def cco(self, motor_number, coordinate_number):
        """
        tmcl_cco(motor_number, coordinate_number) --> None

        Capture Coordinate:
        -------------------
        The actual position of the axis is copied to the selected
        coordinate variable. Depending on the global parameter 84, the
        coordinates are only stored in RAM or also stored in the EEPROM
        and copied back on startup (with the default setting the
        coordinates are stored in RAM only). Please see the SCO and GCO
        commands on how to copy coordinates between RAM and EEPROM.
        Note, that the coordinate number 0 is always stored in RAM only.

        TMCL-Mnemonic: CCO <coordinate number>, <motor number>
        """
        c = 'CCO'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        coord_n = int(coordinate_number)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if not 0 <= coord_n < self.MAX_COORDINATE:
            raise TMCLRangeError(c, "coordinate number", coord_n, self.MAX_COORDINATE)
        status, value = self._query((0x01, cn, coord_n, mn, 0x0000))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def sco(self, motor_number, coordinate_number, position):
        """
        tmcl_sco(self, motor_number, coordinate_number, position) --> None

        Set Coordinate:
        ---------------
        Up to 20 position values (coordinates) can be stored for every
        axis for use with the MVP COORD command. This command sets a
        coordinate to a specified value. Depending on the global
        parameter 84, the coordinates are only stored in RAM or also
        stored in the EEPROM and copied back on startup (with the
        default setting the coordinates are stored in RAM only).
        Please note that the coordinate number 0 is always stored in
        RAM only.

        TMCL-Mnemonic: SCO <coordinate number>, <motor number>, <position>
        """
        c = 'SCO'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        coord_n = int(coordinate_number)
        pos = int(position)
        if not 0 <= coord_n < self.MAX_COORDINATE:
            raise TMCLRangeError(c, "coordinate number", coord_n, self.MAX_COORDINATE)
        if not -self.MAX_POSITION <= pos < self.MAX_POSITION:
            raise TMCLRangeError(c, "position", pos, -self.MAX_POSITION, self.MAX_POSITION)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        elif not (mn == 0xFF and pos == 0):
            raise TMCLError(c, "special function requires pos == 0")
        status, value = self._query((0x01, cn, coord_n, mn, pos))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def gco(self, motor_number, coordinate_number):
        """
        tmcl_gco(self, motor_number, coordinate_number) --> int

        Get Coordinate:
        ---------------
        This command makes possible to read out a previously stored
        coordinate. In standalone mode the requested value is copied to
        the accumulator register for further processing purposes such
        as conditioned jumps. In direct mode, the value is only output
        in the value field of the reply, without affecting the
        accumulator. Depending on the global parameter 84, the
        coordinates are only stored in RAM or also stored in the EEPROM
        and copied back on startup (with the default setting the
        coordinates are stored in RAM, only).
        Please note that the coordinate number 0 is always stored in
        RAM, only.

        TMCL-Mnemonic: GCO <coordinate number>, <motor number>
        """
        c = 'GCO'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        coord_n = int(coordinate_number)
        if not 0 <= coord_n < self.MAX_COORDINATE:
            raise TMCLRangeError(c, "coordinate number", coord_n, self.MAX_COORDINATE)
        if not (0 <= mn < self.MAX_MOTOR or mn == 0xFF):
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        status, value = self._query((0x01, cn, coord_n, mn, 0))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return value

    def sio(self, port_number, state):
        """
        tmcl_sio(output_number, state) --> None

        Set Output:
        -----------
        This command sets the status of the general digital output
        either to low (0) or to high (1).

        TMCL-Mnemonic: SIO <port number>, <bank number>, <value>
        """
        c = 'SIO'
        cn = NUMBER_COMMANDS[c]
        outp = int(port_number)
        bank = 0x02
        s = bool(state)
        if not 0 <= outp < self.MAX_OUTPUT[bank]:
            raise TMCLRangeError(c, "output number", outp, self.MAX_OUTPUT[bank])
        status, value = self._query((0x01, cn, outp, bank, s))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def gio(self, port_number, bank_number):
        """
        tmcl_gio(port_number, bank_number) --> int

        Get Input / Output:
        -------------------
        With this command the status of the two available general
        purpose inputs of the module can be read out. The function
        reads a digital or analogue input port. Digital lines will read
        0 and 1, while the ADC channels deliver their 12 bit result in
        the range of 0... 4095. In direct mode the value is only output
        in the value field of the reply, without affecting the accumulator.
        The actual status of a digital output line can also be read.

        TMCL-Mnemonic: GIO <port number>, <bank number>
        """
        c = 'GIO'
        cn = NUMBER_COMMANDS[c]
        outp = int(port_number)
        bank = int(bank_number)
        if bank == 0 and not (0 <= outp < self.MAX_OUTPUT[bank]):
            raise TMCLRangeError(c, "output number @ bank{}".format(bank), outp, self.MAX_OUTPUT[bank])
        elif bank == 1 and not (0 <= outp < self.MAX_OUTPUT[bank]):
            raise TMCLRangeError(c, "output number @ bank{}".format(bank), outp, self.MAX_OUTPUT[bank])
        elif bank == 2 and not (0 <= outp < self.MAX_OUTPUT[bank]):
            raise TMCLRangeError(c, "output number @ bank{}".format(bank), outp, self.MAX_OUTPUT[bank])
        else:
            raise TMCLRangeError(c, "bank number", bank, 3)
        status, value = self._query((0x01, cn, outp, bank, 0x0000))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return value

    def sap(self, motor_number, parameter_number, value):
        """
        tmcl_sap(motor_number, parameter_number, value) --> None

        Set Axis Parameter:
        -------------------
        Most of the motion control parameters of the module can be
        specified with the SAP command. The settings will be stored in
        SRAM and therefore are volatile. That is, information will be
        lost after power off. Please use command STAP (store axis
        parameter) in order to store any setting permanently.

        TMCL-Mnemonic: SAP <parameter number>, <motor number>, <value>
        """
        c = 'SAP'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        pn = int(parameter_number)
        v = int(value)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        pn, v = self._pn_checkrange(pn, v, c)
        status, value = self._query((0x01, cn, pn, mn, v))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def gap(self, motor_number, parameter_number):
        """
        tmcl_gap(self, motor_number, parameter_number) --> int

        Get Axis Parameter:
        -------------------
        Most parameters of the TMCM-1110 can be adjusted individually
        for the axis. With this parameter they can be read out. In
        standalone mode the requested value is also transferred to the
        accumulator register for further processing purposes (such as
        conditioned jumps). In direct mode the value read is only
        output in the value field of the reply (without affecting the
        accumulator).

        TMCL-Mnemonic: GAP <parameter number>, <motor number>
        """
        c = 'GAP'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        pn = int(parameter_number)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if pn not in AXIS_PARAMETER:
            raise TMCLKeyError(c, "parameter number", pn, AXIS_PARAMETER)
        status, value = self._query((0x01, cn, pn, mn, 0x0000))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return value

    def sgp(self, bank_number, parameter_number, value):
        """
        tmcl_sgp(self, bank_number, parameter_number, value) --> None

        Set Global Parameter:
        ---------------------
        Most of the module specific parameters not directly related to
        motion control can be specified and the TMCLTM user variables
        can be changed. Global parameters are related to the host
        interface, peripherals or other application specific variables.
        The different groups of these parameters are organized in banks
        to allow a larger total number for future products. Currently,
        bank 0 and bank 1 are used for global parameters. Bank 2 is
        used for user variables and bank 3 is used for interrupt
        configuration.

        All module settings will automatically be stored non-volatile
        (internal EEPROM of the processor). The TMCLTM user variables
        will not be stored in the EEPROM automatically, but this can
        be done by using STGP commands.

        TMCL-Mnemonic: SGP <parameter number>, <bank number>, <value>
        """
        c = 'SGP'
        cn = NUMBER_COMMANDS[c]
        bn = int(bank_number)
        pn = int(parameter_number)
        v = int(value)
        if not 0 <= bn < self.MAX_BANK:
            raise TMCLRangeError(c, "bank number", bn, self.MAX_BANK)
        pn, v = self._pn_checkrange((bn, pn), v, c)
        status, value = self._query((0x01, cn, pn, bn, v))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def ggp(self, bank_number, parameter_number):
        """
        tmcl_ggp(self, bank_number, parameter_number) --> int

        Get Global Parameter:
        ---------------------
        All global parameters can be read with this function. Global
        parameters are related to the host interface, peripherals or
        application specific variables. The different groups of these
        parameters are organized in banks to allow a larger total
        number for future products. Currently, bank 0 and bank 1 are
        used for global parameters. Bank 2 is used for user variables
        and bank 3 is used for interrupt configuration. Internal
        function: the parameter is read out of the correct position
        in the appropriate device. The parameter format is converted
        adding leading zeros (or ones for negative values).

        TMCL-Mnemonic: GGP <parameter number>, <bank number>
        """
        c = 'GGP'
        cn = NUMBER_COMMANDS[c]
        bn = int(bank_number)
        pn = int(parameter_number)
        if not 0 <= bn < self.MAX_BANK:
            raise TMCLRangeError(c, "bank number", bn, self.MAX_BANK)
        if not (bn, pn) in GLOBAL_PARAMETER:
            raise TMCLKeyError(c, "parameter number @ bank{}".format(bn), pn, AXIS_PARAMETER)
        status, value = self._query((0x01, cn, pn, bn, 0x0000))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return value

    def stap(self, motor_number, parameter_number):
        """
        tmcl_stap(self, motor_number, parameter_number) --> None

        Store Axis Parameter:
        ---------------------
        An axis parameter previously set with a Set Axis Parameter
        command (SAP) will be stored permanent. Most parameters are
        automatically restored after power up.

        TMCL-Mnemonic: STAP <parameter number>, <motor number>
        """
        c = 'STAP'
        cn = NUMBER_COMMANDS[c]
        mn = int(motor_number)
        pn = int(parameter_number)
        if not 0 <= mn < self.MAX_MOTOR:
            raise TMCLRangeError(c, "motor number", mn, self.MAX_MOTOR)
        if not pn in AXIS_PARAMETER:
            raise TMCLKeyError(c, "parameter number", pn, AXIS_PARAMETER)
        status, value = self._query((0x01, cn, pn, mn, 0x0000))
        if status != STAT_OK:
            raise TMCLStatusError(c, STATUSCODES[status])
        return None

    def rsap(self):
        """
        Restore Axis Parameter:
        -----------------------

        Not yet implemented
        """
        raise NotImplementedError("yet!")

    def stgp(self):
        """
        Store Global Parameter:
        -----------------------

        Not yet implemented
        """
        raise NotImplementedError("yet!")

    def rsgp(self):
        """
        Restore Global Parameter:
        -------------------------

        Not yet implemented
        """
        raise NotImplementedError("yet!")

