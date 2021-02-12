"""
A Graphical User Interface for inspecting a HDF5 file.
"""
import argparse
import logging
import sys
import traceback

import h5py

from pathlib import Path

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout
from PyQt5.QtWidgets import QSplitter

from observer import Observable, Observer
import h5

logging.basicConfig(level=logging.INFO)
MODULE_LOGGER = logging.getLogger(__name__)


class StandardItemModel(QStandardItemModel):
    ExpandableRole = Qt.UserRole + 500

    def hasChildren(self, index):
        if self.data(index, StandardItemModel.ExpandableRole):
            return True
        return super().hasChildren(index)

    # def canFetchMore(self, parent: QModelIndex) -> bool:
    #     MODULE_LOGGER.info(f"Calling canFetchMore....")
    #     traceback.print_stack()
    #     return False
    #
    # def fetchMore(self, parent: QModelIndex) -> None:
    #     MODULE_LOGGER.info(f"Calling fetchMore....")


class HDF5UIController(Observer):
    def __init__(self, model, view):

        self.model = model
        self.view = view
        self.view.addObserver(self)

    def update(self, changed_object):
        pass

    def do(self, actions):
        pass

    def show_view(self):
        self.view.show()


class HDF5UIView(QMainWindow, Observable):
    NAME_COLUMN, SIZE_COLUMN, TYPE_COLUMN = range(3)

    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('HDF5 Inspector')

        self.init_gui()

    def init_gui(self):

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        toolbar_widget = self.create_toolbar()

        hbox = QHBoxLayout()

        split_widget = QSplitter(orientation=Qt.Horizontal)

        split_widget.addWidget(self.create_navigation_pane())
        split_widget.addWidget(self.create_inspection_pane())

        hbox.addWidget(split_widget)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def create_navigation_pane(self):
        nav_frame = QFrame()
        nav_frame.setObjectName("NavigationFrame")
        # nav_frame.setStyleSheet("background-color: rgb(43, 43, 43); margin:5px; "
        #                         "border:1px solid rgb(255, 255, 255);")

        nav_layout = QHBoxLayout()

        self.dataset_tree_model = self.create_hdf5_tree_model()
        dataset_tree = QTreeView()
        # The following line speeds up significantly when expanding a group for huge datasets
        # The first time expanded will always be slow because all data is loaded, from then
        # expanding the same group should be fast.
        dataset_tree.setUniformRowHeights(True)
        dataset_tree.setModel(self.dataset_tree_model)

        nav_layout.addWidget(dataset_tree)
        nav_frame.setLayout(nav_layout)

        # self.hdf_file = h5.get_file(Path(__file__).parent / Path('tests/data/kde.hdf5'))
        # self.hdf_file = h5.get_file(Path('/Users/rik/Documents/PLATO/issue#316/issue#316.hdf5'))  # this file is about 7.2GB
        # self.hdf_file = h5.get_file(Path('/Users/rik/Desktop/focusSweep_5540_10_135.hdf5'))
        self.hdf_file = h5.get_file(Path("/Users/rik/data/CSL/daily/MSSL_20201203_N-FEE_DUMP.hdf5"), mode='r')

        dataset_tree.expanded.connect(self.update_group_item)

        self._populate_navigation_tree(self.hdf_file, self.dataset_tree_model.invisibleRootItem())

        return nav_frame

    def create_full_group_name(self, item):
        group_name = item.text()
        while item.parent():
            item = item.parent()
            group_name = item.text() + '/' + group_name
        return '/' + group_name

    def update_group_item(self, index: QModelIndex):
        MODULE_LOGGER.info(f"{index.row()}")
        item = self.dataset_tree_model.itemFromIndex(index)
        parent = item.parent() or self.dataset_tree_model.invisibleRootItem()
        group_name = self.create_full_group_name(item)
        MODULE_LOGGER.info(f"idx={item.text()}")
        MODULE_LOGGER.info(f"group_name = {group_name}")
        MODULE_LOGGER.info(f"rowCount = {item.rowCount()}")
        group = self.hdf_file[group_name]
        if not item.rowCount():
            self._populate_navigation_tree(group, item)
        MODULE_LOGGER.info("Returning...")

    def _populate_navigation_tree(self, group, parent: QStandardItemModel):
        # print(f"Entering populate_navigation_tree with {children!r}")

        if isinstance(group, h5py.Dataset):
            return
        for child_name in group:
            child = group[child_name]
            if isinstance(child, h5py.Dataset):
                child_size = str(child.shape)
                child_type_name = str(child.dtype)
            else:
                child_size = ""
                child_type_name = h5.get_type_name(child)
            child_item = QStandardItem(child_name)
            parent.appendRow([child_item, QStandardItem(child_size), QStandardItem(child_type_name)])
            if isinstance(child, h5py.Group):
                number_of_subitems = len(child)
                if number_of_subitems:
                    child_item.setData(True, StandardItemModel.ExpandableRole)
                child_item.setData(f"{number_of_subitems} sub-items", Qt.ToolTipRole)
                # self._populate_navigation_tree(child, child_item)
                pass

    def create_hdf5_tree_model(self):
        model = StandardItemModel(0, 3)
        model.setHorizontalHeaderLabels(['Datasets', 'Size', 'Type'])
        return model

    def create_inspection_pane(self):
        inspection_frame = QFrame()
        inspection_frame.setObjectName("InspectionFrame")
        # inspection_frame.setStyleSheet("background-color: rgb(43, 43, 43); margin:5px; "
        #                                "border:1px solid rgb(255, 255, 255);")
        return inspection_frame

    def create_toolbar(self):
        pass


class HDF5UIModel:
    def __init__(self):
        pass


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", dest="filename", action="store",
                        help="The name of the HDF5 file.")
    return parser.parse_args()


def main():

    app = QApplication(sys.argv)

    args = parse_arguments()

    controller = HDF5UIController(HDF5UIModel(), HDF5UIView())

    controller.show_view()
    sys.exit(app.exec_())


if __name__ == "__main__":

    main()
    # import cProfile
    # cProfile.run("main()", sort="cumtime")

