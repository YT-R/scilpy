#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compute the RISH (Rotationally Invariant Spherical Harmonics) features
of an SH signal [1].

Each RISH feature map is the total energy of its
associated order. Mathematically, it is the sum of the squared SH
coefficients of the SH order.

This script supports both symmetrical and asymmetrical SH images as input, of
any SH order.

Each RISH feature will be saved as a separate file.

[1] Mirzaalian, Hengameh, et al. "Harmonizing diffusion MRI data across
multiple sites and scanners." MICCAI 2015.
https://scholar.harvard.edu/files/hengameh/files/miccai2015.pdf
"""
import argparse

import nibabel as nib
import numpy as np

from scilpy.io.image import get_data_as_mask
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist, \
    assert_outputs_exist
from scilpy.reconst.sh import compute_rish


def _build_arg_parser():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('in_sh',
                   help='Path of the sh image. Must be a symmetric SH file.')
    p.add_argument('out_prefix',
                   help='Prefix of the output RISH files to save.')
    p.add_argument('--full_basis', action="store_true",
                   help="Input SH image uses a full SH basis (asymmetrical)")
    p.add_argument('--mask',
                   help='Path to a binary mask.\nOnly data inside the mask '
                        'will be used for computation.')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, [args.in_sh], optional=[args.mask])

    sh_img = nib.load(args.in_sh)
    sh = sh_img.get_fdata(dtype=np.float32)
    mask = None
    if args.mask:
        mask = get_data_as_mask(nib.load(args.mask), dtype=bool)

    rish, orders = compute_rish(sh, mask, full_basis=args.full_basis)

    # Save each RISH feature as a separate file
    for i, order_id in enumerate(orders):
        fname = "{}{}.nii.gz".format(args.out_prefix, order_id)

        # Check if file exists
        assert_outputs_exist(parser, args, fname)

        # Save RISH image
        nib.save(nib.Nifti1Image(rish[..., i], sh_img.affine), fname)


if __name__ == '__main__':
    main()
