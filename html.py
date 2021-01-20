from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys

class MainWindow(QMainWindow):

    def __init__(self ):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('QWebView打开网页例子')
        self.browser = QWebEngineView()
        self.browser.setHtml('''
            <div id="live2d-widget">
            <canvas id="live2dcanvas" width="300" height="600" style="position: fixed;opacity: 0.7;right: 0px;bottom: -20px;z-index: 99999;pointer-events: none;border: 1px dashed rgb(204, 204, 204);">
            </canvas>
            </div>

            <script type="text/javascript" charset="utf-8" async="" src="https://cdn.jsdelivr.net/npm/live2d-widget@3.0.4/lib/L2Dwidget.0.min.js"></script>

            <script type="text/javascript"  src="https://cdn.jsdelivr.net/npm/live2d-widget@3.0.4/lib/L2Dwidget.min.js?_=1557308476616"></script>
            <script type="text/javascript">
            L2Dwidget.init();
            </script>
        '''
        )
        
        self.setCentralWidget(self.browser)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())