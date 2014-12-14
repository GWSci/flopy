from flopy.mbase import Package

class ModflowLmt(Package):
    '''MT3D link package class
    No parameters implemented'''
    def __init__(self, model, output_file_name='mt3d_link.ftl', output_file_unit=54, output_file_header='extended', output_file_format='unformatted', extension ='lmt6', unitnumber=30):
        Package.__init__(self, model, extension, 'LMT6', unitnumber) # Call ancestor's init to set self.parent, extension, name and unit number
        self.heading = '# Lmt input file for MODFLOW, generated by Flopy.'
        self.url = 'lmt.htm'
        self.output_file_name='mt3d_link.ftl'
        self.output_file_unit=54
        self.output_file_header='extended'
        self.output_file_format='unformatted'
        self.parent.add_package(self)
    def __repr__( self ):
        return 'Link-MT3D package class'
    def write_file(self):
        f_lmt = open(self.fn_path, 'w')
        f_lmt.write('%s\n' % self.heading)
        f_lmt.write('%s\n' % ('OUTPUT_FILE_NAME ' + self.output_file_name))
        f_lmt.write('%s%10i\n' % ('OUTPUT_FILE_UNIT ', self.output_file_unit))
        f_lmt.write('%s\n' % ('OUTPUT_FILE_HEADER ' + self.output_file_header))
        f_lmt.write('%s\n' % ('OUTPUT_FILE_FORMAT ' + self.output_file_format))
        f_lmt.close()

