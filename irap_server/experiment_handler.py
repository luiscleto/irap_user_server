import os
import subprocess
import urllib2
import tempfile
import zipfile
from zipfile import ZipFile

from django.core import files
from django.utils.http import urlquote_plus

from irap_server import gridfs_storage
from irap_server.utils import copy_grid_file, zipdir
from irap_user_server.local_settings import IRAP_DIR, MAX_NUMBER_OF_PROCESSES
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
        # TODO replace this with system call to a proper library capable of handling any compression type
        zip_ref = ZipFile(libraries_name)
        zip_ref.extractall(IRAP_DIR + '/data/raw_data/' + exp.species)
        zip_ref.close()
    print("Files copied")
    return True


def configure_exp(exp):
    return set_config_file(exp) and create_directories(exp) and prepare_files(exp)


def save_logs(exp):
    outfile_name = IRAP_DIR + "/" + exp.title + ".out.log"
    errfile_name = IRAP_DIR + "/" + exp.title + ".err.log"

    exp.out_log.save(exp.title + ".out.log", files.File(open(outfile_name)))
    exp.err_log.save(exp.title + ".out.log", files.File(open(errfile_name)))


def run_analysis(exp):
    print("Starting analysis")
    outfile_name = IRAP_DIR + "/" + exp.title + ".out.log"
    errfile_name = IRAP_DIR + "/" + exp.title + ".err.log"
    with open(errfile_name, "w") as errfile:
        with open(outfile_name, "w") as outfile:
            errfile.write("=====================================================================\n" +
                          "========================= STARTING ANALYSIS =========================\n" +
                          "=====================================================================\n\n")
            outfile.write("=====================================================================\n" +
                          "========================= STARTING ANALYSIS =========================\n" +
                          "=====================================================================\n\n")
            result = subprocess.check_call(["irap",
                                            "conf=" + exp.title + ".conf",
                                            "mapper=tophat1",
                                            "de_method=deseq",
                                            "max_threads=" + str(MAX_NUMBER_OF_PROCESSES)],
                                           stdout=outfile, stderr=errfile)
            if result:
                exp.status = -1.0
                exp.fail_message = "IRAP failed to execute properly"
                exp.save()
                return False
    save_logs(exp)
    print("Analysis finished")
    return True


def generate_report(exp):
    print("Generating report")
    outfile_name = IRAP_DIR + "/" + exp.title + ".out.log"
    errfile_name = IRAP_DIR + "/" + exp.title + ".err.log"
    with open(errfile_name, "a") as errfile:
        with open(outfile_name, "a") as outfile:
            errfile.write("=====================================================================\n" +
                          "========================= GENERATING REPORT =========================\n" +
                          "=====================================================================\n\n")
            outfile.write("=====================================================================\n" +
                          "========================= GENERATING REPORT =========================\n" +
                          "=====================================================================\n\n")
            result = subprocess.check_call(["irap",
                                            "conf=" + exp.title + ".conf",
                                            "mapper=tophat1",
                                            "de_method=deseq",
                                            "max_threads=" + str(MAX_NUMBER_OF_PROCESSES),
                                            "report"],
                                           stdout=outfile, stderr=errfile)
            if result:
                exp.status = -1.0
                exp.fail_message = "IRAP failed to generate report"
                exp.save()
                return False
    save_logs(exp)
    report_dir = IRAP_DIR + "/" + exp.title + "/report"
    zipf = zipfile.ZipFile(report_dir + ".zip", 'w', zipfile.ZIP_DEFLATED)
    zipdir(report_dir, zipf)
    zipf.close()

    exp.results_archive.save(exp.title + ".report.zip", files.File(open(report_dir + ".zip")))

    print("Report finished")
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
        save_logs(exp)
        return
    exp.status = 80.0
    exp.save()
    if not generate_report(exp):
        print("Failed " + exp.title)
        save_logs(exp)
        return
    exp.status = 100.0
    exp.save()
    print("Finished " + exp.title)
