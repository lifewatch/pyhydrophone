from setuptools import setup

setup(name='pyhydrophone',
      version='0.1',
      description='Python scripts to read hydrophones files',
      url='https://github.com/cparcerisas/pyhydrophone.git',
      author='Clea Parcerisas',
      author_email='cleaparcerisas@gmail.com',
      license='',
      packages=['pyhydrophone'],
      package_data={'pyhydrophone': ['calibration/soundtrap/*.ini']},
      zip_safe=False)