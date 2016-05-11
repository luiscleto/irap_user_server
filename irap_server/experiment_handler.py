import urllib2
import tempfile

from django.core import files
from django.utils.http import urlquote_plus

from irap_server import gridfs_storage
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
    with open(IRAP_DIR + "/" + exp.title + ".conf", 'wb') as f:
        while True:
            buf = grid_file.read(16 * 1024)
            if not buf:
                break
            f.write(buf)


def configure_exp(exp):
    print("to be done one day")
    set_config_file(exp)
    return True


def start_exp(exp):
    print("Starting " + exp.title)
    if not check_files(exp):
        print("Failed " + exp.title)
        return
    exp.status = 7.0
    exp.save()
    if not configure_exp(exp):
        print("Failed " + exp.title)
        return
    exp.status = 10.0
    exp.save()
    print("Finished " + exp.title)
