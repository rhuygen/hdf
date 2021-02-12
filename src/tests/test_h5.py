import pytest

import h5
import h5py
import logging

from pathlib import Path

TEST_FILE = Path(__file__).parent / Path('data/accounts.h5')
TEST_FILE = Path(__file__).parent / Path('data/kde.hdf5')


def test_get_file():
    logging.info(f'import h5 -> {h5}')

    h5_file = h5.get_file(TEST_FILE)

    assert h5_file
    assert isinstance(h5_file, h5.File)


def test_show_file():
    h5_file = h5.get_file(TEST_FILE)

    print("-"*80)
    h5.show_file(h5_file)

    assert isinstance(h5_file, h5.File)


def test_datasets_generator():
    h5_file = h5.get_file(TEST_FILE)

    print("-"*80)
    print(h5.show_datasets(h5_file))

    for ds in h5.datasets(h5_file):
        assert isinstance(ds, h5.Dataset)


def test_groups_generator():
    h5_file = h5.get_file(TEST_FILE)

    print("-"*80)
    print(h5.show_groups(h5_file, recursive=False, max_level=1))

    for gr in h5.groups(h5_file):
        print("*" * 80)
        print(h5.show_groups(gr, max_level=5))
        assert isinstance(gr, h5.Group)


def generate_test_data():

    import numpy as np
    import h5py

    filename = Path(__file__).parent / Path("data/sim_weather.hdf5")

    temperature = np.random.random(1024)
    wind = np.random.random(2048)

    f = h5py.File(filename, mode='w')
    f["/15/temperature"] = temperature
    f["/15/temperature"].attrs["dt"] = 10.0
    f["/15/temperature"].attrs["start_time"] = 1375204299
    f["/15/wind"] = wind
    f["/15/wind"].attrs["dt"] = 5.0
    f["/15/wind"].attrs["start_time"] = 1375204299

    f.close()

    return filename

def test_load_performance():
    import time

    hdf_file = h5py.File(Path('/Users/rik/Documents/PLATO/issue#316/issue#316.hdf5'), 'r')  # this file is about 7.2GB
    time_ = time.time()

    def get_all(name):
        print(name)

    def get_objects(name, obj):
        if isinstance(obj, h5py.Dataset):
            return obj

    with hdf_file as f:
        #g = f.visit(get_all)
        group = f.visititems(get_objects)
        print(group)

    #for item in hdf_file['/Images']:
    #    x = hdf_file[f'/Images/{item}']

    print(f"{time.time() - time_}")

def test_test_data_file():

    fn = generate_test_data()

    h5_file = h5.get_file(fn, mode='r')

    print("-"*80)
    h5.show_groups(h5_file)

    dataset = h5_file["/15/temperature"]
    print(type(dataset.attrs))
    print(dir(dataset.attrs))
    attributes = dataset.attrs.items()
    print(dict(attributes))

def test_context_manager():

    fn = generate_test_data()

    with h5.get_file(fn, mode='r') as h5_file:
        h5.show_groups(h5_file)
        assert h5_file.id.valid

    with pytest.raises(ValueError):
        dataset = h5_file["/15/temperature"]

    assert not h5_file.id.valid

