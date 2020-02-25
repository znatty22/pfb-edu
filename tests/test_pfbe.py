import os
import shutil

from conftest import TEST_DATA_DIR
from click.testing import CliRunner

from pfb_exporter import cli


def test_export():
    output_dir = os.path.join(TEST_DATA_DIR, 'pfb_export')
    model_dir = output_dir
    data_dir = os.path.join(TEST_DATA_DIR, 'input')

    runner = CliRunner()
    result = runner.invoke(
        cli.export, [model_dir, data_dir, '--output_dir', output_dir]
    )

    assert result.exit_code == 0


def test_transform():
    output_dir = os.path.join(TEST_DATA_DIR, 'pfb_export')
    model_dir = output_dir

    runner = CliRunner()
    result = runner.invoke(
        cli.transform, [model_dir, '--output_dir', output_dir]
    )

    assert result.exit_code == 0
