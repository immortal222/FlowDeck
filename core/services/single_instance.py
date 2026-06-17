from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QLocalServer, QLocalSocket


class SingleInstance(QObject):
    """Ensures only a single instance of the application is running by using a local server."""

    show_main_window = pyqtSignal()

    def __init__(self, server_name="LinkWeaveApp_Server"):
        super().__init__()
        self.server_name = server_name
        self.is_running = False

        # Attempt to connect to an existing server instance
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)

        if socket.waitForConnected(500):
            # Instance is already running
            self.is_running = True
            # Send wake-up signal to the primary instance
            socket.write(b"WAKE_UP")
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
        else:
            # Primary instance: initialize the server
            self.server = QLocalServer()
            # Clean up stale server from previous crashes
            QLocalServer.removeServer(self.server_name)
            self.server.listen(self.server_name)
            self.server.newConnection.connect(self.handle_new_connection)

    def handle_new_connection(self):
        """Triggered in the primary instance when a secondary instance attempts to launch."""
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(500):
            message = socket.readAll().data().decode('utf-8')
            if message == "WAKE_UP":
                # Signal the UI to bring the main window to the front
                self.show_main_window.emit()
        socket.disconnectFromServer()
