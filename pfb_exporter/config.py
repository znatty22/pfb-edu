import logging
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_OVERWRITE_OPT = True
DEFAULT_LOG_FILENAME = "pfb-export.log"
DEFAULT_TRANFORM_MOD = os.path.join(
    ROOT_DIR, 'pfb_exporter', 'transform', 'sqla.py'
)
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), 'pfb_export')
DEFAULT_DATA_DICT_FILE = 'kf-data-dict.json'
DEFAULT_AVRO_SCHEMA_FILE = 'kf-schema.avro'
DEFAULT_PFB_FILE = 'kf-pfb.avro'
