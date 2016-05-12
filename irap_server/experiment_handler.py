import os
import urllib2
import tempfile
from zipfile import ZipFile

from django.core import files
from django.utils.http import urlquote_plus

from irap_server import gridfs_storage
from irap_server.utils import copy_grid_file
from irap_user_server.local_settings import IRAP_DIR
from user_server.models import RefGenome, GTFFile


def download_file(local_file, url):
    try:
        response = urllib2.urlopen(url)
        while True:
            chunk = response.read(16 * 1024)
            if not chunk:
                break
            local_file.write(chunk)
    except urllib2.URLError as e:
        return str(e.reason)
    except Exception as e:
        return str(e.message)
    return ''


def check_files(exp):
    print("Checking files for: " + exp.title)
    rg = exp.reference_genome
    gtf_f = exp.gtf_file
    if not rg.file_content:
        local_file = tempfile.NamedTemporaryFile()
        print("Downloading reference genome...")
        res = download_file(local_file, rg.file_address)
        if res != '':
            exp.status = -1.0
            exp.fail_message = "Failed to download reference genome: " + res
            exp.save()
            return False
        rg.file_content = files.File(local_file)
        rg.save()
        print("Finished downloading reference genome")
        local_file.close()
    if not gtf_f.file_content:
        local_file = tempfile.NamedTemporaryFile()
        print("Downloading GTF file...")
        res = download_file(local_file, gtf_f.file_address)
        if res != '':
            exp.status = -1.0
            exp.fail_message = "Failed to download GTF file: " + res
            exp.save()
            return False
        gtf_f.file_content = files.File(local_file)
        gtf_f.save()
        print("Finished downloading GTF file")
        local_file.close()
    return True


def set_config_file(exp):
    grid_file = gridfs_storage.open(urlquote_plus(str(exp.conf_file)[1:]))
    copy_grid_file(grid_file, IRAP_DIR + "/" + exp.title + ".conf")
    return True


def create_directories(exp):
    if not os.path.exists(IRAP_DIR + '/data/reference/' + exp.species):
        os.makedirs(IRAP_DIR + '/data/reference/' + exp.species)
    if not os.path.exists(IRAP_DIR + '/data/raw_data/' + exp.species):
        os.makedirs(IRAP_DIR + '/data/raw_data/' + exp.species)
    return True


def prepare_files(exp):
    print("Retrieving reference files and raw data...")
    rg_name = IRAP_DIR + '/data/reference/' + exp.species + '/' + exp.reference_genome.file_address.split('/')[-1]
    gtf_name = IRAP_DIR + '/data/reference/' + exp.species + '/' + exp.gtf_file.file_address.split('/')[-1]
    libraries_name = IRAP_DIR + '/data/raw_data/' + exp.species + '/' + str(exp.libraries_file)[1:]
    if not os.path.exists(rg_name):
        grid_file = gridfs_storage.open(urlquote_plus(str(exp.reference_genome.file_content)[1:]))
        copy_grid_file(grid_file, rg_name)
    if not os.path.exists(gtf_name):
        grid_file = gridfs_storage.open(urlquote_plus(str(exp.gtf_file.file_content)[1:]))
        copy_grid_file(grid_file, gtf_name)
    if not os.path.exists(libraries_name):
        grid_file = gridfs_storage.open(urlquote_plus(str(exp.libraries_file)[1:]))
        copy_grid_file(grid_file, libraries_name)
        # TODO replace this with system call to a proper library capable of handling any compression types
        zip_ref = ZipFile(libraries_name)
        zip_ref.extractall(IRAP_DIR + '/data/raw_data/' + exp.species)
        zip_ref.close()
    print("Files copied")
    return True


def configure_exp(exp):
    return set_config_file(exp) and create_directories(exp) and prepare_files(exp)


def run_analysis(exp):
    return True


def start_exp(exp):
    print("Starting " + exp.title)
    if not check_files(exp):
        print("Failed " + exp.title)
        return
    exp.status = 6.0
    exp.save()
    if not configure_exp(exp):
        print("Failed " + exp.title)
        exp.status = -1.0
        exp.fail_message = "failed to retrieve experiment files"
        exp.save()
        return
    exp.status = 8.0
    exp.save()
    if not run_analysis(exp):
        print("Failed " + exp.title)
        exp.status = -1.0
        exp.fail_message = "Analysis failed to run"
        exp.save()
        return
    exp.status = 80.0
    exp.save()
    print("Finished " + exp.title)
