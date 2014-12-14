"""
mfrch module.  Contains the ModflowRch class. Note that the user can access
the ModflowRch class as `flopy.modflow.ModflowRch`.

Additional information for this MODFLOW package can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/index.html?rch.htm>`_.

"""

import numpy as np
from flopy.mbase import Package
from flopy.utils import util_2d

class ModflowRch(Package):
    """
    MODFLOW Recharge Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.modflow.mf.Modflow`) to which
        this package will be added.
    irchcb : int
        is a flag and a unit number. (the default is 0).
    nrchop : int
        is the recharge option code. Recharge fluxes are defined in a layer
        variable, RECH, with one value for each vertical column. Accordingly,
        recharge is applied to one cell in each vertical column, and the
        option code determines which cell in the column is selected for
        recharge.
    rech : float or array of float (nrow, ncol)
        is the recharge flux. (default is 1.e-3).
    irch : int or array of int
        is the layer number variable that defines the layer in each vertical
        column where recharge is applied. (default is 1).
    extension : string
        Filename extension (default is 'rch')
    unitnumber : int
        File unit number (default is 19).

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----
    Parameters are not supported in FloPy.

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()
    >>> rch = flopy.modflow.ModflowRch(m, nrchop=3, rech=1.2e-4)

    """
    def __init__(self, model, nrchop=3, irchcb=0, rech=1e-3, irch=1,
                 extension ='rch', unitnumber=19):
        """
        Package constructor.

        """
        # Call parent init to set self.parent, extension, name and unit number
        Package.__init__(self, model, extension, 'RCH', unitnumber)
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.heading = '# RCH for MODFLOW, generated by Flopy.'
        self.url = 'rch.htm'
        self.nrchop = nrchop
        self.irchcb = irchcb
        self.rech = []
        self.irch = []
        if (not isinstance(rech, list)):
            rech = [rech]
        for i,a in enumerate(rech):
            r = util_2d(model,(nrow,ncol),np.float32,a,name='rech_'+str(i+1))
            self.rech = self.rech + [r]
        if (not isinstance(irch, list)):
            irch = [irch]
        for i,a in enumerate(irch):
            ir = util_2d(model,(nrow,ncol),np.int,a,name='irech_'+str(i+1))
            self.irch = self.irch + [ir]
        self.np = 0
        self.parent.add_package(self)

    def __repr__( self ):
        return 'Recharge class'

    def ncells( self):
        # Returns the  maximum number of cells that have recharge (developed for MT3DMS SSM package)
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        return (nrow * ncol)

    def write_file(self):
        """
        Write the file.

        """
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        f_rch = open(self.fn_path, 'w')
        f_rch.write('{0:s}\n'.format(self.heading))
        f_rch.write('{0:10d}{1:10d}\n'.format(self.nrchop,self.irchcb))
        for n in range(nper):
            if (n < len(self.rech)):
                inrech = 1
            else:
                inrech = -1
            if (n < len(self.irch)):
                inirch = 1
            else:
                inirch = -1
            comment = 'Recharge array for stress period ' + str(n + 1)
            f_rch.write('{0:10d}{1:10d} #{2:s}\n'.format(inrech, inirch,
                                                         comment))
            if (n < len(self.rech)):
                f_rch.write(self.rech[n].get_file_entry())
            if ((n < len(self.irch)) and (self.nrchop == 2)):
                f_rch.write(self.irch[n].get_file_entry())
        f_rch.close()

    @staticmethod
    def load(f, model, nper=None, ext_unit_dict=None):
        """
        Load an existing package.

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        nper : int
            The number of stress periods.  If nper is None, then nper will be
            obtained from the model object. (default is None).
        ext_unit_dict : dictionary, optional
            If the arrays in the file are specified using EXTERNAL,
            or older style array control records, then `f` should be a file
            handle.  In this case ext_unit_dict is required, which can be
            constructed using the function
            :class:`flopy.utils.mfreadnam.parsenamefile`.

        Returns
        -------
        rch : ModflowRch object
            ModflowRch object.

        Examples
        --------

        >>> import flopy
        >>> m = flopy.modflow.Modflow()
        >>> rch = flopy.modflow.mfrch.load('test.rch', m)

        """
        if type(f) is not file:
            filename = f
            f = open(filename, 'r')
        #dataset 0 -- header
        while True:
            line = f.readline()
            if line[0] != '#':
                break
        if "parameter" in line.lower():
            raw = line.strip().split()
            assert int(raw[1]) == 0,"Parameters not supported"
            line = f.readline()
        #dataset 2
        t = line.strip().split()
        nrchop = int(t[0])
        irchcb = 0
        try:
            if int(t[1]) != 0:
                irchcb = 53
        except:
            pass
        if nper is None:
            nrow, ncol, nlay, nper = model.get_nrow_ncol_nlay_nper()
        #read data for every stress period
        rech = []
        irch = []
        current_rech = []
        current_irch = []
        for iper in xrange(nper):
            line = f.readline()
            t = line.strip().split()
            inrech = int(t[0])
            if nrchop == 2:
                inirch = int(t[1])
            if inrech >= 0:
                print \
                    '   loading rech stress period {0:3d}...'.format(iper+1)
                t = util_2d.load(f, model, (nrow,ncol), np.float32, 'rech',
                                 ext_unit_dict)
                current_rech = t
            rech.append(current_rech)
            if nrchop == 2:
                if inirch >= 0:
                    print '   loading irch stress period {0:3d}...'.format(
                        iper+1)
                    t = util_2d.load(f, model, (nrow,ncol), np.int, 'irch',
                                     ext_unit_dict)
                    current_irch = t
                irch.append(current_irch)
        rch = ModflowRch(model, nrchop=nrchop, irchcb=irchcb, rech=rech,
                         irch=irch)
        return rch

