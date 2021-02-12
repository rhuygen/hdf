import h5py
from pathlib import Path


def generate_test_data():

    import numpy as np

    filename = Path(__file__).parent / Path("data/sim_weather.hdf5")

    temperature = np.random.random(1024)
    wind = np.random.random(2048)
    pressure = np.random.random(512)

    f = h5py.File(filename, mode='w')

    grp = f.create_group("15")
    grp.attrs["description"] = "Weather Station 15"

    f["/15/temperature"] = temperature
    f["/15/temperature"].attrs["dt"] = 10.0
    f["/15/temperature"].attrs["start_time"] = 1375204299

    f["/15/wind"] = wind
    f["/15/wind"].attrs["dt"] = 5.0
    f["/15/wind"].attrs["start_time"] = 1375204307
    f["/15/pressure"] = pressure

    f.close()

    return filename


def test_print_attrs():

    fn = generate_test_data()
    # fn = Path(__file__).parent / Path('data/kde.hdf5')

    h5file = h5py.File(fn, mode='r')

    def print_attrs(name, obj):
        from h5 import get_type_id
        print(f"{name} [{get_type_id(obj)}]")
        for key, val in obj.attrs.items():
            print(f"    {key}: {val}")

    print()
    h5file.visititems(print_attrs)


def test_explore():

    fn = generate_test_data()
    # fn = Path(__file__).parent / Path('data/kde.hdf5')

    h5file = h5py.File(fn, mode='r')

    print()
    for key in h5file.keys():
        for ds in h5file[key].keys():
            print(f"{key}/{ds}")
