#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a json file with DWI, T1 and fmap informations from BIDS folder
"""

import os

import argparse
from bids import BIDSLayout
from bids.layout import Query
from glob import glob
import json
import logging
import pathlib

import coloredlogs

from scilpy.io.utils import (add_overwrite_arg, add_verbose_arg,
                             assert_inputs_exist,
                             assert_outputs_exist)


conversion = {"i": "x",
              "i": "x-",
              "j": "y",
              "j-": "y-",
              "k": "z",
              "k": "z-",
              "LR": "x",
              "RL": "x-",
              "AP": "y",
              "PA": "y-"}


def _build_arg_parser():
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)

    p.add_argument("in_bids",
                   help="Input BIDS folder.")

    p.add_argument("out_json",
                   help="Output json file.")

    p.add_argument('--bids_ignore',
                   help="If you want to ignore some subjects or some files, "
                        "you can provide an extra bidsignore file.")

    p.add_argument("--fs",
                   help='Output freesurfer path. It will add keys wmparc and '
                        'aparc+aseg.')

    p.add_argument('--clean',
                   action='store_true',
                   help='If set, it will remove all the participants that '
                        'are missing any information.')

    p.add_argument("--readout", type=float, default=0.062,
                   help="Default total readout time value [%(default)s].")

    add_overwrite_arg(p)
    add_verbose_arg(p)

    return p


def _load_bidsignore_(bids_root, additional_bidsignore=None):
    """Load .bidsignore file from a BIDS dataset, returns list of regexps"""
    bids_root = pathlib.Path(bids_root)
    bids_ignore_path = bids_root / ".bidsignore"
    bids_ignores = []
    if bids_ignore_path.exists():
        bids_ignores = bids_ignores +\
                bids_ignore_path.read_text().splitlines()

    if additional_bidsignore:
        bids_ignores = bids_ignores + \
            additional_bidsignore.read_text().splitlines()

    if bids_ignores:
        import re
        import fnmatch
        return tuple(
            [
                re.compile(fnmatch.translate(bi))
                for bi in bids_ignores
                if len(bi) and bi.strip()[0] != "#"
            ]
        )
    return tuple()


def get_opposite_phase_encoding_direction(phase_encoding_direction):
    if len(phase_encoding_direction) == 2:
        return phase_encoding_direction[:-1]
    else:
        return phase_encoding_direction+'-'


def get_data(layout, nSub, dwis, t1s, fs, default_readout, clean):
    """ Return subject data

    Parameters
    ----------
    nSub : String
        Subject name

    dwis : list of BIDSFile object
        DWI objects

    t1s : List of BIDSFile object
        List of T1s associated to the current subject

    fs : List of fs paths
        List of freesurfer path

    default_readout : Float
        Default readout time

    Returns
    -------
    Dictionnary containing the metadata
    """

    bvec_path = ['todo', '']
    bval_path = ['todo', '']
    dwi_path = ['todo', '']
    totalreadout = default_readout
    PE = ['todo', '']
    topup_suffix = {'epi': ['', ''], 'sbref': ['', '']}
    nSess = 0
    nRun = 0

    if len(dwis) == 2:
        dwi_path[1] = dwis[1].path
        bvec_path[1] = layout.get_bvec(dwis[1].path)
        bval_path[1] = layout.get_bval(dwis[1].path)
        if 'direction' in dwis[1].entities:
            PE[1] = conversion[dwis[1].entities['direction']]
        elif 'PhaseEncodingDirection' in dwis[1].entities:
            PE[1] = conversion[dwis[1].entities['PhaseEncodingDirection']]

    curr_dwi = dwis[0]
    PE[0] = conversion[curr_dwi.entities['PhaseEncodingDirection']]

    if 'TotalReadoutTime' in curr_dwi.entities:
        totalreadout = curr_dwi.entities['TotalReadoutTime']

    if 'session' in curr_dwi.entities:
        nSess = curr_dwi.entities['session']

    if 'run' in curr_dwi.entities:
        nRun = curr_dwi.entities['run']

    IntendedForPath = os.path.sep.join(curr_dwi.relpath.split(os.path.sep)[1:])
    if 'TotalReadoutTime' in curr_dwi.entities:
        related_files = layout.get(IntendedFor=IntendedForPath,
                                   regex_search=True,
                                   TotalReadoutTime=totalreadout)
    else:
        related_files = layout.get(IntendedFor=IntendedForPath,
                                   regex_search=True)

    if len(related_files) == 1 and related_files[0].suffix == 'epi' and len(dwis) == 1:
        # Usual use case - 1 DWI + 1 fmap
        if 'direction' in curr_dwi.entities:
            PE[0] = conversion[curr_dwi.entities['direction']]
            if curr_dwi.entities['direction'][::-1] == related_files[0].entities['direction']:
                topup_suffix['epi'][1] = related_files[0].path
        elif 'PhaseEncodingDirection' in curr_dwi.entities:
            PE[0] = conversion[curr_dwi.entities['PhaseEncodingDirection']]
            if curr_dwi.entities['PhaseEncodingDirection'] == get_opposite_phase_encoding_direction(related_files[0].entities['PhaseEncodingDirection']):
                topup_suffix['epi'][1] = related_files[0].path
            else:
                topup_suffix['epi'][1] = related_files[0].path
    elif len(related_files) >= 2:
        direction = False
        if 'direction' in curr_dwi.entities:
            dwi_direction = curr_dwi.entities['direction']
            direction = True
        elif 'PhaseEncodingDirection' in curr_dwi.entities:
            dwi_direction = curr_dwi.entities['PhaseEncodingDirection']

        for curr_related in related_files:
            if direction:
                if dwi_direction == curr_related.entities['direction'][::-1]:
                    topup_suffix[curr_related.suffix][1] = curr_related.path
                elif dwi_direction == curr_related.entities['direction']:
                    topup_suffix[curr_related.suffix][0] = curr_related.path
            else:
                if dwi_direction == get_opposite_phase_encoding_direction(curr_related.entities['PhaseEncodingDirection']):
                    topup_suffix[curr_related.suffix][1] = curr_related.path
                elif dwi_direction == curr_related.entities['PhaseEncodingDirection']:
                    topup_suffix[curr_related.suffix][0] = curr_related.path

        if len(dwis) == 2:
            if not any(s == '' for s in topup_suffix['sbref']):
                topup = topup_suffix['sbref']
            elif not any(s == '' for s in topup_suffix['epi']):
                topup = topup_suffix['epi']
            else:
                topup = ['', '']
        elif len(dwis) == 1:
            if topup_suffix['epi'][1] != '':
                topup = topup_suffix['epi']
            else:
                topup = ['', '']
        else:
            logging.warning("""
                            BIDS structure unkown.Please send an issue:
                            https://github.com/scilus/scilpy/issues
                            """)

    # T1 setup
    t1_path = 'todo'
    wmparc_path = ''
    aparc_aseg_path = ''
    if fs:
        t1_path = fs[0]
        wmparc_path = fs[1]
        aparc_aseg_path = fs[2]
    else:
        t1_nSess = []
        if not t1s and clean:
            return {}

        for t1 in t1s:
            if 'session' in t1.entities:
                if t1.entities['session'] == nSess:
                    t1_nSess.append(t1)
            else:
                t1_nSess.append(t1)

        if len(t1_nSess) == 1:
            t1_path = t1_nSess[0].path

    return {'subject': nSub,
            'session': nSess,
            'run': nRun,
            't1': t1_path,
            'wmparc': wmparc_path,
            'aparc_aseg': aparc_aseg_path,
            'dwi': dwi_path[0],
            'bvec': bvec_path[0],
            'bval': bval_path[0],
            'rev_dwi': dwi_path[1],
            'rev_bvec': bvec_path[1],
            'rev_bval': bval_path[1],
            'topup': topup[0],
            'rev_topup': topup[1],
            'DWIPhaseEncodingDir': PE[0],
            'rev_DWIPhaseEncodingDir': PE[1],
            'TotalReadoutTime': totalreadout}


def associate_dwis(layout, nSub):
    """ Return subject data
    Parameters
    ----------
    layout: pyBIDS layout
        BIDS layout
    nSub: String
        Current subject to analyse

    Returns
    -------
    all_dwis: list
        List of dwi
    """
    all_dwis = []
    base_dict = {'subject': nSub,
                 'datatype': 'dwi',
                 'extension': 'nii.gz',
                 'suffix': 'dwi'}

    # Get possible directions
    phaseEncodingDirection = [Query.ANY, Query.ANY]
    directions = layout.get_direction(**base_dict)

    if not directions and 'PhaseEncodingDirection' in layout.get_entities():
        logging.warning("Found no directions.")
        directions = [Query.ANY, Query.ANY]
        phaseEncodingDirection = layout.get_PhaseEncodingDirection(**base_dict)
        if len(phaseEncodingDirection) <= 1:
            logging.warning("Found one phaseEncodingDirection.")
            return layout.get(part=Query.NONE, **base_dict) +\
                layout.get(part='mag', **base_dict)
    elif len(directions) == 1:
        logging.warning("Found one direction.")
        return layout.get(part=Query.NONE, **base_dict) +\
            layout.get(part='mag', **base_dict)
    elif not directions:
        logging.warning("Found no directions or PhaseEncodingDirections.")
        return layout.get(part=Query.NONE, **base_dict) +\
            layout.get(part='mag', **base_dict)

    if len(phaseEncodingDirection) > 2 or len(directions) > 2:
        logging.warning("These acquisitions have too many encoding directions.")
        return []

    all_dwis = layout.get(part=Query.NONE,
                          PhaseEncodingDirection=phaseEncodingDirection[0],
                          direction=directions[0],
                          **base_dict) +\
        layout.get(part='mag',
                   PhaseEncodingDirection=phaseEncodingDirection[0],
                   direction=directions[0],
                   **base_dict)
    all_rev_dwis = layout.get(part=Query.NONE,
                              PhaseEncodingDirection=phaseEncodingDirection[1],
                              direction=directions[1],
                              **base_dict) +\
        layout.get(part='mag',
                   PhaseEncodingDirection=phaseEncodingDirection[1],
                   direction=directions[1],
                   **base_dict)

    all_associated_dwis = []
    logging.warning('Number of dwi: {}'.format(len(all_dwis)))
    logging.warning('Number of rev_dwi: {}'.format(len(all_rev_dwis)))
    while len(all_dwis) > 0:
        curr_dwi = all_dwis[0]

        curr_association = [curr_dwi]
        rev_curr_entity = curr_dwi.get_entities()

        rev_iter_to_rm = []
        for iter_rev, rev_dwi in enumerate(all_rev_dwis):
            # At this stage, we need to check only direction
            if 'direction' in curr_dwi.entities:
                rev_curr_entity['direction'] = rev_curr_entity['direction'][::-1]
                if rev_curr_entity == rev_dwi.get_entities():
                    curr_association.append(rev_dwi)
                    rev_iter_to_rm.append(iter_rev)
            elif curr_dwi.entities['PhaseEncodingDirection'] == rev_dwi.entities['PhaseEncodingDirection'][:-1] and rev_curr_entity == rev_dwi.get_entities():
                curr_association.append(rev_dwi)
                rev_iter_to_rm.append(iter_rev)

        # drop all rev_dwi used
        logging.warning('Checking dwi {}'.format(all_dwis[0]))
        del all_dwis[0]
        for item_to_remove in rev_iter_to_rm[::-1]:
            logging.warning('Removing item {} from rev_dwi'.format(item_to_remove))
            del all_rev_dwis[item_to_remove]

        # Add to associated list
        if len(curr_association) < 3:
            all_associated_dwis.append(curr_association)
        else:
            logging.warning("These acquisitions have too many associated dwis.")
    if len(all_rev_dwis):
        for curr_rev_dwi in all_rev_dwis:
            all_associated_dwis.append([curr_rev_dwi])

    return all_associated_dwis


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, [], args.bids_ignore)
    assert_outputs_exist(parser, args, args.out_json)

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.getLogger().setLevel(log_level)
    coloredlogs.install(level=log_level)

    data = []
    layout = BIDSLayout(args.in_bids, validate=False,
                        ignore=_load_bidsignore_(args.in_bids,
                                                 args.bids_ignore))
    subjects = layout.get_subjects()
    subjects.sort()

    logging.info("Found {} subject(s)".format(len(subjects)))

    for nSub in subjects:
        mess = '# Validating subject: {}'.format(nSub)
        logging.info("-" * len(mess))
        logging.info(mess)
        dwis = associate_dwis(layout, nSub)

        fs_inputs = []
        t1s = []

        if args.fs:
            logging.info("# Looking for FS files")
            t1_fs = glob(os.path.join(args.fs, 'sub-' + nSub, 'mri/T1.mgz'))
            wmparc = glob(os.path.join(args.fs, 'sub-' + nSub, 'mri/wmparc.mgz'))
            aparc_aseg = glob(os.path.join(args.fs, 'sub-' + nSub,
                                           'mri/aparc+aseg.mgz'))
            if len(t1_fs) == 1 and len(wmparc) == 1 and len(aparc_aseg) == 1:
                fs_inputs = [t1_fs[0], wmparc[0], aparc_aseg[0]]
        else:
            logging.info("# Looking for T1 files")
            t1s = layout.get(subject=nSub,
                             datatype='anat', extension='nii.gz',
                             suffix='T1w')

        # Get the data for each run of DWIs
        for dwi in dwis:
            data.append(get_data(layout,
                                 nSub,
                                 dwi,
                                 t1s,
                                 fs_inputs,
                                 args.readout,
                                 args.clean))

    if args.clean:
        data = [d for d in data if d]

    with open(args.out_json, 'w') as outfile:
        json.dump(data,
                  outfile,
                  indent=4,
                  separators=(',', ': '),
                  sort_keys=True)
        # Add trailing newline for POSIX compatibility
        outfile.write('\n')


if __name__ == '__main__':
    main()
