import wx
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import re


class PrimaryGUI(wx.Frame):

    def __init__(self, parent, title, sid, authtoken, phonenumber, default_recipient_file, config_file):
        super(PrimaryGUI, self).__init__(parent, title=title, size=(650, 400))

        # Initialize dynamic variables
        self.config_file = config_file
        self.recipients_file_location = default_recipient_file
        self.sid_value = sid
        self.auth_token_value = authtoken
        self.phonenumber_value = phonenumber

        # Initialize a dynamic TextCtrl field for the message and recipients file
        self.message_textctrl = wx.TextCtrl()
        self.recipients_tc = wx.TextCtrl()

        # Initialize UI Functions
        self.init_ui()

        # Center the screen
        self.Centre()

        # Set the minimum screen size
        self.SetMinSize(size=(610, 400))

        # Make the screen visible to the user
        self.Show()

    # Initialize the UI
    def init_ui(self):

        # Get system font
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(10)

        # Set up the menubar
        menubar = wx.MenuBar()
        configuration_menu = wx.Menu()
        menubar.Append(configuration_menu, '&Configuration')
        self.SetMenuBar(menubar)

        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        panel.SetBackgroundColour(wx.Colour(red=245, blue=245, green=245))

        # Main vertical sizer box
        vertical_sizer_box = wx.BoxSizer(wx.VERTICAL)

        # Adds Enter Message dialog
        label_hbox = wx.BoxSizer(wx.HORIZONTAL)
        label_stext = wx.StaticText(panel, label='Enter Message:')
        label_stext.SetFont(font)
        label_hbox.Add(label_stext)
        vertical_sizer_box.Add(label_hbox, flag=wx.LEFT | wx.TOP, border=5)

        # Adds text box to enter dialog
        message_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.message_textctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        message_hbox.Add(self.message_textctrl, proportion=1, flag=wx.EXPAND)
        vertical_sizer_box.Add(message_hbox, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND | wx.TOP, border=5)

        # Add gap between box and buttons
        vertical_sizer_box.Add((-1, 10))

        # Add buttons and field for recipients file
        buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        recipients_stext = wx.StaticText(panel, label='Recipients File:')
        recipients_stext.SetFont(font)
        buttons_hbox.Add(recipients_stext, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=5)
        self.recipients_tc = wx.TextCtrl(panel, size=(250, 22))
        buttons_hbox.Add(self.recipients_tc, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=5)
        select_file_button = wx.Button(panel, label='Select File', size=(70, 30))
        buttons_hbox.Add(select_file_button)
        buttons_hbox.Add((0, 10), 1, flag=wx.EXPAND)
        tags_button = wx.Button(panel, label='Tags', size=(50, 30))
        buttons_hbox.Add(tags_button, flag=wx.RIGHT, border=5)
        send_message_button = wx.Button(panel, label='Send Message', size=(100, 30))
        buttons_hbox.Add(send_message_button, flag=wx.LEFT | wx.BOTTOM | wx.ALIGN_RIGHT, border=0)
        vertical_sizer_box.Add(buttons_hbox, flag=wx.RIGHT | wx.EXPAND, border=10)

        # Add gap a bottom of screen
        vertical_sizer_box.Add((-1, 10))

        panel.SetSizer(vertical_sizer_box)

        # Add events to buttons
        self.Bind(wx.EVT_BUTTON, self.on_send_message, id=send_message_button.GetId())
        self.Bind(wx.EVT_BUTTON, self.on_select_file, id=select_file_button.GetId())
        self.Bind(wx.EVT_BUTTON, self.on_tags, id=tags_button.GetId())

        # This event is called any time a menu is about to be opened
        # This should be changed to work only on the configuration menu if more menus are added
        self.Bind(wx.EVT_MENU_OPEN, self.on_configuration)

    def tag_matching(self, msg, recipient):
        rep = {"#Bond": recipient.bond,
               "#FirstName": recipient.first_name,
               "#LastName": recipient.last_name,
               "#PhoneNumber": recipient.phonenumber,
               }
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))
        return pattern.sub(lambda m: rep[re.escape(m.group(0))], msg)

    def load_recipients(self):
        wb = load_workbook(recipients_file_location)
        sheet = wb.worksheets[0]
        recipients_list = []
        for i in range(2, sheet.max_row + 1):
            recipients_list.append(Recipient(bond=sheet.cell(row=i, column=1).value,
                                             first_name=sheet.cell(row=i, column=2).value,
                                             last_name=sheet.cell(row=i, column=3).value,
                                             phonenumber=sheet.cell(row=i, column=4).value,))
        return recipients_list

    # Here we will put the code for when the message is going to be sent
    def on_send_message(self, event):
        recipients_list = load_recipients()
        msg = self.message_textctrl.GetValue()
        for recipient in recipients_list:
            format_msg = tag_matching(msg, recipient)
            twilioCli.messages.create(body=format_msg, from_=recipient.phonenumber, to=phonenumber_value)


    # Using tKinter to allow the user to select a file location
    def on_select_file(self, event):

        # Open up the GUI for selecting a file
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename(title="Choose a File",
                                   initialdir=os.path.dirname(os.path.realpath(__file__)),
                                   filetypes=(("Excel File (*.xlsx)", "*.xlsx"),
                                              ("Legacy Excel File (*.xls)", "*.xls"),
                                              ),
                                   )  # show an "Open" dialog box and return the path to the selected file

        # If  a file was selected, store it and put it on the screen
        if filename is not "":
            self.recipients_file_location = filename
            self.recipients_tc.SetValue(filename)

    # Open a message dialog showing the current tag options
    def on_tags(self, event):
        dial = wx.MessageDialog(None, 'Check Documentation for Information on Tags\n'
                                      '#FirstName\n'
                                      '#LastName\n'
                                      '#Bond\n'
                                      '#PhoneNumber'
                                      , 'Tags', wx.OK | wx.ICON_QUESTION)# This isn't actually a question
                                                                                       # But theres an annoying sound
                                                                                       # otherwise
        dial.ShowModal()

    # Here we will show the configuration menu
    def on_configuration(self, event):
        print("Select your configuration")

class Recipient():
    def __init__(self, bond="", first_name="", last_name="", phonenumber=""):
        self.bond = bond
        self.first_name = first_name
        self.last_name = last_name
        self.phonenumber = phonenumber
