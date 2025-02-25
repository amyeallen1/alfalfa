import os
import datetime
import pytest
import tempfile
import zipfile
from unittest import TestCase
from time import sleep
from alfalfa_client.alfalfa_client import AlfalfaClient


# Consider factoring this out of the test file
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def create_zip(model_dir):
    osw_dir_path = os.path.join(os.path.dirname(__file__), 'models', model_dir)
    zip_file_fd, zip_file_path = tempfile.mkstemp(suffix='.zip')

    zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    zipdir(osw_dir_path, zipf)
    zipf.close()
    return zip_file_path


@pytest.mark.integration
class TestRefrigCaseOSW(TestCase):

    def test_simple_internal_clock(self):
        zip_file_path = create_zip('refrig_case_osw')
        alfalfa = AlfalfaClient(url='http://localhost')
        model_id = alfalfa.submit(zip_file_path)

        alfalfa.wait(model_id, "Stopped")

        alfalfa.start(
            model_id,
            external_clock="false",
            start_datetime=datetime.datetime(2019, 1, 2, 0, 0, 0),
            end_datetime=datetime.datetime(2019, 1, 3, 0, 0, 0),
            timescale=5
        )

        alfalfa.wait(model_id, "Running")
        alfalfa.stop(model_id)
        alfalfa.wait(model_id, "Stopped")

    def test_simple_external_clock(self):
        zip_file_path = create_zip('refrig_case_osw')
        alfalfa = AlfalfaClient(url='http://localhost')
        model_id = alfalfa.submit(zip_file_path)

        alfalfa.wait(model_id, "Stopped")
        start_dt = datetime.datetime(2019, 1, 2, 0, 2, 0)
        alfalfa.start(
            model_id,
            external_clock="false",
            start_datetime=start_dt,
            end_datetime=datetime.datetime(2019, 1, 3, 0, 0, 0),
            timescale=1
        )

        alfalfa.wait(model_id, "Running")

        # -- Assert model gets to expected start time
        model_time = alfalfa.get_sim_time(model_id)
        assert start_dt.strftime("%Y-%m-%d %H:%M") in model_time
        updated_dt = start_dt

        # -- Advance a single time step
        alfalfa.advance([model_id])

        # The above should hold in advance state.
        sleep(5)
        model_time = alfalfa.get_sim_time(model_id)
        updated_dt += datetime.timedelta(minutes=1)
        assert updated_dt.strftime("%Y-%m-%d %H:%M") in model_time

        # -- Advance a single time step
        alfalfa.advance([model_id])

        # The above should hold in advance state.
        sleep(65)
        model_time = alfalfa.get_sim_time(model_id)
        updated_dt += datetime.timedelta(minutes=1)
        assert updated_dt.strftime("%Y-%m-%d %H:%M") in model_time

        # Shut down
        alfalfa.stop(model_id)
        alfalfa.wait(model_id, "Stopped")
