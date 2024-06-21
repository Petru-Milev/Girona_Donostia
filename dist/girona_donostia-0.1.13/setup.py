from setuptools import setup, find_packages

setup(
    name='girona_donostia',
    version='0.1.13',    
    description='A package to help facilitate studying of Nonlinear optical propreties',
    url='https://github.com/Petru-Milev/Girona_Donostia',
    author='Petru Milev',
    author_email='petia.md36@gmail.com',
    license='MIT',
    packages = find_packages(include=['girona_donostia', 'girona_donostia.*']),

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License' ,  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
