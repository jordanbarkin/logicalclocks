### Not an F1 racecar, but will walk through the data directory and create ###
### a plot for each data file, with the same name and different extension. ###
### run with `python3 plotter.py`

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(FILE_DIR, 'data')
PLOT_DIR = os.path.join(FILE_DIR, 'plots')

# give our plots some style
sns.set_style('darkgrid')


# figure out trial, port used, and clock speed for data file
# --> Assumes file extension is .txt
# --> Assumes the structure trial_<trial #>_port_<port #>_clockspeed_<clk_speed>.txt
# --> Assumes <clk_speed> ends with the string 'hz'
def decode_fname(fname):
    fname_params = fname[:-4].split('_') # nuke the last four chars
    trial = fname_params[1]
    port = fname_params[3]
    clk_speed = fname_params[5][:-2] # nuke the last two chars
    return trial, port, clk_speed

# takes in list of file names + plots together for each file
# --> logical clock time vs message queue length
# --> logical clock time vs system time
def plot_trial(fnames):
    fig, axs = plt.subplots(2, 3, sharex=True, sharey='row')

    i = 0
    for f in fnames:
        df = pd.read_csv(f)
        dir, fname = os.path.split(f)
        trial, port, clk_speed = decode_fname(fname) # note these are strs

        fig.suptitle('Trial %s' % trial, fontsize=20)

        axs[0, i].plot(df['logical_clock_time'], df['message_queue_length'])
        axs[0, i].set_title('Port %s, %s Hz' % (port, clk_speed), fontsize=16)

        axs[1, i].plot(df['logical_clock_time'], df['system_time'])
        i += 1

    axs[0, 0].set_ylabel('Message Queue Length', fontsize=14)
    axs[1, 0].set_ylabel('System Time', fontsize=14) # TODO: check the unit here?
    axs[1, 1].set_xlabel('Logical Clock Time', fontsize=14)

    fig.set_size_inches(12,6)
    save_fname = 'trial_%s.png' % (trial)
    save_fname = os.path.join(dir, save_fname)
    plt.savefig(save_fname, dpi=300)

    #plt.show()

if __name__ == '__main__':
    for subdir, dirs, files in os.walk(DATA_DIR):
        i = 1
        while True:
            curr_trial = 'trial_' + str(i)
            curr_trial_files = [os.path.join(*[DATA_DIR, subdir, f]) for f in files
                                    if (curr_trial in f) and ('.txt' in f)]

            # no more data files so stop
            if (curr_trial_files == []):
                break

            plot_trial(curr_trial_files)
            i += 1
