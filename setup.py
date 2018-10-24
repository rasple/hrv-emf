from setuptools import setup, find_packages

setup(name='hrv-emf-server',
      version='0.1',
      description='Server for HRV measurements',
      url='https://github.com/rasple/hrv-emf-server',
      author='Frank Meier',
      author_email='it16078@lehre.dhbw-stuttgart.de',
      license='GPLv3',
      packages=find_packages(),
      python_requires=">=3.3",
      install_requires=[]
      )

