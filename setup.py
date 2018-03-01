from setuptools import setup, find_packages


def read(*filenames, **kwargs):
    import io
    from os.path import join, dirname
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(join(dirname(__file__), filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


setup(
    name='os-spage',
    version=read('src/os_spage/VERSION'),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='MIT License',
    description='Read and write spage.',
    long_description=open('README.md').read(),
    author='Ozzy',
    author_email='cfhamlet@gmail.com',
    url='https://github.com/cfhamlet/os-spage',
    zip_safe=False,
    install_requires=['os-rotatefile', 'jsonschema'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ])
