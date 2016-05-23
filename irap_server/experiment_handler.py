from __future__ import print_function
import os
import subprocess
import urllib
import urllib2
import tempfile
import uuid
import zipfile
from zipfile import ZipFile

import mmap
from django.core import files
from django.utils.http import urlquote_plus
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from irap_server import gridfs_storage
from irap_server.utils import copy_grid_file, zipdir
from irap_user_server.local_settings import IRAP_DIR, MAX_NUMBER_OF_PROCESSES, FRONT_END_SERVER_ADDRESS
from user_server.models import RefGenome, GTFFile, Experiment


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


def upload_files_to_front(f_name, name, address, field, model):
    url = FRONT_END_SERVER_ADDRESS + "/storegridfile/"
    # Register the streaming http handlers with urllib2
    register_openers()

    # headers contains the necessary Content-Type and Content-Length
    # datagen is a generator object that yields the encoded parameters
    datagen, headers = multipart_encode({"file": open(f_name, "rb"),
                                         "name": name,
                                         "address": address,
                                         "field": field,
                                         "model": model})

    # Create the Request object
    request = urllib2.Request(url, datagen, headers)
    # Actually do the request, and get the response
    print(urllib2.urlopen(request).read())


def check_files(exp):
    print("Checking files for: " + exp.title)
    rg = exp.reference_genome
    gtf_f = exp.gtf_file
    if not rg.file_content:
        path = IRAP_DIR + "/" + str(uuid.uuid4()) + ".gz"
        local_file = open(path, "w+")
        print("Downloading reference genome...")
        res = download_file(local_file, rg.file_address)
        if res != '':
            exp.status = -1.0
            exp.fail_message = "Failed to download reference genome: " + res
            exp.save()
            return False
        local_file.close()
        upload_files_to_front(path, 'unused', rg.file_address, "file_content", "referencegenome")
        print("Finished downloading reference genome")
        os.remove(path)
    if not gtf_f.file_content:
        path = IRAP_DIR + "/" + str(uuid.uuid4()) + ".gz"
        local_file = open(path, "w+")
        print("Downloading GTF file...")
        res = download_file(local_file, gtf_f.file_address)
        if res != '':
            exp.status = -1.0
            exp.fail_message = "Failed to download GTF file: " + res
            exp.save()
            return False
        local_file.close()
        upload_files_to_front(path, 'unused', gtf_f.file_address, "file_content", "gtffile")
        print("Finished downloading GTF file")
        os.remove(path)
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

    upload_files_to_front(outfile_name, exp.title, 'http://unused.com', "out_log", "experiment")
    upload_files_to_front(errfile_name, exp.title, 'http://unused.com', "err_log", "experiment")


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
                                            "conf=" + IRAP_DIR + "/" + exp.title + ".conf",
                                            "mapper=tophat1",
                                            "de_method=deseq",
                                            "data_dir=" + IRAP_DIR + "/data",
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
                                            "conf=" + IRAP_DIR + "/" + exp.title + ".conf",
                                            "mapper=tophat1",
                                            "de_method=deseq",
                                            "data_dir=" + IRAP_DIR + "/data",
                                            "max_threads=" + str(MAX_NUMBER_OF_PROCESSES),
                                            "report"],
                                           stdout=outfile, stderr=errfile)
            if result:
                exp.status = -1.0
                exp.fail_message = "IRAP failed to generate report"
                exp.save()
                return False
    save_logs(exp)
    exp = Experiment.objects.get(title__iexact=exp.title)
    report_dir = IRAP_DIR + "/" + exp.title + "/report"
    zipf = zipfile.ZipFile(report_dir + ".zip", 'w', zipfile.ZIP_DEFLATED)
    zipdir(report_dir, zipf)
    zipf.close()

    upload_files_to_front(report_dir + ".zip", exp.title, 'http://unused.com', "results_archive", "experiment")

    print("Report finished")
    return True


def start_exp(exp):
    print("Starting " + exp.title)
    if not check_files(exp):
        print("Failed " + exp.title)
        return
    exp = Experiment.objects.get(title__iexact=exp.title)
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
    exp = Experiment.objects.get(title__iexact=exp.title)
    exp.status = 80.0
    exp.save()
    if not generate_report(exp):
        print("Failed " + exp.title)
        save_logs(exp)
        return
    exp = Experiment.objects.get(title__iexact=exp.title)
    exp.status = 100.0
    exp.save()
    print("Finished " + exp.title)
