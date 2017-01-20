import codecs
import csv
import os

from bids.base.dataset import DataSet
from bids.base.group import Group
from bids.base.session import Session
from bids.base.subject import Subject
from .image_reader import ImageReader
from .group_reader import GroupReader


class CSVReader(object):
    def __init__(self, path_to_csv_file):
        self.dataset = DataSet()
        self.path_to_csv_file = os.path.abspath(path_to_csv_file)
        self._directory = os.path.dirname(self.path_to_csv_file)

    def read_csv(self):
        with codecs.open(self.path_to_csv_file, "rU", "utf-16") as csv_file:
            reader = csv.DictReader(csv_file)
            for line in reader:
                subject_id = line["subject"]

                if not self.dataset.has_subject_id(subject_id):
                    subject = Subject(subject_id=subject_id)
                    self.dataset.add_subject(subject)
                else:
                    subject = self.dataset.get_subject(subject_id)

                session_name = line["session"]
                if not subject.has_session(session_name):
                    session = Session(name=session_name)
                    subject.add_session(session)
                else:
                    session = subject.get_session(session_name)

                image = self.read_image(line["file"], line["modality"], line['task'])
                group_name = self.modality_to_group_name(image.get_modality())

                if session.has_group(group_name):
                    group = session.get_group(group_name)
                else:
                    group = GroupReader.load_group(group_name=group_name)
                    session.add_group(group)

                group.add_image(image)

        return self.dataset

    def read_image(self, file_path, modality, task_name=None):
        modality = self.correct_modality(modality.lower())
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self._directory, file_path))
        return ImageReader.read_image(path_to_image=file_path, modality=modality, task_name=task_name)

    @staticmethod
    def correct_modality(modality):
        if "t1" in modality:
            return 'T1w'
        elif "flair" in modality:
            return 'FLAIR'
        return modality

    @staticmethod
    def modality_to_group_name(modality):
        if "bold" in modality.lower():
            return "func"
        return "anat"


def read_csv(path_to_csv_file):
    return CSVReader(path_to_csv_file).read_csv()