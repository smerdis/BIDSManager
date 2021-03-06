import os

from .sql import SQLInterface
from .base import BIDSFolder
from ..write.dataset_writer import write_json


class DataSet(BIDSFolder):
    def __init__(self, subjects=None, *inputs, **kwargs):
        super(DataSet, self).__init__(*inputs, **kwargs)
        self.subjects = self._dict
        self._type = "Dataset"
        if subjects:
            self.add_subjects(subjects)

    def add_subjects(self, subjects):
        for subject in subjects:
            self.add_subject(subject)

    def add_subject(self, subject):
        self._add_object(subject, subject.get_id(), "Subject")

    def get_subject_ids(self):
        return sorted([subject_id for subject_id in self.subjects])

    def get_number_of_subjects(self):
        return len(self.subjects)

    def get_subject(self, subject_id):
        return self.subjects[subject_id]

    def get_subjects(self):
        return list(self.subjects.values())

    def get_images(self, modality=None, acquisition=None, subject_id=None, session=None, run_number=None,
                   group_name=None, task_name=None):
        if subject_id:
            return self.get_subject(subject_id=subject_id).get_images(modality=modality, acquisition=acquisition,
                                                                      session_name=session, run_number=run_number,
                                                                      group_name=group_name, task_name=task_name)
        else:
            images = []
            for bids_subject in self.subjects.values():
                images.extend(bids_subject.get_images(modality=modality, acquisition=acquisition, session_name=session,
                                                      run_number=run_number, group_name=group_name,
                                                      task_name=task_name))
            return images

    def get_image(self, **kwargs):
        images = self.get_images(**kwargs)
        if len(images) > 1:
            raise RuntimeError("More than one image found: ".format([image.get_path() for image in images]))
        return images[0]

    def has_subject_id(self, subject_id):
        return subject_id in self.get_subject_ids()

    def create_sql_interface(self, sql_file):
        return SQLInterface(self, sql_file)

    def update(self, move=False):
        super(DataSet, self).update(move=move)
        self.write_child_metadata("participants.tsv")
        self.write_dataset_description()

    def write_dataset_description(self):
        if self.get_metadata():
            write_json(self.get_metadata(), os.path.join(self.get_path(), "dataset_description.json"))
