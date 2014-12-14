from numpy import empty,zeros
from flopy.mbase import Package

class ModflowMnw1(Package):
    '''
    NOTE: The functionality of the ADD flag in data set 4 is not supported. Also not supported are all water-quality parameters (Qwval Iqwgrp),
    water level limitations (Hlim Href DD), non-linear well losses, and pumping limitations (QCUT Q-%CUT Qfrcmn Qfrcmx DEFAULT).
    '''

    def __init__( self, model, mxmnw=0, iwl2cb=0, iwelpt=0, nomoiter=0, kspref=1,
                  wel1_bynode_qsum=None,
                  itmp=0,
                  lay_row_col_qdes_mn_multi=None,
                  mnwname=None,
                  extension='mnw1', unitnumber=33 ):
        Package.__init__(self, model, extension, 'MNW1', unitnumber) # Call ancestor's init to set self.parent, extension, name, and unit number
        self.url = 'mnw1.htm'
        self.nper = self.parent.nrow_ncol_nlay_nper[-1]
        self.heading = '# Multi-node well 1 (MNW1) file for MODFLOW, generated by Flopy'
        self.mxmnw = mxmnw              #-maximum number of multi-node wells to be simulated
        self.iwl2cb = iwl2cb            #-flag and unit number
        self.iwelpt = iwelpt            #-verbosity flag
        self.nomoiter = nomoiter        #-integer indicating the number of iterations for which flow in MNW wells is calculated
        self.kspref = kspref            #-alphanumeric key indicating which set of water levels are to be used as reference values for calculating drawdown
        self.losstype = 'SKIN'          #-string indicating head loss type for each well
        self.wel1_bynode_qsum = wel1_bynode_qsum #-nested list containing file names, unit numbers, and ALLTIME flag for auxilary output, e.g. [['test.ByNode',92,'ALLTIME']]
        self.itmp = itmp                #-array containing # of wells to be simulated for each stress period (shape = (NPER))  
        self.lay_row_col_qdes_mn_multi = lay_row_col_qdes_mn_multi  #-list of arrays containing lay, row, col, qdes, and MN or MULTI flag for all well nodes (length = NPER)
        self.mnwname = mnwname          #-string prefix name of file for outputting time series data from MNW1

        #-create empty arrays of the correct size
        self.itmp = zeros( self.nper,dtype='int32' )

        #-assign values to arrays
        self.assignarray_old( self.itmp, itmp )

        #-input format checks:
        lossTypes = ['SKIN','LINEAR']
        assert self.losstype in lossTypes, 'LOSSTYPE (%s) must be one of the following: "%s" or "%s"' % ( self.losstype, lossTypes[0], lossTypes[1] )
        auxFileExtensions = ['wl1','ByNode','Qsum']
        for each in self.wel1_bynode_qsum:
            assert each[0].split('.')[1] in auxFileExtensions, 'File extensions in "wel1_bynode_qsum" must be one of the following: ".wl1", ".ByNode", or ".Qsum".'
        assert self.itmp.max() <= self.mxmnw, 'ITMP cannot exceed maximum number of wells to be simulated.'
        
        self.parent.add_package(self)
    def __repr__( self ):
        return 'Multi-node well 1 Ppckage class'         
    def write_file( self ):
        
        #-open file for writing
        f_mnw1 = open( self.file_name[0], 'w' )

        #-write header
        f_mnw1.write( '%s\n' % self.heading )

        #-Section 1 - MXMNW IWL2CB IWELPT NOMOITER REF:kspref
        f_mnw1.write( '%10i%10i%10i%10i REF = %s\n' % ( self.mxmnw, self.iwl2cb, self.iwelpt, self.nomoiter, self.kspref) )
        
        #-Section 2 - LOSSTYPE {PLossMNW}
        f_mnw1.write( '%s\n' % ( self.losstype ) )                        

        #-Section 3a - {FILE:filename WEL1:iunw1}
        for each in self.wel1_bynode_qsum:
            if each[0].split('.')[1] == 'wl1':
                f_mnw1.write( 'FILE:%s WEL1:%10i\n' % ( each[0],each[1] ) )

        #-Section 3b - {FILE:filename BYNODE:iunby} {ALLTIME}
        for each in self.wel1_bynode_qsum:
            if each[0].split('.')[1] == 'ByNode':
                if len(each) == 2:
                    f_mnw1.write( 'FILE:%s BYNODE:%10i\n' % ( each[0],each[1] ) )
                elif len(each) == 3:
                    f_mnw1.write( 'FILE:%s BYNODE:%10i %s\n' % ( each[0],each[1],each[2] ) )

        #-Section 3C - {FILE:filename QSUM:iunqs} {ALLTIME}
        for each in self.wel1_bynode_qsum:
            if each[0].split('.')[1] == 'Qsum':
                if len(each) == 2:
                    f_mnw1.write( 'FILE:%s QSUM:%10i\n' % ( each[0],each[1] ) )
                elif len(each) == 3:
                    f_mnw1.write( 'FILE:%s QSUM:%10i %s\n' % ( each[0],each[1],each[2] ) )
        

        #-Repeat NPER times:
        for p in range(self.nper):
            #-Section 4 - ITMP ({ADD} flag is not supported)
            f_mnw1.write( '%10i\n' % ( self.itmp[p] ) )

            #-Section 5 - Lay Row Col Qdes {(MN MULTI) QWval Rw Skin Hlim Href (DD) Cp:C (QCUT Q-%CUT: Qfrcmn Qfrcmx) DEFAULT SITE: MNWsite}
            for node in self.lay_row_col_qdes_mn_multi:
                f_mnw1.write( '%10i%10i%10i %10f %s \n' % ( node[0],node[1],node[2],node[3],node[4] ) )

        #-Un-numbered section PREFIX:MNWNAME
        if self.mnwname:
            f_mnw1.write('PREFIX:%s\n' % ( self.mnwname ) )


        f_mnw1.close()

