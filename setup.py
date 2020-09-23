from setuptools import setup

setup(name='pyhydrophone',
      version='0.1',
      description='Python scripts to read hydrophones files',
      url='https://github.com/lifewatch/pyhydrophone.git',
      author='Clea Parcerisas',
      author_email='clea.parcerisas@vliz.com',
      license='',
      packages=['pyhydrophone'],
      package_data={'pyhydrophone': ['calibration/soundtrap/*.ini']},
      zip_safe=False)