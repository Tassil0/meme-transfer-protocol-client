import os
import sys
import gi
import socket
import pynetstring
import base64
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

def main():
    try:
        win = MainWindow()
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception:
        print(Exception)
    sys.exit(0)


def check_server(ip: str):
    try:
        return os.system("ping -c 1 " + ip)
    except Exception:
        return Exception


def resize_image(img: str):
    # pix = GdkPixbuf.Pixbuf.new_from_file(img)
    # return pix.scale_simple(200, 150, GdkPixbuf.Pixbuf.INTERP_BILINEAR)
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(img, 150, 150, True)


class Sock():
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.datalength = 0

    def open_main(self, nick: str) -> [str, int]:
        self.send_msg('MTP V:1.0')
        print('msg with version sent')
        res = self.recv_full_msg()
        print(res)
        if res == 'S MTP V:1.0':
            print('Connection initialized')
        else:
            self.send_err('wrong vesrion')
            print('wrong version')
        self.send_msg(nick)
        token = self.recv_msg()
        port = self.recv_msg()
        return token, int(port)

    def close_main(self, dtoken: str) -> [int]:
        server_msglength = int(self.recv_msg())
        self.send_msg(dtoken)
        if not self.recv_msg() == 'ACK':
            self.send_err('expected S ACK')
            print('expected S ACK')
        self.sock.close()
        return server_msglength, self.datalength

    def open_data(self, nick: str, token: str) -> int:
        self.send_msg(nick)
        server_token = self.recv_msg()
        if server_token == token:
            return 0
        return 1

    def close_data(self) -> tuple[str, int]:
        res = self.recv_msg()
        if not res.split(':')[0] == 'END':
            self.send_err('expected END:<dtoken>')
            print('expected END:<dtoken>')
        self.sock.close()  # ukončit data channel
        # return dtoken
        return res.split(':')[1], self.datalength

    def handle_requests(self, meme: str, description: str, nsfw: bool, password: str):
        for i in range(4):
            res = self.recv_msg()
            print(res)
            if res == 'REQ:meme':
                meme = self.encode_meme(meme)
                data_length = len(meme)
                self.send_meme(meme)
                print('meme sent')
            elif res == 'REQ:description':
                self.send_msg(description)
                data_length = len(description)
                print('description sent')
            elif res == 'REQ:isNSFW':
                if nsfw:
                    self.send_msg("true")
                    data_length = 4
                else:
                    self.send_msg("false")
                    data_length = 5
                print('nsfw sent')
            elif res == 'REQ:password':
                self.send_msg(password)
                data_length = len(password)
                print('pass sent')
            res = self.recv_msg()
            print(res)
            server_datalength = int(res.split(':')[1])
            if server_datalength == data_length:
                print('sent data integrity checked')
            else:
                self.send_err('data integrity broken')
                print('data integrity broken')


    def send_msg(self, msg: str):
        self.datalength = self.datalength + len(msg)
        self.sock.sendall(pynetstring.encode(bytes('C ' + msg, 'utf-8')))

    def send_meme(self, meme: bytes):
        self.datalength = self.datalength + len(meme)
        self.sock.sendall(pynetstring.encode(b'C ' + meme))

    def recv_msg(self) -> str:
        return pynetstring.decode(self.sock.recv(1024))[0].decode('utf-8').split(' ')[1]

    def recv_full_msg(self) -> str:
        return pynetstring.decode(self.sock.recv(1024))[0].decode('utf-8')

    def send_err(self, err: str):
        self.sock.sendall(pynetstring.encode(bytes('E ' + err, 'utf-8')))

    def encode_meme(self, meme: str) -> bytes:
        with open(meme, 'rb') as f:
            data = base64.b64encode(f.read())
        return data


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Meme Transfer Protocol")

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = "Meme Transfer Protocol"

        self.file = ""

        # Main content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.add(header_bar)

        # image
        self.img = Gtk.Image()
        self.img.set_margin_top(20)
        self.img.set_margin_bottom(20)
        self.img.set_halign(Gtk.Align.CENTER)
        allocation = content.get_allocation()

        # LABELS
        # IP label
        label_ip = Gtk.Label()
        label_ip.set_text("IP Address:")
        # Port label
        label_port = Gtk.Label()
        label_port.set_text("Port:")
        # Nick label
        label_nick = Gtk.Label()
        label_nick.set_text("Nick:")
        # Password label
        label_password = Gtk.Label()
        label_password.set_text("Password:")
        # NSFW label
        label_nsfw = Gtk.Label()
        label_nsfw.set_text("NSFW")
        # Description label
        label_description = Gtk.Label()
        label_description.set_text("Description:")
        # Server Status label
        self.label_server = Gtk.Label()
        self.label_server.set_halign(Gtk.Align.START)
        # Status label
        self.label_status = Gtk.Label()
        self.label_status.set_halign(Gtk.Align.END)

        # ENTRIES / INPUTS
        # Entry fields
        self.entry_ip = Gtk.Entry(placeholder_text="159.89.4.84")
        self.entry_port = Gtk.Entry(placeholder_text="42069")
        self.entry_nick = Gtk.Entry(placeholder_text="Karlos")
        self.entry_password = Gtk.Entry(placeholder_text="silnehelso")
        self.switch_nsfw = Gtk.Switch()
        self.switch_nsfw.set_halign(Gtk.Align.CENTER)
        self.entry_description = Gtk.Entry(placeholder_text="description")

        # BUTTONS
        # Choose file button
        btn_file = Gtk.Button()
        btn_file.set_label(f'Choose MEME')
        btn_file.connect('clicked', self.btn_file_on_click)
        # send button
        btn_send = Gtk.Button()
        btn_send.set_label(f'Send MEME')
        btn_send.connect('clicked', self.btn_send_on_click)
        # refresh server status
        btn_refresh = Gtk.Button()
        btn_refresh.set_label(f'Refresh')
        btn_refresh.connect('clicked', self.btn_refresh_on_click)

        # Input Entries Grid
        entry_grid = Gtk.Grid()
        entry_grid.set_row_spacing(20)
        entry_grid.set_column_spacing(20)
        entry_grid.set_margin_start(20)
        entry_grid.set_margin_end(20)
        entry_grid.set_margin_top(20)
        # second row (label_ip, entry_ip, label_port, entry_port)
        entry_grid.attach(label_ip, 0, 0, 1, 1)
        entry_grid.attach_next_to(self.entry_ip, label_ip, Gtk.PositionType.RIGHT, 1, 1)
        entry_grid.attach_next_to(label_port, self.entry_ip, Gtk.PositionType.RIGHT, 1, 1)
        entry_grid.attach_next_to(self.entry_port, label_port, Gtk.PositionType.RIGHT, 1, 1)
        # third row (label_nick, entry_nick, label_password, entry_password)
        entry_grid.attach(label_nick, 0, 1, 1, 1)
        entry_grid.attach_next_to(self.entry_nick, label_nick, Gtk.PositionType.RIGHT, 1, 1)
        entry_grid.attach_next_to(label_password, self.entry_nick, Gtk.PositionType.RIGHT, 1, 1)
        entry_grid.attach_next_to(self.entry_password, label_password, Gtk.PositionType.RIGHT, 1, 1)
        # checkbox row
        entry_grid.attach(label_nsfw, 0, 2, 1, 1)
        entry_grid.attach_next_to(self.switch_nsfw, label_nsfw, Gtk.PositionType.RIGHT, 1, 1)
        # description row
        entry_grid.attach(label_description, 0, 3, 1, 1)
        entry_grid.attach_next_to(self.entry_description, label_description, Gtk.PositionType.RIGHT, 4, 1)
        # add entry Grid to window
        content.add(entry_grid)

        # image
        content.add(self.img)

        # Button grid
        btn_grid = Gtk.Grid()
        btn_grid.set_column_spacing(20)
        btn_grid.set_halign(Gtk.Align.CENTER)
        btn_grid.attach(btn_file, 0, 0, 1, 1)
        btn_grid.attach_next_to(btn_send, btn_file, Gtk.PositionType.RIGHT, 1, 1)
        # add button grid to window
        content.add(btn_grid)

        # Status grid
        status_grid = Gtk.Grid()
        status_grid.set_column_spacing(50)
        status_grid.set_margin_start(20)
        status_grid.set_margin_top(20)
        status_grid.set_margin_bottom(20)
        status_grid.set_halign(Gtk.Align.FILL)
        status_grid.attach(btn_refresh, 0, 0, 1, 1)
        status_grid.attach_next_to(self.label_server, btn_refresh, Gtk.PositionType.RIGHT, 1, 1)
        status_grid.attach_next_to(self.label_status, self.label_server, Gtk.PositionType.RIGHT, 1, 1)
        # add status grid to window
        content.add(status_grid)

        # check default server
        btn_refresh.emit('clicked')

        # Add main content box to window
        self.add(content)


    def btn_refresh_on_click(self, widget):
        server = self.entry_ip.get_text()
        if server == "":
            server = "159.89.4.84"
            if check_server(server) == 0:
                self.label_status.set_text('Default Connection Checked')
                self.label_server.set_text('Default Server Online')
        else:
            res = check_server(server)
            if res == 0:
                self.label_status.set_text('Connection Checked')
                self.label_server.set_text('Server Online')
            else:
                self.label_status.set_text('Wrong IP or Offline')
                self.label_server.set_text('Server Offline')


    def btn_send_on_click(self, widget):
        host = self.entry_ip.get_text()
        port = self.entry_port.get_text()
        nick = self.entry_nick.get_text()
        password = self.entry_password.get_text()
        description = self.entry_description.get_text()
        nsfw = self.switch_nsfw.get_active()
        meme = self.file

        if host == '':
            host = '159.89.4.84'
        if port == '':
            port = 42069
        if nick == '':
            nick = 'tassilobalbo'
        if password == '':
            password = 'kokos'
        port = int(port)

        # inicializovat main socket
        main_socket = Sock(host, port)
        res = main_socket.open_main(nick)
        token = res[0]
        data_port = res[1]
        # inicializovat data socket
        data_socket = Sock(host, data_port)
        if data_socket.open_data(nick, token) == 0:
            print('data channel initialized')
        else:
            data_socket.send_err('data channel failed to initialize')
            print('data channel failed to initialize')
            return
        data_socket.handle_requests(meme, description, nsfw, password)
        close_data = data_socket.close_data()
        dtoken = close_data[0]
        data_channel_length = close_data[1]
        close_main = main_socket.close_main(dtoken)
        server_msglength = close_main[0]
        main_channel_length = close_main[1]
        total_length = data_channel_length + main_channel_length
        if server_msglength == total_length:
            self.label_status.set_text('Meme sent with data integrity')
            print('Meme sent with data integrity')
        else:
            self.label_status.set_text('Meme sent without data integrity')
            print('Meme sent without data integrity')


    def btn_file_on_click(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a MEME", self, Gtk.FileChooserAction.OPEN,
                                       ("Cancel", Gtk.ResponseType.CANCEL, "Ok", Gtk.ResponseType.OK,))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file = dialog.get_filename()
            print("File selected: " + self.file)
            self.label_status.set_text(self.file)
            self.img.set_from_pixbuf(resize_image(self.file))
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG files")
        filter_png.add_pattern("*.png")

        filter_png = Gtk.FileFilter()
        filter_png.set_name("JPG files")
        filter_png.add_pattern("*.jpg")


if __name__ == '__main__':
    main()
