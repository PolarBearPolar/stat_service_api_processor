# Import modules
import sys
from dsd import DSD
from generate_requests import generate_requests
from download_data import download_data
from transform_data import transform_data

# Get parameters from command line
dataset_id = sys.argv[1]
work_dir = sys.argv[2]
save_mode = sys.argv[3]
host_work_dir = sys.argv[4]

# Initial parameters
save_modes = ['txt', 'xlsx']

# Define run function
def run():
    global dataset_id, workdir, save_mode, save_modes
    # Check if save mode is available
    while save_mode not in save_modes:
        save_mode = input(f"Choose the save mode from the available save modes ({','.join(save_modes)}): ")
    # Get dataset
    dsd = DSD(dataset_id)
    dsd.to_string()
    # Generate requests
    filter_expression = generate_requests(dsd)
    # Download data
    filepaths = download_data(dsd, work_dir, filter_expression)
    # Transform data
    transform_data(dsd, work_dir, filepaths, save_mode, host_work_dir)
    
# Run code
if __name__ == '__main__':
    run()