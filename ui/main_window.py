from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QHBoxLayout,
    QApplication, QDialog, QDialogButtonBox, QScrollArea
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import requests
import html

from logic.downloader import search_programmes, download_by_indexes
from logic.scraper import fetch_basic_info, fetch_detailed_info

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BBC get_iplayer UI")

        layout = QVBoxLayout()

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Search query (e.g. Just a Minute)")
        layout.addWidget(self.query_input)

        filter_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["radio", "tv"])
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_combo)

        self.channel_combo = QComboBox()
        self.channel_combo.addItems([
            "Radio 1", "Radio 2", "Radio 3", "Radio 4", "Radio 4 Extra",
            "Radio 5 Live", "Radio 5 Sports Extra", "Radio 6 Music",
            "Asian Network", "World Service",
            "BBC One", "BBC Two", "BBC Three", "BBC Four", "CBBC", "CBeebies",
            "BBC News", "BBC Parliament", "BBC Scotland", "BBC Alba"
        ])
        filter_layout.addWidget(QLabel("Channel:"))
        filter_layout.addWidget(self.channel_combo)

        layout.addLayout(filter_layout)

        self.search_button = QPushButton("Search")
        layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.perform_search)

        self.results_list = QListWidget()
        self.results_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.results_list)

        self.download_button = QPushButton("Download Selected")
        layout.addWidget(self.download_button)
        self.download_button.clicked.connect(self.download_selected)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def perform_search(self):
        query = self.query_input.text().strip()
        type_ = self.type_combo.currentText()
        channel = self.channel_combo.currentText()
        if not query:
            query = ".*"

        self.status_label.setText("Searching...")
        results = search_programmes(query, type_, channel)
        self.results_list.clear()

        for result in results:
            info = fetch_basic_info(result['pid'])
            title = info['title'] if info['title'] else result['title']
            description = info['description'] if info['description'] else "No description available."
            duration = info.get('duration', 'Unknown duration')

            item = QListWidgetItem(f"{result['index']}: {title}\n{duration} — {description}")
            if info['image']:
                try:
                    response = requests.get(info['image'])
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    icon = QIcon(pixmap.scaled(64, 64, Qt.KeepAspectRatio))
                    item.setIcon(icon)
                except Exception:
                    pass
            item.setData(Qt.UserRole, result['index'])
            item.setData(Qt.UserRole + 1, result['pid'])
            self.results_list.addItem(item)

        self.status_label.setText(f"Found {len(results)} results.")

    def download_selected(self):
        selected_items = [
            self.results_list.item(i)
            for i in range(self.results_list.count())
            if self.results_list.item(i).isSelected()
        ]

        if not selected_items:
            self.status_label.setText("No items selected.")
            return

        selected_info = []
        selected_indexes = []
        for item in selected_items:
            pid = item.data(Qt.UserRole + 1)
            index = item.data(Qt.UserRole)
            info = fetch_detailed_info(pid)
            info['index'] = index
            selected_info.append(info)
            selected_indexes.append(index)

        confirmed = self.show_multiple_program_details(selected_info)

        if confirmed:
            self.status_label.setText("Downloading...")
            status = download_by_indexes(selected_indexes)
            self.status_label.setText(status)
        else:
            self.status_label.setText("Download cancelled.")

    def show_multiple_program_details(self, info_list):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selected Programmes")
        dialog.setMinimumSize(600, 600)

        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        for info in info_list:
            block = QVBoxLayout()

            title_label = QLabel(f"<h2>{html.escape(info['title'])}</h2>")
            title_label.setTextFormat(Qt.RichText)
            block.addWidget(title_label)

            duration_label = QLabel(f"<b>Duration:</b> {html.escape(info.get('duration', 'Unknown'))}")
            duration_label.setTextFormat(Qt.RichText)
            block.addWidget(duration_label)

            description_label = QLabel(html.escape(info['description']))
            description_label.setWordWrap(True)
            block.addWidget(description_label)
            if info.get('image'):
                try:
                    response = requests.get(info['image'], timeout=5)
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap.scaledToWidth(400, Qt.SmoothTransformation))
                    block.addWidget(image_label)
                except Exception:
                    pass

            if info.get('tracks'):
                tracks_html = "<b>Tracks:</b><ul>"
                for track in info['tracks']:
                    safe_track = html.escape(track)
                    tracks_html += f"<li>{safe_track}</li>"
                tracks_html += "</ul>"
                tracks_label = QLabel(tracks_html)
                tracks_label.setTextFormat(Qt.RichText)
                tracks_label.setWordWrap(True)
                block.addWidget(tracks_label)

            block.addSpacing(20)
            block_widget = QWidget()
            block_widget.setLayout(block)
            content_layout.addWidget(block_widget)

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        result = dialog.exec_()
        return result == QDialog.Accepted
