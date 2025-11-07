import os
import h5py
import yaml
import time
import numpy
import argparse


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
    catalog_folder = os.path.join(folder, 'CATALOG/')
    os.makedirs(os.path.join(folder, 'CATALOG/'), exist_ok=True)
    os.makedirs(os.path.join(catalog_folder, '{}/'.format(tag)), exist_ok=True)
    
    dataset_directory = os.path.join(directory, 'DATASET/')
    os.makedirs(os.path.join(dataset_directory, 'CATALOG/'), exist_ok=True)
    os.makedirs(os.path.join(dataset_directory, '{}/'.format(tag)), exist_ok=True)
    
    # Load
    with open(os.path.join(dataset_directory, 'CATALOG/OBSERVE.yaml'), 'r') as file:
        observation_list = numpy.sort(yaml.safe_load(file)['healpix_pixels'])
    
    # Loop
    observation = {}
    
    for value in observation_list:
        print('ID: {}'.format(value))
        
        # Load
        with h5py.File(os.path.join(dataset_directory, 'CATALOG/OBSERVATION_{}.hdf5'.format(value)), 'r') as file:
            catalog = {key: file[key][...] for key in file.keys()}
        
        major_disk = catalog['major_disk'] * numpy.sqrt(catalog['magnification'])
        major_bulge = catalog['major_bulge'] * numpy.sqrt(catalog['magnification'])
        
        minor_disk = major_disk * (1 - catalog['ellipticity_disk']) / (1 + catalog['ellipticity_disk'])
        minor_bulge = major_bulge * (1 - catalog['ellipticity_bulge']) / (1 + catalog['ellipticity_bulge'])
        
        fraction = catalog['bulge_to_total_ratio']
        catalog['major'] = fraction * major_bulge + (1 - fraction) * major_disk
        catalog['minor'] = fraction * minor_bulge + (1 - fraction) * minor_disk
        
        factor_disk = 1.46
        factor_bulge = 4.66
        
        radius_disk = factor_disk * numpy.sqrt(major_disk * minor_disk)
        radius_bulge = factor_bulge * numpy.sqrt(major_bulge * minor_bulge)
        catalog['radius'] = numpy.sqrt(fraction * numpy.square(radius_bulge) + (1 - fraction) * numpy.square(radius_disk))
        
        condition = catalog['radius'] > 0.0
        
        # Condition
        z1 = 0.0
        z2 = 3.0
        condition = (z1 < catalog['redshift_true']) & (catalog['redshift_true'] < z2)
        
        magnitude1 = {'Y1': 16, 'Y10': 16}
        magnitude2 = {'Y1': 24.05, 'Y10': 25.30}
        condition = condition & (magnitude1[tag] < catalog['mag_i_lsst']) & (catalog['mag_i_lsst'] < magnitude2[tag])
        
        # Append
        for key in catalog.keys():
            if key in observation.keys():
                observation[key] = numpy.concatenate([observation[key], catalog[key][condition]])
            else:
                observation[key] = catalog[key][condition]
    
    # Save
    with h5py.File(os.path.join(catalog_folder, '{}/OPENUNIVERSE.hdf5'.format(tag)), 'w') as file:
        for key in observation.keys():
            file.create_dataset(key, data=observation[key], dtype=observation[key].dtype)
    
    # Duration
    end = time.time()
    duration = (end - start) / 60
    
    # Return
    print('Time: {:.2f} minutes'.format(duration))
    return duration


if __name__ == '__main__':
    # Input
    PARSE = argparse.ArgumentParser(description='Open Universe')
    PARSE.add_argument('--tag', type=str, required=True, help='The tag of the configuration')
    PARSE.add_argument('--folder', type=str, required=True, help='The base folder of the catalogs')
    PARSE.add_argument('--directory', type=str, required=True, help='The base directory of the datasets')
    
    # Parse
    TAG = PARSE.parse_args().tag
    FOLDER = PARSE.parse_args().folder
    DIRECTORY = PARSE.parse_args().directory
    
    # Output
    OUTPUT = main(TAG, FOLDER, DIRECTORY)