import pickle
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QDialog, QListWidget, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView


class Browser(QWidget):
    def __init__(self):
        super().__init__()
        icon = QIcon("assets/my_own_icon.png")
        self.setWindowIcon(icon)
        self.setWindowTitle("MyBrowser4Fun")
        self.setGeometry(50, 50, 1600, 900)

        self.webview = QWebEngineView()
        self.webview.load(QUrl("https://www.google.com/"))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.tabs.currentChanged.connect(self.update_address_bar)

        self.new_tab_btn = QPushButton("New Tab")
        self.new_tab_btn.clicked.connect(self.new_tab)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.browse)
        self.address_bar.textChanged.connect(lambda: self.update_address(QUrl(self.address_bar.text())))
        self.webview.urlChanged.connect(lambda url: self.update_address(url))
        self.webview.urlChanged.connect(self.save_to_history)

        self.browse_btn = QPushButton("Search")
        self.browse_btn.clicked.connect(self.browse)

        self.new_tab()

        self.back_btn = QPushButton("<")
        self.back_btn.clicked.connect(self.webview.back)

        self.forward_btn = QPushButton(">")
        self.forward_btn.clicked.connect(self.webview.forward)

        self.reload_btn = QPushButton("Refresh")
        self.reload_btn.clicked.connect(self.webview.reload)

        self.history_btn = QPushButton("History")
        self.history_btn.clicked.connect(self.show_history)
        self.history = []

        try:
            with open('history.pkl', 'rb') as f:
                self.history = pickle.load(f)
        except:
            pass
        app.aboutToQuit.connect(self.save_history)

        address_layout = QHBoxLayout()
        address_layout.addWidget(self.back_btn)
        address_layout.addWidget(self.forward_btn)
        address_layout.addWidget(self.reload_btn)
        address_layout.addWidget(self.address_bar)
        address_layout.addWidget(self.browse_btn)
        address_layout.addWidget(self.history_btn)
        address_layout.addWidget(self.new_tab_btn)

        layout = QVBoxLayout()
        layout.addLayout(address_layout)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def new_tab(self):
        webview = QWebEngineView()
        webview.load(QUrl("https://www.google.com/"))
        webview.urlChanged.connect(lambda url: self.update_address(url))
        self.tabs.addTab(webview, "New Tab")
        self.tabs.setCurrentWidget(webview)

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def update_address_bar(self, index):
        self.webview = self.tabs.widget(index)
        self.address_bar.setText(self.webview.url().toString())

    def update_address(self, url):
        self.webview = self.tabs.currentWidget()
        self.address_bar.setText(url.toString())

    def browse(self):
        query = self.address_bar.text()
        if "." in query and not query.startswith("http://") and not query.startswith("https://"):
            url = QUrl("http://" + query)
        else:
            url = QUrl("https://www.google.com/search?q=" + query)
        self.webview.load(url)
        self.history.append(url.toString())

    def update_address(self, url):
        if self.address_bar.text() != url.toString():
            self.address_bar.setText(url.toString())

    def show_history(self):
        history = self.get_history()
        dialog = HistoryDialog(history, self)
        dialog.exec_()

    def save_history(self):
        with open('history.pkl', 'wb') as f:
            pickle.dump(self.history, f)

    def save_to_history(self, url):
        if url.toString() not in self.history:
            self.history.append(url.toString())

    def get_history(self):
        return self.history

    def closeEvent(self, event):
        self.save_history()
        event.accept()


class HistoryDialog(QDialog):
    def __init__(self, history, parent):
        super().__init__()
        icon = QIcon("assets/my_own_icon.png")
        self.setWindowIcon(icon)
        self.setWindowTitle("History")

        self.parent = parent
        self.history_list = QListWidget()
        for url in history:
            self.history_list.addItem(url)
        self.history_list.itemClicked.connect(self.load_url)
        self.remove_btn = QPushButton("Usuń")
        self.remove_btn.clicked.connect(self.remove_item)
        layout = QVBoxLayout()
        layout.addWidget(self.history_list)
        layout.addWidget(self.remove_btn)
        self.setLayout(layout)

    def load_url(self, item):
        url = QUrl(item.text())
        if not url.toString().startswith("http://") and not url.toString().startswith("https://"):
            url = QUrl("http://" + item.text())
        self.parent.webview.load(url)

    def remove_item(self):
        selected_item = self.history_list.takeItem(self.history_list.currentRow())
        self.parent.history.remove(selected_item.text())
        del selected_item


app = QApplication(sys.argv)
browser = Browser()
browser.show()
sys.exit(app.exec_())
