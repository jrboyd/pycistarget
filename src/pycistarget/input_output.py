"""Read/write cistarget and DEM results to/from hdf5 files."""

import h5py
import numpy as np
from typing import Literal
from pycistarget.motif_enrichment_cistarget import cisTarget
import pycistarget

_CISTARGET_METADATA_FIELD = [
    "specie",
    "auc_threshold",
    "nes_threshold",
    "rank_threshold",
    "annotation_version",
    "annotation",
    "path_to_motif_annotations",
    "motif_similarity_fdr",
    "orthologous_identity_threshold",
    "motifs_to_use",
]

_DTYPE_MAPPING = {
    "Logo": "S",
    "Region_set": "S",
    "Direct_annot": "S",
    "Motif_similarity_annot": "S",
    "Orthology_annot": "S",
    "Motif_similarity_and_Orthology_annot": "S",
    "NES": np.float64,
    "AUC": np.float64,
    "Rank_at_max": np.float64,
    "Motif_hits": np.int64,
    "Target": "S",
    "Query": "S",
}


def write_cistarget(
    cistarget: cisTarget,
    path: str,
    mode: Literal["w", "a"] = "w",
):
    """
    Write cisTarget class to hdf5 file.

    Parameters
    ----------
    cistarget: cisTarget
        cisTarget class to write to disk.
    path_or_buf: Union[str, h5py.File]
        A path (str) to which to write the cisTarget class
        or a hdf5 file buffer.
    mode: Literal["w", "a"]
        Mode used to open file.
        Defaults to 'w'
    """
    h5 = h5py.File(path, mode)
    # Set root to name of cistarget run
    h5_root = h5.create_group(cistarget.name)
    
    # Save metadata
    h5_metadata_grp = h5_root.create_group("metadata")
    for metadata_field in _CISTARGET_METADATA_FIELD:
        data = getattr(cistarget, metadata_field)
        if data is not None:
            h5_metadata_grp.create_dataset(name=metadata_field, data=data)
    h5_metadata_grp.create_dataset(
        name="version",
        data=pycistarget.__version__)

    # Save cistromes
    h5_cistromes_grp = h5_root.create_group("cistromes")

    # Save database coordinates of cistromes
    h5_cistromes_database_grp = h5_cistromes_grp.create_group("database")
    for cistrome in cistarget.cistromes["Database"].keys():
        h5_cistromes_database_grp.create_dataset(
            name=cistrome,
            data=np.array(cistarget.cistromes["Database"][cistrome], dtype="S"),
        )

    # Save region_set coordinates of cistromes
    h5_cistromes_regionset_grp = h5_cistromes_grp.create_group("region_set")
    for cistrome in cistarget.cistromes["Region_set"].keys():
        h5_cistromes_regionset_grp.create_dataset(
            name=cistrome,
            data=np.array(cistarget.cistromes["Region_set"][cistrome], dtype="S"),
        )

    # Save motif_hits
    h5_motifhits_grp = h5_root.create_group("motif_hits")

    # Save database coordinates of motif hits
    h5_motifhits_database_grp = h5_motifhits_grp.create_group("database")
    for motif in cistarget.motif_hits["Database"].keys():
        h5_motifhits_database_grp.create_dataset(
            name=motif,
            data=np.array(cistarget.motif_hits["Database"][motif], dtype="S"),
        )

    # Save region_set coordinates of motif hits
    h5_motifhits_regionset_grp = h5_motifhits_grp.create_group("region_set")
    for motif in cistarget.motif_hits["Region_set"].keys():
        h5_motifhits_regionset_grp.create_dataset(
            name=motif,
            data=np.array(cistarget.motif_hits["Region_set"][motif], dtype="S"),
        )

    # Make copy of motif enrichment dataframe and set data types
    motif_enrichment = cistarget.motif_enrichment.copy()
    motif_enrichment = motif_enrichment.astype(
        {
            key: _DTYPE_MAPPING[key]
            for key in _DTYPE_MAPPING.keys()
            if key in motif_enrichment.columns
        }
    )

    # Close file handle.
    h5.close()
    

    # Write motif enrichment to disk
    motif_enrichment.to_hdf(
        path, key=f"{cistarget.name}/motif_enrichment", append=True, mode="r+"
    )

    # Make a copy of regions_to_db dataframe
    # remove index, which is a copy of the target columns
    # and set data types.
    regions_to_db = cistarget.regions_to_db.copy()
    regions_to_db.reset_index(drop=True)
    regions_to_db = regions_to_db.astype(
        {
            key: _DTYPE_MAPPING[key]
            for key in _DTYPE_MAPPING.keys()
            if key in regions_to_db.columns
        }
    )
    # Write regions_to_db to disk
    regions_to_db.to_hdf(
        path, key=f"{cistarget.name}/regions_to_db", append=True, mode="r+"
    )

def read_cistarget_hdf5():
    pass