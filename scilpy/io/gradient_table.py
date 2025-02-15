# -*- coding: utf-8 -*-

import logging
import os

import numpy as np


def save_gradient_sampling_mrtrix(bvecs, shell_idx, bvals, filename):
    """
    Save table gradient (MRtrix format)

    Parameters
    ----------
    bvecs: numpy.array
        bvecs normalized to 1.
    shell_idx: numpy.array
        Shell index for bvecs.
    bvals: numpy.array
    filename: str
        output file name
    ------
    """
    with open(filename, 'w') as f:
        for idx in range(bvecs.shape[1]):
            f.write('{:.8f} {:.8f} {:.8f} {:}\n'
                    .format(bvecs[0, idx], bvecs[1, idx], bvecs[2, idx],
                            bvals[shell_idx[idx]]))

    logging.info('Gradient sampling saved in MRtrix format as {}'
                 .format(filename))


def save_gradient_sampling_fsl(bvecs, shell_idx, bvals, filename_bval,
                               filename_bvec):
    """
    Save table gradient (FSL format)

    Parameters
    ----------
    bvecs: numpy.array
        bvecs normalized to 1.
    shell_idx: numpy.array
        Shell index for bvecs.
    bvals: numpy.array
    filename_bval: str
        output bval filename.
    filename_bvec: str
        output bvec filename.
    ------
    """
    basename, ext = os.path.splitext(filename_bval)

    np.savetxt(filename_bvec, bvecs, fmt='%.8f')
    np.savetxt(filename_bval,
               np.array([bvals[idx] for idx in shell_idx])[None, :],
               fmt='%.3f')

    logging.info('Gradient sampling saved in FSL format as {}'
                 .format(basename + '{.bvec/.bval}'))
