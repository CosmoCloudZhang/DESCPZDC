import os
import h5py
import time
import numpy
import argparse
import opencosmo


def main(tag, folder, directory):
    '''
    Generate the photometric catalogs
    
    Arguments:
        tag (str): The tag of the configuration
        folder (str): The base folder of the catalogs
        directory (str): The base directory of the datasets
    Returns:
        duration (float): The duration of the process
    '''
    # Start
    start = time.time()
    
    # Path
    file_list = os.listdir(os.path.join(directory))
    catalog_folder = os.path.join(folder, 'CATALOG/')
    os.makedirs(os.path.join(folder, 'CATALOG/'), exist_ok=True)
    os.makedirs(os.path.join(catalog_folder, '{}/'.format(tag)), exist_ok=True)
    
    ra = numpy.array([])
    dec = numpy.array([])
    lsst_u = numpy.array([])
    lsst_g = numpy.array([])
    lsst_r = numpy.array([])
    lsst_i = numpy.array([])
    lsst_z = numpy.array([])
    lsst_y = numpy.array([])
    redshift = numpy.array([])
    redshift_true = numpy.array([])
    
    for file_name in file_list:
        catalog = opencosmo.open(os.path.join(directory, file_name))
        select = (190.0 < catalog.data['ra'].value) & (catalog.data['ra'].value < 208.0) & (catalog.data['dec'].value < 76.6)
        
        ra = numpy.concatenate([ra, catalog.data['ra'][select]])
        dec = numpy.concatenate([dec, catalog.data['dec'][select]])
        lsst_u = numpy.concatenate([lsst_u, catalog.data['lsst_u'][select]])
        lsst_g = numpy.concatenate([lsst_g, catalog.data['lsst_g'][select]])
        lsst_r = numpy.concatenate([lsst_r, catalog.data['lsst_r'][select]])
        lsst_i = numpy.concatenate([lsst_i, catalog.data['lsst_i'][select]])
        lsst_z = numpy.concatenate([lsst_z, catalog.data['lsst_z'][select]])
        lsst_y = numpy.concatenate([lsst_y, catalog.data['lsst_y'][select]])
        redshift = numpy.concatenate([redshift, catalog.data['redshift'][select]])
        redshift_true = numpy.concatenate([redshift_true, catalog.data['redshift_true'][select]])
    
    z1 = 0.0
    z2 = 3.0
    condition = (z1 < redshift_true) & (redshift_true < z2)
    
    magnitude1 = {'Y1': 16, 'Y10': 16}
    magnitude2 = {'Y1': 24.05, 'Y10': 25.30}
    condition = condition & (magnitude1[tag] < lsst_i) & (lsst_i < magnitude2[tag])
    
    # Save
    with h5py.File(os.path.join(catalog_folder, '{}/DIFFSKY.hdf5'.format(tag)), 'w') as file:
        
        file.create_dataset('ra', data=ra[condition], dtype=numpy.float32)
        file.create_dataset('dec', data=dec[condition], dtype=numpy.float32)
        file.create_dataset('mag_u_lsst', data=lsst_u[condition], dtype=numpy.float32)
        file.create_dataset('mag_g_lsst', data=lsst_g[condition], dtype=numpy.float32)
        file.create_dataset('mag_r_lsst', data=lsst_r[condition], dtype=numpy.float32)
        file.create_dataset('mag_i_lsst', data=lsst_i[condition], dtype=numpy.float32)
        file.create_dataset('mag_z_lsst', data=lsst_z[condition], dtype=numpy.float32)
        file.create_dataset('mag_y_lsst', data=lsst_y[condition], dtype=numpy.float32)
        file.create_dataset('redshift', data=redshift[condition], dtype=numpy.float32)
        file.create_dataset('redshift_true', data=redshift_true[condition], dtype=numpy.float32)
    
    # Duration
    end = time.time()
    duration = (end - start) / 60
    
    # Return
    print('Time: {:.2f} minutes'.format(duration))
    return duration


if __name__ == '__main__':
    # Input
    PARSE = argparse.ArgumentParser(description='DiffSky')
    PARSE.add_argument('--tag', type=str, required=True, help='The tag of the configuration')
    PARSE.add_argument('--folder', type=str, required=True, help='The base folder of the catalogs')
    PARSE.add_argument('--directory', type=str, required=True, help='The base directory of the datasets')
    
    # Parse
    TAG = PARSE.parse_args().tag
    FOLDER = PARSE.parse_args().folder
    DIRECTORY = PARSE.parse_args().directory
    
    # Output
    OUTPUT = main(TAG, FOLDER, DIRECTORY)