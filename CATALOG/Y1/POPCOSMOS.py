import os
import h5py
import time
import numpy
import argparse
import opencosmo


def main(tag, folder):
    '''
    Generate the photometric catalogs
    
    Arguments:
        tag (str): The tag of the configuration
        folder (str): The base folder of the catalogs
    Returns:
        duration (float): The duration of the process
    '''
    # Start
    start = time.time()
    
    # Path
    catalog_folder = os.path.join(folder, 'CATALOG/')
    os.makedirs(os.path.join(folder, 'CATALOG/'), exist_ok=True)
    os.makedirs(os.path.join(catalog_folder, '{}/'.format(tag)), exist_ok=True)
    
    with h5py.File(os.path.join(catalog_folder, 'mock_catalog_Ch1_26.hdf5'), 'r') as file:
        redshift = file['sps_parameters'][:, 15]
        mag_u_lsst = - 2.5 * numpy.log10(file['fluxes_lsst'][:, 0])
        mag_g_lsst = - 2.5 * numpy.log10(file['fluxes_lsst'][:, 1])
        mag_r_lsst = - 2.5 * numpy.log10(file['fluxes_lsst'][:, 2])
        mag_i_lsst = - 2.5 * numpy.log10(file['fluxes_lsst'][:, 3])
        mag_z_lsst = - 2.5 * numpy.log10(file['fluxes_lsst'][:, 4])
        mag_y_lsst = - 2.5 * numpy.log10(file['fluxes_lsst'][:, 5])
    
    # Condition
    z1 = 0.0
    z2 = 3.0
    condition = (z1 < redshift) & (redshift < z2)
    
    magnitude1 = {'Y1': 16, 'Y10': 16}
    magnitude2 = {'Y1': 24.05, 'Y10': 25.30}
    condition = condition & (magnitude1[tag] < mag_i_lsst) & (mag_i_lsst < magnitude2[tag])
    
    # Save
    with h5py.File(os.path.join(catalog_folder, '{}/POPCOSMOS.hdf5'.format(tag)), 'w') as file:
        
        file.create_dataset('redshift', data=redshift[condition], dtype=numpy.float32)
        file.create_dataset('mag_u_lsst', data=mag_u_lsst[condition], dtype=numpy.float32)
        file.create_dataset('mag_g_lsst', data=mag_g_lsst[condition], dtype=numpy.float32)
        file.create_dataset('mag_r_lsst', data=mag_r_lsst[condition], dtype=numpy.float32)
        file.create_dataset('mag_i_lsst', data=mag_i_lsst[condition], dtype=numpy.float32)
        file.create_dataset('mag_z_lsst', data=mag_z_lsst[condition], dtype=numpy.float32)
        file.create_dataset('mag_y_lsst', data=mag_y_lsst[condition], dtype=numpy.float32)
    
    # Duration
    end = time.time()
    duration = (end - start) / 60
    
    # Return
    print('Time: {:.2f} minutes'.format(duration))
    return duration


if __name__ == '__main__':
    # Input
    PARSE = argparse.ArgumentParser(description='PopCosmos')
    PARSE.add_argument('--tag', type=str, required=True, help='The tag of the configuration')
    PARSE.add_argument('--folder', type=str, required=True, help='The base folder of the catalogs')
    
    # Parse
    TAG = PARSE.parse_args().tag
    FOLDER = PARSE.parse_args().folder
    
    # Output
    OUTPUT = main(TAG, FOLDER)