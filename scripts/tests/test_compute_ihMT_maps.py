#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile

from scilpy.io.fetcher import fetch_data, get_home, get_testing_files_dict

# If they already exist, this only takes 5 seconds (check md5sum)
fetch_data(get_testing_files_dict(), keys=['ihMT.zip'])
tmp_dir = tempfile.TemporaryDirectory()


def test_help_option(script_runner):
    ret = script_runner.run('scil_compute_ihMT_maps.py', '--help')
    assert ret.success


def test_execution_ihMT(script_runner):

    in_mask = os.path.join(get_home(), 'ihMT', 'mask.nii.gz')

    in_e1_altnp = os.path.join(get_home(),
                               'ihMT', 'echo-1_acq-altnp_ihmt.nii.gz')
    in_e2_altnp = os.path.join(get_home(),
                               'ihMT', 'echo-2_acq-altnp_ihmt.nii.gz')
    in_e3_altnp = os.path.join(get_home(),
                               'ihMT', 'echo-3_acq-altnp_ihmt.nii.gz')

    in_e1_altpn = os.path.join(get_home(),
                               'ihMT', 'echo-1_acq-altpn_ihmt.nii.gz')
    in_e2_altpn = os.path.join(get_home(),
                               'ihMT', 'echo-2_acq-altpn_ihmt.nii.gz')
    in_e3_altpn = os.path.join(get_home(),
                               'ihMT', 'echo-3_acq-altpn_ihmt.nii.gz')

    in_e1_mtoff = os.path.join(get_home(),
                               'ihMT', 'echo-1_acq-mtoff_ihmt.nii.gz')
    in_e2_mtoff = os.path.join(get_home(),
                               'ihMT', 'echo-2_acq-mtoff_ihmt.nii.gz')
    in_e3_mtoff = os.path.join(get_home(),
                               'ihMT', 'echo-3_acq-mtoff_ihmt.nii.gz')

    in_e1_neg = os.path.join(get_home(),
                             'ihMT', 'echo-1_acq-neg_ihmt.nii.gz')
    in_e2_neg = os.path.join(get_home(),
                             'ihMT', 'echo-2_acq-neg_ihmt.nii.gz')
    in_e3_neg = os.path.join(get_home(),
                             'ihMT', 'echo-3_acq-neg_ihmt.nii.gz')

    in_e1_pos = os.path.join(get_home(),
                             'ihMT', 'echo-1_acq-pos_ihmt.nii.gz')
    in_e2_pos = os.path.join(get_home(),
                             'ihMT', 'echo-2_acq-pos_ihmt.nii.gz')
    in_e3_pos = os.path.join(get_home(),
                             'ihMT', 'echo-3_acq-pos_ihmt.nii.gz')

    in_e1_t1w = os.path.join(get_home(),
                             'ihMT', 'echo-1_acq-T1w_ihmt.nii.gz')
    in_e2_t1w = os.path.join(get_home(),
                             'ihMT', 'echo-2_acq-T1w_ihmt.nii.gz')
    in_e3_t1w = os.path.join(get_home(),
                             'ihMT', 'echo-3_acq-T1w_ihmt.nii.gz')

    successes = []
    # no option
    tmp_dir = tempfile.TemporaryDirectory()
    os.chdir(os.path.expanduser(tmp_dir.name))
    ret = script_runner.run('scil_compute_ihMT_maps.py', tmp_dir.name,
                            in_mask,
                            '--in_altnp', in_e1_altnp, in_e2_altnp,
                            in_e3_altnp,
                            '--in_altpn', in_e1_altpn, in_e2_altpn,
                            in_e3_altpn,
                            '--in_mtoff', in_e1_mtoff, in_e2_mtoff,
                            in_e3_mtoff,
                            '--in_negative', in_e1_neg, in_e2_neg, in_e3_neg,
                            '--in_positive', in_e1_pos, in_e2_pos, in_e3_pos,
                            '--in_t1w', in_e1_t1w, in_e2_t1w, in_e3_t1w)
    successes.append(ret.success)

    # --out_prefix
    tmp_dir = tempfile.TemporaryDirectory()
    os.chdir(os.path.expanduser(tmp_dir.name))
    ret = script_runner.run('scil_compute_ihMT_maps.py', tmp_dir.name,
                            in_mask,
                            '--in_altnp', in_e1_altnp, in_e2_altnp,
                            in_e3_altnp,
                            '--in_altpn', in_e1_altpn, in_e2_altpn,
                            in_e3_altpn,
                            '--in_mtoff', in_e1_mtoff, in_e2_mtoff,
                            in_e3_mtoff,
                            '--in_negative', in_e1_neg, in_e2_neg, in_e3_neg,
                            '--in_positive', in_e1_pos, in_e2_pos, in_e3_pos,
                            '--in_t1w', in_e1_t1w, in_e2_t1w, in_e3_t1w,
                            '--out_prefix', 'sub_01')
    successes.append(ret.success)

    # --filtering
    tmp_dir = tempfile.TemporaryDirectory()
    os.chdir(os.path.expanduser(tmp_dir.name))
    ret = script_runner.run('scil_compute_ihMT_maps.py', tmp_dir.name,
                            in_mask,
                            '--in_altnp', in_e1_altnp, in_e2_altnp,
                            in_e3_altnp,
                            '--in_altpn', in_e1_altpn, in_e2_altpn,
                            in_e3_altpn,
                            '--in_mtoff', in_e1_mtoff, in_e2_mtoff,
                            in_e3_mtoff,
                            '--in_negative', in_e1_neg, in_e2_neg, in_e3_neg,
                            '--in_positive', in_e1_pos, in_e2_pos, in_e3_pos,
                            '--in_t1w', in_e1_t1w, in_e2_t1w, in_e3_t1w,
                            '--out_prefix', 'sub-01',
                            '--filtering')
    successes.append(ret.success)

    assert all(successes)
