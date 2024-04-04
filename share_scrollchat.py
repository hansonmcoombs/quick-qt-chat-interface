"""
created matt_dumont
on: 26/03/24
"""
import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from pydantic import BaseModel
import sys

# modified from https://stackoverflow.com/questions/40595060/bubble-chat-weight-in-python-and-pyqt
# and https://forum.pythonguis.com/t/cloud-around-the-text-in-qtextedit/318/5

class QueryHistoryItem(BaseModel):
    username: str
    message: str
    dt: datetime.datetime

    def __hash__(self):
        return hash((self.username, self.message, self.dt))


BUBBLE_PADDING = QtCore.QMargins(15, 5, 15, 5)
TEXT_PADDING = QtCore.QMargins(25, 25, 25, 25)


class Bubble(QtWidgets.QLabel):
    def __init__(self, qhistoritem: QueryHistoryItem, color, startwidth):
        timetext = qhistoritem.dt.strftime("%D %H:%M")
        transstring = '<p style="color: rgba(0, 0, 0, 0.5);">'
        datestr = f"{transstring}<small><em>{timetext}:</em></small></p>"
        text = f"{datestr} <p>{'</p> <p>'.join(qhistoritem.message.split('\n'))}</p>"
        super(Bubble, self).__init__(text)

        self.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.background_color = color
        self.setWordWrap(True)
        self.setGeometry(0, 0, startwidth, 1000)
        self.setContentsMargins(5, 5, 5, 5)
        flags = QtCore.Qt.TextInteractionFlag.TextSelectableByMouse | QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
        self.setTextInteractionFlags(flags)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

    def paintEvent(self, e):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        p.setBrush(QtGui.QBrush(QtGui.QColor(self.background_color)))
        bubblerect = self.rect()
        bubblerect.setSize(self.sizeHint())
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.drawRoundedRect(bubblerect, 10, 10)

        super(Bubble, self).paintEvent(e)

    def sizeHint(self):
        text = self.text()
        # Calculate the dimensions the text will require.
        metrics = QtGui.QFontMetrics(QtGui.QFont())
        rect = self.rect().marginsRemoved(TEXT_PADDING)
        rect = metrics.boundingRect(rect, QtCore.Qt.TextFlag.TextWordWrap, text)
        rect = rect.marginsAdded(TEXT_PADDING)  # Re add padding for item size.
        return QtCore.QSize(rect.size().width(), rect.size().height() + 50)


class ChatLine(QtWidgets.QWidget):

    def __init__(self, qhistitem: QueryHistoryItem, color, left, startwidth, spacewidth=50):
        super(ChatLine, self).__init__()

        hbox = QtWidgets.QHBoxLayout()
        label = Bubble(qhistitem, color, startwidth - spacewidth)
        space = QtWidgets.QSpacerItem(spacewidth, 1,
                                      QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                      QtWidgets.QSizePolicy.Policy.Preferred)
        if left is not True:
            hbox.addSpacerItem(space)
            hbox.addWidget(label)

        if left is True:
            hbox.addWidget(label)
            hbox.addSpacerItem(space)

        self.setLayout(hbox)

        hbox.setContentsMargins(0, 5, 0, 5)
        self.setContentsMargins(0, 5, 0, 5)


class ScrollChat(QtWidgets.QScrollArea):

    def __init__(self, myuser, minwidth=400, colordict=None, othercolor="#a5d6a7"):
        """

        :param myuser: your username e.g. what your name would be in a QueryHistoryItem
        :param minwidth: minimum width of the chat area
        :param colordict:
        :param othercolor:
        """
        super(ScrollChat, self).__init__()
        self.chatlinewidgets = {}
        if colordict is None:
            colordict = {myuser: "#90caf9"}
        self.user = myuser
        self.colordict = colordict
        self.othercolor = othercolor
        self.minwith = minwidth

        self.view = QtWidgets.QWidget()
        self.view.setMinimumWidth(minwidth)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed)

        self.setWidgetResizable(True)
        self.setVerticalScrollBar(QtWidgets.QScrollBar(orientation=QtCore.Qt.Orientation.Vertical))
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.vbox = QtWidgets.QVBoxLayout(self.view)
        self.setWidget(self.view)

    def add_chat_item(self, query_item: QueryHistoryItem):
        left = query_item.username != self.user
        color = self.colordict.get(query_item.username, self.othercolor)
        cline = ChatLine(query_item, color, left, self.minwith)
        self.chatlinewidgets[query_item] = cline
        self.vbox.addWidget(cline)

    def remove_chat_item(self, query_item: QueryHistoryItem):
        cline = self.chatlinewidgets.pop(query_item)
        self.vbox.removeWidget(cline)
        cline.deleteLater()

    def clear_chat(self):
        i = 0
        startlen = len(self.chatlinewidgets)
        while len(self.chatlinewidgets) > 0:
            if i > startlen + 2:
                raise ValueError("Too many iterations, should not get here")
            query_item = list(self.chatlinewidgets.keys())[0]
            self.remove_chat_item(query_item)
            i += 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scrollchat = ScrollChat("me")

    scrollchat.add_chat_item(QueryHistoryItem(username='me',
                                              message="this is a test message\nwith a newline",
                                              dt=datetime.datetime.now(),
                                              enginetype="chatengine"))

    scrollchat.add_chat_item(QueryHistoryItem(username='other',
                                              message="Other persons's messsage",
                                              dt=datetime.datetime.now(),
                                              enginetype="chatengine"))

    scrollchat.add_chat_item(QueryHistoryItem(username='me',
                                              message="this is a test msessage",
                                              dt=datetime.datetime.now(),
                                              enginetype="chatengine"))

    qi = QueryHistoryItem(username='other',
                          message="Other persons's message, should be removed",
                          dt=datetime.datetime.now(),
                          enginetype="chatengine")
    scrollchat.add_chat_item(qi)

    scrollchat.add_chat_item(QueryHistoryItem(username='me',
                                              message=("Right longer message sas df asdf asdf asd fasdf asd fasdfa s "
                                                       "df asd fasdf as dfsdf asdfide this is the end"),
                                              dt=datetime.datetime.now(),
                                              enginetype="chatengine"))

    scrollchat.add_chat_item(QueryHistoryItem(
        username='other',
        message=("Other long message Lorem ipsum dolor sit amet, consectetur "
                 "adipiscing elit, sed "
                 "do eiusmod tempor incididunt ut labore \n "
                 "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                 "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse \n"
                 "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                 "culpa qui officia deserunt mollit anim id est laborum. \n "
                 "\n \n End of longboy"),
        dt=datetime.datetime.now(),
        enginetype="chatengine"))

    scrollchat.remove_chat_item(qi)

    scrollchat.show()
    sys.exit(app.exec())