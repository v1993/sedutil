import gtk
import os
import re
import sys
import getopt
import gobject
import subprocess
import time
import datetime
import threading
import pbkdf2
import powerset
import string
import hashlib
import platform
import lockhash
import runop
import random

gobject.threads_init()

def make_hbox(homogeneous, spacing, expand, fill, padding,lab,ent):

    box = gtk.HBox(homogeneous, spacing)

    button = gtk.Button(lab)
    box.pack_start(button, expand, fill, padding)
    button.show()

    txt = gtk.Entry()
    txt.set_text(ent)
    box.pack_start(txt, True, True, padding)
    return box
    
    
class LockApp(gtk.Window):
    ''' An application for pyGTK.  Instantiate
        and call the run method to run. '''
    firstscan = True
    firstmsg = True
    devname="\\\\.\\PhysicalDrive9"
    
    bad_pw = dict({'password': 1,
                   '12345678': 1,
                   '123456789': 1,
                   'football': 1,
                   'baseball': 1,
                   '1234567890': 1,
                   '1qaz2wsx': 1,
                   'princess': 1,
                   'qwertyuiop': 1,
                   'passw0rd': 1,
                   'starwars': 1,
                   '11111111': 1,
                   'sunshine': 1,
                   'zaq1zaq1': 1,
                   'password1': 1})
                   
    eventDescriptions = dict({1 : 'Activate',
                              2 : 'Admin Login',
                              3 : 'User Login',
                              4 : 'RevertSP without erase data',
                              5 : 'RevertSP with erase data',
                              6 : 'Revert using PSID (erase data)',
                              7 : 'GenKey',
                              8 : 'Cryptographic Erase',
                              9 : 'Numerous failed authentication attempts, Datastore cannot be written',
                              10: 'Password changed for SID',
                              11: 'Password changed for Admins',
                              12: 'Password changed for Users',
                              13: 'Attempt to RevertSP',
                              14: 'RevertSP failed',
                              15: 'Attempt to Revert',
                              16: 'Revert failed',
                              17: 'Attempt to revert using PSID',
                              18: 'Revert using PSID failed'})
                   
    image = "LINUXRelease.img"

    LKRNG = "0" 
    LKRNG_SLBA = "0"
    LKRNG_LBALEN = "0"
    LKATTR = "RW"

    VERSION = -1
    
    queryWinText = ""
    
    __gsignals__ = {
        "delete-event" : "override"
    }
     
    try:
        opts, args = getopt.getopt(sys.argv[1:], [""], ["pba", "demo", "standard", "premium"])
    except getopt.GetoptError, err:
        exit(2)

    for o, a in opts:
        if o in ("--demo"):
            VERSION = 0
        elif o in ("--pba"):
            VERSION = 1
        elif o in ("--standard"):
            VERSION = 2
        elif o in ("--premium"):
            VERSION = 3
    
   
    devs_list = [] #[ "/dev/sda" , "/dev/sdb",  "/dev/sdc",  "/dev/sdd",  "/dev/sde" ]
    locked_list = []
    setup_list = []
    unlocked_list = []
    nonsetup_list = []
    tcg_list = []
    msid_list = []
    pba_list = []
    
    vendor_list = [] # "Sandisk" 
    opal_ver_list = [] # 1, 2, or 12
    series_list = [] # series number 
    sn_list = []
    
    salt_list = []
    
    lockstatus_list = []
    setupstatus_list = []
    
    scanning = False
    view_state = 0
    NOT_AUTHORIZED = 256
    AUTHORITY_LOCKED_OUT = 4608
    
    def __init__(self):
        runop.findos(self)
        
        version_text = os.popen(self.prefix + 'sedutil-cli --version').read()
        regex_license = 'Valid Fidelity Lock License found 0:([124]);'
        f = re.search(regex_license, version_text)
        if f or self.VERSION != -1:
            if self.VERSION == -1:
                v = f.group(1)
                if v == '1':
                    self.VERSION = 0
                elif v == '2':
                    self.VERSION = 2
                elif v == '4':
                    self.VERSION = 3

    
            res = lockhash.testPBKDF2()
            status = res[0]
            hash_v = os.popen(self.prefix + 'sedutil-cli --validatePBKDF2').read()
            valid_pass = 'passed'
            f = re.search(res[1], hash_v)
            
            if status != 0 or not f:
                self.msg_err("Hash validation failed")
                self.exitapp()
            
            
        
            gtk.Window.__init__(self)
            if self.VERSION == 0:
                self.set_title('Fidelity Lock Disk Drive Security Manager - Demo version')
            elif self.VERSION == 1:
                self.set_title('Fidelity Lock Disk Drive Security Manager - PBA version')
            elif self.VERSION == 2:
                self.set_title('Fidelity Lock Disk Drive Security Manager - Standard version')
            else:
                self.set_title('Fidelity Lock Disk Drive Security Manager - Premium version')
                
            
                
            if os.path.isfile('icon.jpg'):
                self.set_icon_from_file('icon.jpg')

            height = 550
            width = 600
            if platform.system() == 'Linux':
                width = 650
                
            self.set_size_request(width, height)

            self.connect('destroy', gtk.main_quit)
            
            self.connect('delete_event', self.destroy_main)
            
            homogeneous = False
            spacing = 0
            expand = False
            fill = False
            padding = 0
            
            self.vbox0 = gtk.VBox(False,0)
            self.hbox0 = gtk.HBox(False,0)
            self.hbox = gtk.HBox(False,0)
            self.vbox = gtk.VBox(False,5)
            
            self.menuBar = gtk.MenuBar()
            
            self.navMenu = gtk.Menu()
            self.navM = gtk.MenuItem("Main")
            self.navM.set_submenu(self.navMenu)
            self.backToMain = gtk.MenuItem("Home")
            self.backToMain.connect("activate", self.returnToMain)
            self.backToMain.set_tooltip_text('Return to Home View')
            self.navMenu.append(self.backToMain)
            self.exitApp = gtk.MenuItem("Exit")
            self.exitApp.connect("activate", self.exitapp)
            self.exitApp.set_tooltip_text('Exit the app')
            self.navMenu.append(self.exitApp)
            self.exitReboot = gtk.MenuItem("Reboot")
            self.exitReboot.connect("activate", self.reboot)
            self.exitReboot.set_tooltip_text('Reboots the computer')
            self.navMenu.append(self.exitReboot)
            self.exitShutDown = gtk.MenuItem("Shut Down")
            self.exitShutDown.connect("activate", self.shutdown)
            self.exitShutDown.set_tooltip_text('Shuts down the computer')
            self.navMenu.append(self.exitShutDown)
            
            
            self.menuBar.append(self.navM)
            
            self.devMenu = gtk.Menu()
            self.devM = gtk.MenuItem("Device")
            self.devM.set_submenu(self.devMenu)
            self.devQuery = gtk.MenuItem("Query drive")
            self.devQuery.connect("activate", self.query)
            self.devQuery.set_tooltip_text('Query the currently selected drive')
            self.devMenu.append(self.devQuery)
            if self.VERSION != 1:
                self.readLog = gtk.MenuItem("View Audit Log")
                self.readLog.connect("activate", self.openLog_prompt)
                self.readLog.set_tooltip_text('Access a drive\'s event log')
                self.devMenu.append(self.readLog)
            self.devScan = gtk.MenuItem("Rescan drives")
            self.devScan.connect("activate", self.run_scan)
            self.devScan.set_tooltip_text('Update the list of detected drives')
            self.devMenu.append(self.devScan)
            
            self.menuBar.append(self.devM)
            
            self.setupMenu = gtk.Menu()
            self.setupM = gtk.MenuItem("Setup")
            self.setupM.set_submenu(self.setupMenu)
            if self.VERSION != 1:
                self.setupFull = gtk.MenuItem("Full Setup")
                self.setupFull.connect("activate", self.setup_prompt1)
                self.setupFull.set_tooltip_text('Set up password and preboot image for a drive')
                self.setupMenu.append(self.setupFull)
                #self.setupPW = gtk.MenuItem("Password only")
                #self.setupPW.connect("activate", self.setupPW_prompt)
                #self.setupPW.set_tooltip_text('Set up password for a drive')
                #self.setupMenu.append(self.setupPW)
                self.updatePBA = gtk.MenuItem("Update Preboot Image")
                self.updatePBA.connect("activate", self.updatePBA_prompt)
                self.updatePBA.set_tooltip_text('Update a drive\'s preboot image')
                self.setupMenu.append(self.updatePBA)
            
            self.changePassword = gtk.MenuItem("Change Password")
            self.changePassword.connect("activate", self.changePW_prompt)
            self.changePassword.set_tooltip_text('Change a drive\'s password')
            self.setupMenu.append(self.changePassword)
            if self.VERSION % 3 == 0:
                self.setupUSB = gtk.MenuItem("Setup USB")
                self.setupUSB.connect("activate", self.setupUSB_prompt)
                self.setupUSB.set_tooltip_text('Set up bootable USB')
                self.setupMenu.append(self.setupUSB)
                
                self.setupUser = gtk.MenuItem("Setup User")
                self.setupUser.connect("activate", self.setupUser_prompt)
                self.setupUser.set_tooltip_text('Set up a user password')
                self.setupMenu.append(self.setupUser)
            
            self.menuBar.append(self.setupM)
            
            
            self.unlockMenu = gtk.Menu()
            self.unlockM = gtk.MenuItem("Unlock")
            self.unlockM.set_submenu(self.unlockMenu)
            self.unlock1 = gtk.MenuItem("Preboot Unlock")
            self.unlock1.connect("activate", self.unlock_prompt)
            self.unlock1.set_tooltip_text('Unlock a drive to boot into')
            self.unlockMenu.append(self.unlock1)
            #if self.VERSION != 1:
            #    self.disableLock = gtk.MenuItem("Disable Lock")
            #    self.disableLock.connect("activate", self.disableLock_prompt)
            #    self.disableLock.set_tooltip_text('Disables locking on a drive')
            #    self.unlockMenu.append(self.disableLock)
            if self.VERSION != 2:
                self.unlockMulti = gtk.MenuItem("Unlock with USB")
                self.unlockMulti.connect("activate", self.unlockUSB_prompt)
                self.unlockMulti.set_tooltip_text('Unlock one or more drives using USB password files')
                self.unlockMenu.append(self.unlockMulti)
        
            self.menuBar.append(self.unlockM)
            if self.VERSION != 1:
                self.lockMenu = gtk.Menu()
                self.lockM = gtk.MenuItem("Lock")
                self.lockM.set_submenu(self.lockMenu)
                #self.lockMI = gtk.MenuItem("Enable Lock")
                #self.lockMI.connect("activate", self.lockEnable_prompt)
                #self.lockMI.set_tooltip_text('Enable locking on a drive')
                #self.lockMenu.append(self.lockMI)
                self.lockD = gtk.MenuItem("Lock Drive")
                self.lockD.connect("activate", self.lock_prompt)
                self.lockD.set_tooltip_text('Lock a drive')
                self.lockMenu.append(self.lockD)
                
                self.menuBar.append(self.lockM)
            
            self.revertMenu = gtk.Menu()
            self.revertM = gtk.MenuItem("Revert")
            self.revertM.set_submenu(self.revertMenu)
            self.revertO = gtk.MenuItem("and Keep Data")
            self.revertO.connect("activate", self.revert_keep_prompt)
            self.revertO.set_tooltip_text('Use password to revert the drive\'s LockingSP while keeping its data')
            self.revertMenu.append(self.revertO)
            self.revertPW = gtk.MenuItem("and Erase")
            self.revertPW.connect("activate", self.revert_erase_prompt)
            self.revertPW.set_tooltip_text('Use password to revert the drive\'s LockingSP and erase data')
            self.revertMenu.append(self.revertPW)
            self.revertPSID = gtk.MenuItem("with PSID")
            self.revertPSID.connect("activate", self.revert_psid_prompt)
            self.revertPSID.set_tooltip_text('Use drive\'s PSID to revert drive to manufacturer settings')
            self.revertMenu.append(self.revertPSID)
            
            self.menuBar.append(self.revertM)
            
            self.helpMenu = gtk.Menu()
            self.helpM = gtk.MenuItem("Help")
            self.helpM.set_submenu(self.helpMenu)
            self.help1 = gtk.MenuItem("Help")
            self.help1.set_tooltip_text('Access online help')
            self.helpMenu.append(self.help1)
            self.updateM = gtk.MenuItem("Check for updates")
            self.updateM.set_tooltip_text('Check for an updated version of this app')
            self.helpMenu.append(self.updateM)
            self.aboutM = gtk.MenuItem("About")
            self.aboutM.connect("activate", self.show_about)
            self.aboutM.set_tooltip_text('About Fidelity Lock')
            self.helpMenu.append(self.aboutM)
            
            self.menuBar.append(self.helpM)
            
            if self.VERSION % 2 != 1:
                self.upgradeMenu = gtk.Menu()
                self.upgradeM = gtk.MenuItem("License")
                self.upgradeM.set_submenu(self.upgradeMenu)
                if self.VERSION == 0:
                    self.upgradeBasic = gtk.MenuItem("Buy Standard")
                    self.upgradeMenu.append(self.upgradeBasic)
                self.upgradePro = gtk.MenuItem("Buy Premium")
                self.upgradeMenu.append(self.upgradePro)
                self.menuBar.append(self.upgradeM)
            
            self.hbox0.pack_start(self.menuBar, True, True, 0)
            self.vbox0.pack_start(self.hbox0, False, False, 0)
            
            self.buttonBox = gtk.HBox(homogeneous, 0)
            
            self.go_button_cancel = gtk.Button('_Cancel')
            
            self.viewLog = gtk.Button('_View Audit Log')
            self.viewLog.set_flags(gtk.CAN_DEFAULT)
            
            self.setup_next = gtk.Button('_Activate and Continue')
            self.setupLockOnly = gtk.Button('_Skip writing Preboot Image')
            self.setupLockPBA = gtk.Button('_Write Preboot Image')
            
            self.setupPWOnly = gtk.Button('_Set Up password')
            self.setupUserPW = gtk.Button('_Set Up User Password')
            
            self.updatePBA_button = gtk.Button('_Update')
            self.updatePBA_button.set_flags(gtk.CAN_DEFAULT)
            
            self.go_button_changePW_confirm = gtk.Button('_Change Password')
            
            self.setupUSB_button = gtk.Button('_Create bootable USB')
            
            self.pbaUnlockReboot = gtk.Button("_Unlock and Reboot")
            self.pbaUnlockReboot.set_flags(gtk.CAN_DEFAULT)
            self.pbaUnlockOnly = gtk.Button("_Unlock only")
            self.pbaUSB_button = gtk.Button('_Unlock with USB')
            
            self.revertOnly_button = gtk.Button('_Revert Drive')
            self.revertOnly_button.set_flags(gtk.CAN_DEFAULT)
            #self.disableLock_button = gtk.Button('_Disable Lock')
            #self.disableLock_button.set_flags(gtk.CAN_DEFAULT)
            
            self.go_button_revert_user_confirm = gtk.Button('_Revert and Erase')
            self.go_button_revert_user_confirm.set_flags(gtk.CAN_DEFAULT)
            self.go_button_revert_psid_confirm = gtk.Button('_Revert with PSID')
            
            #self.lockEnable_button = gtk.Button('_Enable Lock')
            #self.lockEnable_button.set_flags(gtk.CAN_DEFAULT)
            self.lock_button = gtk.Button('_Lock Drive')
            self.lock_button.set_flags(gtk.CAN_DEFAULT)
            
            self.op_label = gtk.Label('Main')
            self.op_label.set_alignment(0,0.5)
            self.vbox.pack_start(self.op_label, False, False, 0)
            
            self.noTCG_instr = gtk.Label('No TCG drives were detected, please insert a TCG drive and use \'Rescan devices\' to continue.')
            self.noTCG_instr.set_alignment(0,0.5)
            self.vbox.pack_start(self.noTCG_instr, False, False, 0)
            
            self.select_instr = gtk.Label('Select a drive from the dropdown menu.')
            self.select_instr.set_alignment(0,0.5)
            self.vbox.pack_start(self.select_instr, False, False, 0)
            
            self.main_instr = gtk.Label('Select an operation from the menu bar above.  Below are all detected drives.')
            self.main_instr.set_alignment(0,0.5)
            self.vbox.pack_start(self.main_instr, False, False, 0)
            
            self.naDevices_instr = gtk.Label('\nNo drives available for this operation.')
            self.naDevices_instr.set_alignment(0,0.5)
            self.vbox.pack_start(self.naDevices_instr, False, False, 0)
            
            self.op_instr = gtk.Label('\n')
            self.op_instr.set_alignment(0,0.5)
            
            self.go_button_cancel.connect('clicked', self.returnToMain)
            self.go_button_revert_user_confirm.connect('clicked', runop.run_revertErase, self)
            self.go_button_revert_psid_confirm.connect('clicked', runop.run_revertPSID, self)
            self.go_button_changePW_confirm.connect('clicked', runop.run_changePW, self)
            self.setup_next.connect('clicked', runop.run_setupFull, self, 0)
            self.updatePBA_button.connect('clicked', runop.run_pbaWrite, self, 0)
            
            self.setupLockOnly.connect('clicked', self.setup_finish)
            self.setupLockPBA.connect('clicked', runop.run_pbaWrite, self, 1)
            
            self.setupUSB_button.connect('clicked', runop.run_setupUSB, self)
            
            self.setupPWOnly.connect('clicked', runop.run_setupFull, self, 1)
            self.setupUserPW.connect('clicked', runop.run_setupUser, self)
            
            self.pbaUnlockReboot.connect("clicked", runop.run_unlockPBA, self, True)
            self.pbaUnlockOnly.connect("clicked", runop.run_unlockPBA, self, False)
            self.pbaUSB_button.connect("clicked", runop.run_unlockUSB, self, 0, None)
            
            #self.lockEnable_button.connect('clicked', runop.run_lockEnable, self)
            self.lock_button.connect('clicked', runop.run_lockDrive, self)
            
            self.revertOnly_button.connect('clicked', runop.run_revertKeep, self)
            #self.disableLock_button.connect('clicked', runop.run_disableLock, self)
            
            self.viewLog.connect('clicked', runop.openLog, self)

            self.scan_passwordonly()
            
            self.wait_instr = gtk.Label('This may take a few seconds...')
            self.pba_wait_instr = gtk.Label('Please wait, writing the preboot image will take a few minutes...')
            self.vbox.pack_start(self.wait_instr, False, False, 5)
            self.vbox.pack_start(self.pba_wait_instr, False, False, 5)
            
            self.waitSpin = gtk.Spinner()
            self.vbox.pack_start(self.waitSpin, False, False, 5)
            
            self.vbox.pack_start(self.op_instr, True, False, 5)
            
            self.box_psid = gtk.HBox(homogeneous, 0)
            
            self.revert_psid_label = gtk.Label("Enter PSID")
            self.revert_psid_label.set_width_chars(22)
            self.revert_psid_label.set_alignment(0,0.5)
            self.box_psid.pack_start(self.revert_psid_label, expand, fill, padding)
            
            self.revert_psid_entry = gtk.Entry()
            self.revert_psid_entry.set_text("")
            self.box_psid.pack_start(self.revert_psid_entry, True, True, padding)
            
            self.box_newpass_confirm = gtk.HBox(homogeneous, 0)
            
            self.confirm_pass_label = gtk.Label("Confirm New Password")
            self.confirm_pass_label.set_width_chars(22)
            self.confirm_pass_label.set_alignment(0,0.5)
            self.box_newpass_confirm.pack_start(self.confirm_pass_label, expand, fill, padding)
            self.confirm_pass_entry = gtk.Entry()
            self.confirm_pass_entry.set_text("")
            self.confirm_pass_entry.set_width_chars(27)
            self.confirm_pass_entry.set_visibility(False)
            self.box_newpass_confirm.pack_start(self.confirm_pass_entry, False, False, padding)
            
            if (gtk.gtk_version[1] > 24 or
                (gtk.gtk_version[1] == 24 and gtk.gtk_version[2] > 28)):
                self.drive_menu = gtk.ComboBoxEntry()
                self.auth_menu = gtk.ComboBoxEntry()
                self.authQuery = gtk.ComboBoxEntry()
                self.usb_menu = gtk.ComboBoxEntry()
            else:
                self.drive_menu = gtk.combo_box_entry_new_text()
                self.auth_menu = gtk.combo_box_entry_new_text()
                self.authQuery = gtk.combo_box_entry_new_text()
                self.usb_menu = gtk.combo_box_entry_new_text()
                
                self.drive_menu.append = self.drive_menu.append_text
                self.auth_menu.append = self.auth_menu.append_text
                self.authQuery.append = self.authQuery.append_text
                self.usb_menu.append = self.usb_menu.append_text
            
            self.box_drive = gtk.HBox(homogeneous, 0)
            
            self.drive_label = gtk.Label("Drive")
            self.drive_label.set_width_chars(22)
            self.drive_label.set_alignment(0,0.5)
            self.box_drive.pack_start(self.drive_label, expand, fill, padding)
            self.box_drive.pack_start(self.drive_menu, False, False, padding)
            self.drive_list = []
            
            self.box_pbausb = gtk.HBox(homogeneous, 0)
            
            self.usb_label = gtk.Label("USB")
            self.usb_label.set_width_chars(22)
            self.usb_label.set_alignment(0,0.5)
            self.box_pbausb.pack_start(self.usb_label, expand, fill, padding)
            self.box_pbausb.pack_start(self.usb_menu, False, False, padding)
            self.usb_list = []
            
            self.box_auth = gtk.HBox(homogeneous, 0)
            
            self.auth_label = gtk.Label("Auth Level")
            self.auth_label.set_width_chars(22)
            self.auth_label.set_alignment(0,0.5)
            self.box_auth.pack_start(self.auth_label, expand, fill, padding)
            self.auth_menu.append('Admin')
            self.auth_menu.append('User')
            self.authQuery.append('Admin')
            self.authQuery.append('User')
            self.auth_menu.set_active(0)
            self.authQuery.set_active(0)
            self.box_auth.pack_start(self.auth_menu, False, False, padding)
            
            self.checkbox_box = gtk.HBox(homogeneous, 0)
            
            self.check_box_pass = gtk.CheckButton("Show Password")
            self.check_box_pass.connect("toggled", self.entry_check_box_pass, self.check_box_pass)
            self.check_box_pass.set_active(False)
            self.check_box_pass.show()
            self.checkbox_box.pack_start(self.check_box_pass, expand, fill, padding)
            
            check_align = gtk.Alignment(1,0,0,0)
            check_align.add(self.checkbox_box)
            
            self.buttonBox.pack_start(self.setup_next, False, False, padding)
            self.buttonBox.pack_start(self.setupLockOnly, False, False, padding)
            self.buttonBox.pack_start(self.setupLockPBA, False, False, padding)
            self.buttonBox.pack_start(self.go_button_changePW_confirm, False, False, padding)
            self.buttonBox.pack_start(self.go_button_revert_user_confirm, False, False, padding)
            self.buttonBox.pack_start(self.go_button_revert_psid_confirm, False, False, padding)
            self.buttonBox.pack_start(self.pbaUnlockReboot, False, False, padding)
            self.buttonBox.pack_start(self.pbaUnlockOnly, False, False, padding)
            self.buttonBox.pack_start(self.setupPWOnly, False, False, padding)
            self.buttonBox.pack_start(self.updatePBA_button, False, False, padding)
            self.buttonBox.pack_start(self.pbaUSB_button, False, False, padding)
            #self.buttonBox.pack_start(self.lockEnable_button, False, False, padding)
            self.buttonBox.pack_start(self.lock_button, False, False, padding)
            self.buttonBox.pack_start(self.revertOnly_button, False, False, padding)
            #self.buttonBox.pack_start(self.disableLock_button, False, False, padding)
            self.buttonBox.pack_start(self.viewLog, False, False, padding)
            self.buttonBox.pack_start(self.setupUSB_button, False, False, padding)
            self.buttonBox.pack_start(self.setupUserPW, False, False, padding)
            
            self.buttonBox.pack_start(self.go_button_cancel, False, False, padding)
            
            self.vbox.pack_start(self.box_auth, False)
            
            self.pass_dialog()
            self.new_pass_dialog()
            
            self.vbox.pack_start(self.box_newpass_confirm, False)
            self.vbox.pack_start(self.box_psid, False)
            self.vbox.pack_start(self.box_drive, False)
            self.vbox.pack_start(self.box_pbausb, False)
            
            self.vbox.pack_start(check_align, False, False, padding)
            
            valign = gtk.Alignment(0,1,0,0)
            self.vbox.pack_start(valign)
            halign = gtk.Alignment(1,0,0,0)
            halign.add(self.buttonBox)
            self.vbox.pack_end(halign, False, False, padding)
            
            self.hbox.set_border_width(20)
            
            self.hbox.pack_start(self.vbox, True, True, padding)
            self.vbox0.pack_start(self.hbox, True, True, padding)
            
            self.add(self.vbox0)
            self.show_all()
            
            self.hideAll()
            self.select_box.show()
            self.main_instr.show()
            self.op_label.show()
                    
            self.run_scan()
            
            print self.devs_list
            print self.sn_list
            print self.salt_list
            print self.locked_list
            print self.setup_list
            print self.unlocked_list
            print self.nonsetup_list
            print self.tcg_list
            
            if len(self.devs_list) == 0:
                self.msg_err('No drives detected, try running this application with Administrator.')
                self.exitapp()
            pwd_test = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
            salt_test = self.salt_list[0]
            dev_test = self.devs_list[0]
            sedutil_txt = os.popen(self.prefix + 'sedutil-cli --hashvalidation ' + pwd_test + ' ' + dev_test).read()
            sedutil_regex = 'hashed password\s*:\s*([A-F0-9]{64})'
            sedutil_match = re.search(sedutil_regex, sedutil_txt)
            sedutil_res = sedutil_match.group(1).lower()
            hash_res = lockhash.hash_pbkdf2(pwd_test, salt_test)
            if sedutil_res != hash_res:
                self.msg_err('Hash validation failed')
            
            dev_os = platform.system()
            
            if self.VERSION == 1 and dev_os == 'Linux':
                bus_file = '/tmp/h.d/hash-sdb-bus.txt'
                ser_file = '/tmp/h.d/hash-sdb-ser.txt'
                if os.path.isfile(bus_file) and os.path.isfile(ser_file): #if USB boot
                    b = open(bus_file)
                    s = open(ser_file)
                    b_info = b.read().lower()
                    s_info = s.read().lower()
                    b.close()
                    s.close()
                    reg_z = '0{64}'
                    m1 = re.match(reg_z, b_info)
                    m2 = re.match(reg_z, s_info)
                    if len(b_info) == 64 and len(s_info) == 64 and not (m1 and m2):
                        present = False
                        bus = 'FidelityLockUSB'
                        for i in range(len(self.devs_list)):
                            salt = self.salt_list[i]
                            b_curr = lockhash.hash_pbkdf2(bus, salt)
                            s_curr = lockhash.hash_pbkdf2(salt, salt)
                            if b_curr == b_info and s_curr == s_info:
                                present = True
                        if not present:
                            self.msg_err('Invalid bootable USB')
                            self.exitapp()
                folder_list = []
                txt = os.popen(self.prefix + 'mount').read()
                dev_regex = '/dev/sd[b-z][1-9]?\s*on\s*(\S+)\s*type'
                drive_list = re.findall(dev_regex, txt)
                txt2 = os.popen(self.prefix + 'blkid').read()
                dev_regex2 = '(/dev/sd[b-z][1-9]?.+)'
                all_list = re.findall(dev_regex2, txt2)
                r1 = '/dev/sd[b-z][1-9]?'
                r2 = 'TYPE="([a-z]+)"'
                for a in all_list:
                    m1 = re.search(r1,a)
                    m2 = re.search(r2,a)
                    dev_a = m1.group(0)
                    type_a = m2.group(1)
                    if dev_a not in drive_list:
                        s = os.system(self.prefix + 'mount -t ' + type_a + ' ' + dev_a)
                txt = os.popen(self.prefix + 'mount').read()
                dev_regex = '/dev/sd[b-z][1-9]?\s*on\s*(\S+)\s*type'
                drive_list = re.findall(dev_regex, txt)
                for d in drive_list:
                    if os.path.isdir('%s/FidelityLock' % d):
                        folder_list.append(d)
                if folder_list != []:
                    message = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_CANCEL)
                    msg = 'USB detected, Proceeding to unlock with USB in 5 seconds.'
                    message.set_markup(msg)
                    self.timer = gobject.timeout_add(5000, runop.run_unlockUSB, None, self, 1, message)
                    res = message.run()
                    cancel = False
                    if res == gtk.RESPONSE_CANCEL :
                        cancel = True
                    message.destroy()
                    gobject.source_remove(self.timer)
                    self.timer = 0
                    if not cancel:
                        runop.run_unlockUSB(None, self, 1, None)
            
            #if self.VERSION == 0:
            #    self.updateM.set_sensitive(False)
            #    self.readLog.set_sensitive(False)
            #    self.setupFull.set_sensitive(False)
            #    #self.setupPW.set_sensitive(False)
            #    self.updatePBA.set_sensitive(False)
            #    self.changePassword.set_sensitive(False)
            #    self.revertPW.set_sensitive(False)
            #    self.revertPSID.set_sensitive(False)
            #    self.unlock1.set_sensitive(False)
            #    #self.lockMI.set_sensitive(False)
            #    self.lockD.set_sensitive(False)
            #    #self.disableLock.set_sensitive(False)
            #    self.unlockMulti.set_sensitive(False)
            #    self.setupUSB.set_sensitive(False)
            #    self.setupUser.set_sensitive(False)
            if self.VERSION == 0:
                self.setup_next.set_sensitive(False)
                self.setupLockOnly.set_sensitive(False)
                self.setupLockPBA.set_sensitive(False)
                self.go_button_changePW_confirm.set_sensitive(False)
                self.go_button_revert_user_confirm.set_sensitive(False)
                self.go_button_revert_psid_confirm.set_sensitive(False)
                self.pbaUnlockReboot.set_sensitive(False)
                self.pbaUnlockOnly.set_sensitive(False)
                self.setupPWOnly.set_sensitive(False)
                self.updatePBA_button.set_sensitive(False)
                self.pbaUSB_button.set_sensitive(False)
                self.lock_button.set_sensitive(False)
                self.revertOnly_button.set_sensitive(False)
                self.viewLog.set_sensitive(False)
                self.setupUSB_button.set_sensitive(False)
                self.setupUserPW.set_sensitive(False)
            if self.VERSION == 1:
                self.unlock_prompt()
                
            self.queryWin = gtk.Window()
            self.queryWin.set_border_width(10)
            self.queryWin.set_title("Query Device")
            
            scrolledWin = gtk.ScrolledWindow()
            scrolledWin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            
            self.queryWin.set_default_size(400, 500)
            if os.path.isfile('icon.jpg'):
                self.queryWin.set_icon_from_file('icon.jpg')
            
            queryVbox = gtk.VBox()
            self.queryWin.add(queryVbox)
            
            queryTextView = gtk.TextView()
            queryTextView.set_editable(False)
            self.queryTextBuffer = queryTextView.get_buffer()
            self.queryTextBuffer.set_text('')
            scrolledWin.add_with_viewport(queryTextView)
            queryVbox.pack_start(scrolledWin, True, True, 0)
            
            self.query_instr = gtk.Label('Enter the device\'s password to access more query information.')
            queryVbox.pack_start(self.query_instr, False, False, 0)
            
            if self.VERSION % 3 == 0:
                self.authBoxQ = gtk.HBox(False, 0)
                authLabel = gtk.Label('Auth Level')
                self.authBoxQ.pack_start(authLabel, True, True, 0)
                self.authBoxQ.pack_start(self.authQuery, True, True,0)
                queryVbox.pack_start(self.authBoxQ, False, False, 0)
            
            self.passBoxQ = gtk.HBox(False, 0)
            plTxt = ''
            if self.VERSION == 1:
                plTxt = 'Enter Admin Password'
            else:
                plTxt = 'Enter Password'
            passLabel = gtk.Label(plTxt)
            self.queryPass = gtk.Entry()
            self.queryPass.set_visibility(False)
            
            submitPass = gtk.Button('Submit')
            submitPass.connect("clicked", self.queryAuth)
            if self.VERSION == 0:
                submitPass.set_sensitive(False)
            self.passBoxQ.pack_start(passLabel, True, True, 0)
            self.passBoxQ.pack_start(self.queryPass, True, True, 0)
            self.passBoxQ.pack_start(submitPass, False, False, 0)
            queryVbox.pack_start(self.passBoxQ, False, False, 0)
            if self.VERSION != 1:
                save_instr = gtk.Label('Press \'Save to text file\' to save the query information in a file.')
                queryVbox.pack_start(save_instr, False, False, 0)
                
                querySave = gtk.Button('_Save to text file')
                querySave.connect("clicked", self.saveToText)
                if self.VERSION == 0:
                    querySave.set_sensitive(False)
                queryVbox.pack_start(querySave, False, False, 0)
            
            self.queryWin.connect('delete_event', self.hide_queryWin)
            
            self.queryWin.hide()
            
            #self.msg_ok("Hash validation passed")
            
            if dev_os == 'Windows':
                verified = powerset.verify_power()
                if 0 in self.setup_list and not verified:
                    message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_YES_NO)
                    message.set_markup("Your system does not have the recommended power settings, would you like to change the settings?")
                    res = message.run()
                    if res == gtk.RESPONSE_YES:
                        message.destroy()
                        powerset.set_power()
                        self.msg_ok("Your power settings have been changed successfully.")
                    elif res == gtk.RESPONSE_NO:
                        message.destroy()
                        
            
        else:
            self.msg_err('No valid license of Fidelity Lock found, please register to get demo license or buy basic/premium license')
            self.exitapp()
           
    def scan_passwordonly(self, *args):
        homogeneous = False
        spacing = 0
        expand = False
        fill = False
        padding = 0
        width = 12
        
        self.box_dev = gtk.HBox(homogeneous, spacing)
        
        self.dev_info = gtk.VBox(homogeneous, 5)
        self.opal_info = gtk.VBox(homogeneous, 5)
        
        self.select_box = gtk.HBox(homogeneous, spacing)
        
        self.vendor_box = gtk.HBox(homogeneous, spacing)
        self.sn_box = gtk.HBox(homogeneous, spacing)
        self.msid_box = gtk.HBox(homogeneous, spacing)
        self.series_box = gtk.HBox(homogeneous, spacing)
        
        self.ssc_box = gtk.HBox(homogeneous, spacing)
        self.status_box = gtk.HBox(homogeneous, spacing)
        self.setup_box = gtk.HBox(homogeneous, spacing)
        self.blockSID_box = gtk.HBox(homogeneous, spacing)
        
        self.label_dev = gtk.Label("Devices")
        self.label_dev.set_alignment(0, 0.5)
        self.label_dev.set_width_chars(14)
        self.select_box.pack_start(self.label_dev, expand, fill, padding)
        self.label_dev.show()
        
        self.label_dev2 = gtk.Label("Device") 
        self.label_dev2.set_alignment(0, 0.5)
        self.label_dev2.set_width_chars(14)
        self.select_box.pack_start(self.label_dev2, expand, fill, padding)
        self.label_dev2.show()

        if (gtk.gtk_version[1] > 24 or
            (gtk.gtk_version[1] == 24 and gtk.gtk_version[2] > 28)):
            self.dev_select = gtk.ComboBoxEntry()
        else:
            self.dev_select = gtk.combo_box_entry_new_text()
            
            self.dev_select.append = self.dev_select.append_text
            
            
        self.select_box.pack_start(self.dev_select, True, True, padding)
        
        self.dev_select.child.connect('changed', self.changed_cb)
        
        self.dev_single = gtk.Entry()
        self.dev_single.set_width_chars(35)
        self.dev_single.set_sensitive(False)

        self.select_box.pack_start(self.dev_single, True, True, padding)
        
        self.vbox.pack_start(self.select_box, False, True, padding)
        
        self.dev_label = gtk.Label(" Device information")
        self.dev_label.show()
        self.dev_info.pack_start(self.dev_label, False, False, padding)
        
        self.vendor_label = gtk.Label("Model Number")
        self.vendor_label.set_alignment(0, 0.5)
        self.vendor_label.set_width_chars(14)
        self.vendor_label.show()
        self.vendor_box.pack_start(self.vendor_label, False, False, padding)
        
        self.dev_vendor = gtk.Entry()
        self.dev_vendor.set_text("")
        self.dev_vendor.set_property("editable", False)
        self.dev_vendor.set_sensitive(False)
        self.dev_vendor.show()
        self.dev_vendor.set_width_chars(38)
        self.vendor_box.pack_start(self.dev_vendor, False, False, padding)
        
        self.dev_info.pack_start(self.vendor_box, True, True, padding)
        
        self.sn_label = gtk.Label("Serial Number")
        self.sn_label.set_alignment(0, 0.5)
        self.sn_label.set_width_chars(14)
        self.sn_label.show()
        self.sn_box.pack_start(self.sn_label, False, False, padding)
        
        self.dev_sn = gtk.Entry()
        self.dev_sn.set_text("")
        self.dev_sn.set_property("editable", False)
        self.dev_sn.set_sensitive(False)
        self.dev_sn.show()
        self.dev_sn.set_width_chars(38)
        self.sn_box.pack_start(self.dev_sn, False, False, padding)
        
        self.dev_info.pack_start(self.sn_box, True, True, padding)
        
        self.msid_label = gtk.Label("MSID")
        self.msid_label.set_alignment(0,0.5)
        self.msid_label.set_width_chars(14)
        self.msid_label.show()
        self.msid_box.pack_start(self.msid_label, False, False, padding)
        
        self.dev_msid = gtk.Entry()
        self.dev_msid.set_text("")
        self.dev_msid.set_property("editable", False)
        self.dev_msid.set_sensitive(False)
        self.dev_msid.show()
        self.dev_msid.set_width_chars(38)
        self.msid_box.pack_start(self.dev_msid, False, False, padding)
        
        self.dev_info.pack_start(self.msid_box, True, True, padding)
        
        self.series_label = gtk.Label("Firmware")
        self.series_label.set_alignment(0,0.5)
        self.series_label.set_width_chars(14)
        self.series_label.show()
        self.series_box.pack_start(self.series_label, False, False, padding)
        
        self.dev_series = gtk.Entry()
        self.dev_series.set_text("")
        self.dev_series.set_property("editable", False)
        self.dev_series.set_sensitive(False)
        self.dev_series.show()
        self.dev_series.set_width_chars(38)
        self.series_box.pack_start(self.dev_series, False, False, padding)
        
        self.dev_info.pack_start(self.series_box, True, True, padding)
        
        #opal_info
        
        self.opal_label = gtk.Label(" TCG information")
        self.opal_label.show()
        self.opal_info.pack_start(self.opal_label, False, False, padding)
        
        self.label_opal_ver = gtk.Label('TCG Version')
        self.label_opal_ver.set_width_chars(12)
        
        self.label_opal_ver.show()
        self.ssc_box.pack_start(self.label_opal_ver, False, False, padding)
        
        self.dev_opal_ver = gtk.Entry()
        self.dev_opal_ver.set_text("")
        self.dev_opal_ver.set_width_chars(18)
        self.dev_opal_ver.set_property("editable", False)
        self.dev_opal_ver.set_sensitive(False)
        self.dev_opal_ver.show()
        self.ssc_box.pack_start(self.dev_opal_ver, False, False, padding)
        
        self.opal_info.pack_start(self.ssc_box, False, True, padding)
        
        self.status_label = gtk.Label(" Lock Status ")
        self.status_label.set_width_chars(12)
        self.status_label.show()
        self.status_box.pack_start(self.status_label, False, False, padding)
        
        self.dev_status = gtk.Entry()
        self.dev_status.set_text("")
        self.dev_status.set_property("editable", False)
        self.dev_status.set_sensitive(False)
        self.dev_status.set_width_chars(18)
        self.dev_status.show()
        self.status_box.pack_start(self.dev_status, False, False, padding)
        
        self.opal_info.pack_start(self.status_box, False, False, padding)
        
        self.setup_label = gtk.Label(" Setup Status ")
        self.setup_label.set_width_chars(12)
        self.setup_label.show()
        self.setup_box.pack_start(self.setup_label, False, False, padding)
        
        self.dev_setup = gtk.Entry()
        self.dev_setup.set_text("")
        self.dev_setup.set_property("editable", False)
        self.dev_setup.set_sensitive(False)
        self.dev_setup.set_width_chars(18)
        self.dev_setup.show()
        self.setup_box.pack_start(self.dev_setup, False, False, padding)
        
        self.opal_info.pack_start(self.setup_box, False, False, padding)
        
        self.blockSID_label = gtk.Label(" Block SID ")
        self.blockSID_label.set_width_chars(12)
        self.blockSID_label.show()
        self.blockSID_box.pack_start(self.blockSID_label, False, False, padding)
        
        self.dev_blockSID = gtk.Entry()
        self.dev_blockSID.set_property("editable", False)
        self.dev_blockSID.set_sensitive(False)
        self.dev_blockSID.set_width_chars(18)
        self.dev_blockSID.show()
        self.blockSID_box.pack_start(self.dev_blockSID, False, False, padding)
        
        self.opal_info.pack_start(self.blockSID_box, False, False, padding)
        
        self.box_dev.pack_start(self.dev_info, True, True, padding)
        self.box_dev.pack_start(self.opal_info, False, True, padding)
        
        self.vbox.pack_start(self.box_dev, False)
        
        self.box_pbaver = gtk.HBox(homogeneous, spacing)
        
        self.dev_pbaVer = gtk.Entry()
        self.dev_pbaVer.set_property("editable", False)
        self.dev_pbaVer.set_sensitive(False)
        self.dev_pbaVer.set_width_chars(18)
        self.dev_pbaVer.show()
        self.box_pbaver.pack_end(self.dev_pbaVer, False, False, padding)
        
        self.dev_pbalabel = gtk.Label(" Preboot Image Version ")
        self.dev_pbalabel.set_width_chars(24)
        self.dev_pbalabel.show()
        self.box_pbaver.pack_end(self.dev_pbalabel, False, False, padding)
        
        self.vbox.pack_start(self.box_pbaver, False)
        
    def entry_check_box_pass(self, widget, checkbox):
        b_entry_checkbox = checkbox.get_active()
        pass_show = False
        if b_entry_checkbox:
            pass_show = True
        else:
            pass_show = False
        self.pass_entry.set_visibility(pass_show)
        self.new_pass_entry.set_visibility(pass_show)
        self.confirm_pass_entry.set_visibility(pass_show)
        return 
        
    def check_passRead(self, checkbox):
        b_entry_checkbox = checkbox.get_active()
        if b_entry_checkbox:
            self.pass_entry.set_text("")
            self.pass_entry.set_sensitive(False)
        else:
            self.pass_entry.set_sensitive(True)
            
            
    def showDrive(self, checkbox):
        b_entry_checkbox = checkbox.get_active()
        if b_entry_checkbox:
            self.drive_list = []
            dev_os = platform.system()
            if dev_os == 'Windows':
                for drive in string.ascii_uppercase:
                    if drive != 'C' and os.path.isdir('%s:\\' % drive):
                        self.drive_list.append(drive + ':')
            elif dev_os == 'Linux':
                txt = os.popen(self.prefix + 'mount').read()
                dev_regex = '/dev/sd[b-z][1-9]?\s*on\s*(\S+)\s*type'
                self.drive_list = re.findall(dev_regex, txt)
            model = self.drive_menu.get_model()
            
            iter = gtk.TreeIter
            for row in model:
                model.remove(row.iter)
            
            length = len(self.drive_list)
            
            if length > 0:
                for d in self.drive_list:
                    if dev_os == 'Windows':
                        self.drive_menu.append(d)
                    elif dev_os == 'Linux':
                        self.drive_menu.append(d)
                self.drive_menu.set_active(0)
            self.box_drive.show()
        else:
            self.box_drive.hide()
                
    def saveToText(self, *args):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Text Files")
        filter.add_mime_type("text/plain")
        filter.add_pattern("*.txt")
        chooser.add_filter(filter)
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            if not filename.endswith('.txt'):
                filename += '.txt'
            f = open(filename, 'w')
            f.write(self.queryWinText)
            f.close()
        chooser.destroy()
        
    
    def run_scan(self, *args):
        if self.firstscan == False:
            model = self.dev_select.get_model()
        
            iter = gtk.TreeIter
            for row in model:
                model.remove(row.iter)

            if len(self.vendor_list) > 0:
                self.vendor_list = []
                self.opal_ver_list = []
                self.sn_list = []
                self.salt_list = []
                self.series_list = []
                self.pba_list = []
                self.lockstatus_list = []
                self.setupstatus_list = []
        
        runop.finddev(self)
            
        length = 0
        if self.view_state == 0:
            length = len(self.devs_list)
            if length > 0:
                for idx in range(length) :
                    self.dev_select.append( self.devs_list[idx])
                self.dev_select.set_active(0)
                self.dev_single.set_text(self.devs_list[0])
                self.dev_vendor.set_text(self.vendor_list[0])
                self.dev_sn.set_text(self.sn_list[0])
                self.dev_series.set_text(self.series_list[0])
                self.dev_msid.set_text(self.msid_list[0])
                self.dev_status.set_text(self.lockstatus_list[0])
                self.dev_setup.set_text(self.setupstatus_list[0])
        elif self.view_state == 1:
            length = len(self.locked_list)
            if length > 0:
                for idx in range(length) :
                    self.dev_select.append( self.devs_list[self.locked_list[idx]])
                self.dev_select.set_active(0)
                self.dev_single.set_text(self.devs_list[self.locked_list[0]])
                self.dev_vendor.set_text(self.vendor_list[self.locked_list[0]])
                self.dev_sn.set_text(self.sn_list[self.locked_list[0]])
                self.dev_series.set_text(self.series_list[self.locked_list[0]])
                self.dev_msid.set_text(self.msid_list[self.locked_list[0]])
                self.dev_status.set_text(self.lockstatus_list[self.locked_list[0]])
                self.dev_setup.set_text(self.setupstatus_list[self.locked_list[0]])
        elif self.view_state == 2:
            length = len(self.setup_list)
            if length > 0:
                for idx in range(length) :
                    self.dev_select.append( self.devs_list[self.setup_list[idx]])
                self.dev_select.set_active(0)
                self.dev_single.set_text(self.devs_list[self.setup_list[0]])
                self.dev_vendor.set_text(self.vendor_list[self.setup_list[0]])
                self.dev_sn.set_text(self.sn_list[self.setup_list[0]])
                self.dev_series.set_text(self.series_list[self.setup_list[0]])
                self.dev_msid.set_text(self.msid_list[self.setup_list[0]])
                self.dev_status.set_text(self.lockstatus_list[self.setup_list[0]])
                self.dev_setup.set_text(self.setupstatus_list[self.setup_list[0]])
        elif self.view_state == 3:
            length = len(self.unlocked_list)
            if length > 0:
                for idx in range(length) :
                    self.dev_select.append( self.devs_list[self.unlocked_list[idx]])
                self.dev_select.set_active(0)
                self.dev_single.set_text(self.devs_list[self.unlocked_list[0]])
                self.dev_vendor.set_text(self.vendor_list[self.unlocked_list[0]])
                self.dev_sn.set_text(self.sn_list[self.unlocked_list[0]])
                self.dev_series.set_text(self.series_list[self.unlocked_list[0]])
                self.dev_msid.set_text(self.msid_list[self.unlocked_list[0]])
                self.dev_status.set_text(self.lockstatus_list[self.unlocked_list[0]])
                self.dev_setup.set_text(self.setupstatus_list[self.unlocked_list[0]])
        elif self.view_state == 4:
            length = len(self.nonsetup_list)
            if length > 0:
                for idx in range(length) :
                    self.dev_select.append( self.devs_list[self.nonsetup_list[idx]])
                self.dev_select.set_active(0)
                self.dev_single.set_text(self.devs_list[self.nonsetup_list[0]])
                self.dev_vendor.set_text(self.vendor_list[self.nonsetup_list[0]])
                self.dev_sn.set_text(self.sn_list[self.nonsetup_list[0]])
                self.dev_series.set_text(self.series_list[self.nonsetup_list[0]])
                self.dev_msid.set_text(self.msid_list[self.nonsetup_list[0]])
                self.dev_status.set_text(self.lockstatus_list[self.nonsetup_list[0]])
                self.dev_setup.set_text(self.setupstatus_list[self.nonsetup_list[0]])
        else:
            length = len(self.tcg_list)
            if length > 0:
                for idx in range(length):
                    self.dev_select.append(self.devs_list[self.tcg_list[idx]])
                self.dev_select.set_active(0)
                self.dev_single.set_text(self.devs_list[self.tcg_list[0]])
                self.dev_vendor.set_text(self.vendor_list[self.tcg_list[0]])
                self.dev_sn.set_text(self.sn_list[self.tcg_list[0]])
                self.dev_series.set_text(self.series_list[self.tcg_list[0]])
                self.dev_msid.set_text(self.msid_list[self.tcg_list[0]])
                self.dev_status.set_text(self.lockstatus_list[self.tcg_list[0]])
                self.dev_setup.set_text(self.setupstatus_list[self.tcg_list[0]])
            
        
        numTCG = len(self.tcg_list)
        
        if numTCG == 0:
            self.noTCG_instr.show()
        else:
            self.noTCG_instr.hide()
        if length > 0:
            self.scanning = True
            self.query(1)
            self.scanning = False
            self.dev_select.set_active(0)
        
        if length <= 1:
            self.dev_select.hide()
            self.label_dev.hide()
            self.dev_single.show()
            self.label_dev2.show()
        else:
            self.dev_single.hide()
            self.label_dev2.hide()
            self.dev_select.show()
            self.label_dev.show()
        
        if self.firstscan:
            self.firstscan = False
        else:
            self.msg_ok('Rescan complete')
    
            
    def query(self, mode):
        index = -1
        if self.view_state == 0 and len(self.devs_list) > 0:
            index = self.dev_select.get_active()
        elif self.view_state == 1 and len(self.locked_list) > 0:
            index = self.locked_list[self.dev_select.get_active()]
        elif self.view_state == 2 and len(self.setup_list) > 0:
            index = self.setup_list[self.dev_select.get_active()]
        elif self.view_state == 3 and len(self.unlocked_list) > 0:
            index = self.unlocked_list[self.dev_select.get_active()]
        elif self.view_state == 4 and len(self.nonsetup_list) > 0:
            index = self.nonsetup_list[self.dev_select.get_active()]
        elif self.view_state == 5 and len(self.tcg_list) > 0:
            index = self.tcg_list[self.dev_select.get_active()]
        else:
            self.msg_err('No device selected')
            return
        self.devname = self.devs_list[index]
        self.dev_vendor.set_text(self.vendor_list[index])
        self.dev_sn.set_text(self.sn_list[index])
        self.dev_series.set_text(self.series_list[index])
        self.dev_msid.set_text(self.msid_list[index])
        self.dev_opal_ver.set_text(self.opal_ver_list[index])
        self.dev_status.set_text(self.lockstatus_list[index])
        self.dev_setup.set_text(self.setupstatus_list[index])
        txt2 = ""
        txt = os.popen(self.prefix + "sedutil-cli --query " + self.devname ).read()
        
        msid = self.msid_list[index]
        
        if mode == 1:
            txt11 = "Locked ="
            m = re.search(txt11, txt)
            if m:
                txt_L = "Locked = Y"
                txt_UL = "Locked = N"
                txt_S = "LockingEnabled = Y"
                txt_ALO = "AUTHORITY_LOCKED_OUT"
                txt_NA = "NOT_AUTHORIZED"
                txt_BSID = "BlockSID"
                txt_BSID_enabled = "BlockSID_BlockSIDState = 0x001"
                
                hasBlockSID = re.search(txt_BSID, txt)
                isBlockSID = re.search(txt_BSID_enabled, txt)
                    
                if hasBlockSID and isBlockSID:
                    self.dev_blockSID.set_text("Enabled")
                elif hasBlockSID:
                    self.dev_blockSID.set_text("Disabled")
                else:
                    self.dev_blockSID.set_text("Not Supported")
                    
        elif index in self.tcg_list:
            queryTextList = ["Fidelity Lock Query information for device " + self.devname + "\n"]
            
            txtVersion = os.popen(self.prefix + "sedutil-cli --version" ).read()
            regex_ver = 'Fidelity Lock Version\s*:\s*.*'
            m = re.search(regex_ver, txtVersion)
            ver_parse = m.group()
            queryTextList.append(ver_parse + "\n\nDevice information\n")
            
            queryTextList.append("Model: " + self.dev_vendor.get_text() + "\n")
            queryTextList.append("Serial Number: " + self.dev_sn.get_text() + "\n")
            queryTextList.append("TCG SSC: " + self.dev_opal_ver.get_text() + "\n")
            queryTextList.append("MSID: " + self.dev_msid.get_text() + "\n")
            
            txtState = os.popen(self.prefix + "sedutil-cli --getmfgstate " + self.devname).read()
            regex_sp = 'adminSP life cycle state\s*:\s*(.*)\nlockingSP life cycle state\s*:\s*(.*)'
            m = re.search(regex_sp, txtState)
            admin_state = m.group(1)
            locking_state = m.group(2)
            
            queryTextList.append("Admin SP State: " + admin_state + "\nLocking SP State: " + locking_state + "\n\nLocking Information\n")
            
            #queryTextList.append("Lock Status: " + self.dev_status.get_text() + "\n")
            
            t = [ "Locked = [YN], LockingEnabled = [YN], MBR shadowing Not Supported = [YN], MBRDone = [YN], MBREnabled = [YN]",
                "Locking Objects = [0-9]*",
                "Max Tables = [0-9]*, Max Size Tables = [0-9]*",
                "Locking Admins = [0-9]*.*, Locking Users = [0-9]*.",
                "Policy = [NY].*",
                "Base comID = 0x[0-9A-F]*, Initial PIN = 0x[0-9A-F]*"]

            for txt11 in t:
                m = re.search(txt11, txt)
                if m:
                    txt1 = m.group()
                    txt11 = txt1.replace("Locking ", "")            
                    txt1 = txt11
                    txt11 = txt1.replace(", ", "\n")
                    txt2 = txt2 + txt11 + "\n"
            txt2 = self.devname + " " + self.dev_vendor.get_text() + "\n" + txt2
        
            tt = [ "Locked = [YN]", 
                    "LockingEnabled = [YN]",
                    "MBR shadowing Not Supported = [YN]",
                    "MBRDone = [YN]",
                    "MBREnabled = [YN]",
                    "Objects = [0-9]*",
                    "Max Tables = [0-9]*",
                    "Max Size Tables = [0-9]*",
                    "Admins = [0-9]",
                    "Users = [0-9]*",
                    "Policy = [YN]",
                    "Base comID = 0x[0-9A-F]*",
                    "Initial PIN = 0x[0-9A-F]*"]
                    
            sts_Locked = ""
            sts_LockingEnabled = ""
            sts_MBRShadowNotSupported = "N"
            sts_MBRDone = ""
            sts_MBREnabled = ""
            tblsz = ""
            nbr_MaxTables = ""
            nbr_Admins = ""
            nbr_Users = ""
            singleUser = ""
            comID_base = ""
            initialPIN = ""
            nbr_Objects = ""
            for txt_33 in tt:
                m = re.search(txt_33,txt2) 
                if m:
                    t3 = m.group()
                    x_words = t3.split(' = ',1)
                    if x_words[0] == "Locked":
                        sts_Locked = x_words[1]
                    elif x_words[0] == "LockingEnabled":
                        sts_LockingEnabled = x_words[1]                   
                    elif x_words[0] == "MBR shadowing Not Supported":
                        sts_MBRShadowNotSupported = x_words[1]
                    elif x_words[0] == "MBRDone":
                        sts_MBRDone = x_words[1]
                    elif x_words[0] == "MBREnabled":
                        sts_MBREnabled = x_words[1]
                    elif x_words[0] == "Max Size Tables":
                        tblsz_i = int(x_words[1],10)   
                        tblsz = str(tblsz_i/1000000) + "MB"
                    elif x_words[0] == "Max Tables":
                        nbr_MaxTables = x_words[1]
                    elif x_words[0] == "Objects":
                        nbr_Objects = x_words[1]
                    elif x_words[0] == "Admins":
                        nbr_Admins = x_words[1]
                    elif x_words[0] == "Users":
                        nbr_Users = x_words[1]  
                    elif x_words[0] == "Policy":
                        singleUser = x_words[1]
                    elif x_words[0] == "Base comID":
                        comID_base = x_words[1]
                    elif x_words[0] == "Initial PIN":
                        initialPIN = x_words[1]
            queryTextList.append("Locked: " + sts_Locked + "\n")
            queryTextList.append("Locking Enabled: " + sts_LockingEnabled + "\n")
            queryTextList.append("MBR Shadowing Not Supported: " + sts_MBRShadowNotSupported + "\n")
            queryTextList.append("Shadow MBR Enabled: " + sts_MBREnabled + "\n")
            queryTextList.append("Shadow MBR Done: " + sts_MBRDone + "\n\nSingle User information\n")
            queryTextList.append("Single User Mode Support: " + singleUser + "\n")
            queryTextList.append("Number of Locking Ranges Supported: " + nbr_Objects + "\n\nDataStore information\n")
            queryTextList.append("DataStore Table Size: " + tblsz + "\n")
            queryTextList.append("Number of DataStore Tables: " + nbr_MaxTables + "\n\nOpal information\n")
            queryTextList.append("Number of Admins: " + nbr_Admins + "\n")
            queryTextList.append("Number of Users: " + nbr_Users + "\n")
            queryTextList.append("Base comID: " + comID_base + "\n")
            queryTextList.append("Initial PIN: " + initialPIN + "\n")
            
            self.queryWinText = ''.join(queryTextList)
        
            if not self.scanning :
                self.queryTextBuffer.set_text(self.queryWinText)
                if self.VERSION != 1:
                    self.queryPass.set_text('')
                self.queryWin.show_all()
                
            else:
                self.scanning = False
        else:
            self.msg_err('Non-TCG devices cannot be queried.')

    def queryAuth(self, *args):
        salt = ''
        index = self.dev_select.get_active()
        if self.view_state == 0:
            salt = self.salt_list[index]
        elif self.view_state == 1:
            salt = self.salt_list[self.locked_list[index]]
        elif self.view_state == 2:
            salt = self.salt_list[self.setup_list[index]]
        elif self.view_state == 3:
            salt = self.salt_list[self.unlocked_list[index]]
        elif self.view_state == 4:
            salt = self.salt_list[self.nonsetup_list[index]]
        elif self.view_state == 5:
            salt = self.salt_list[self.tcg_list[index]]
        devpass = lockhash.hash_pass(self.queryPass.get_text(), salt, self.dev_msid.get_text())
        level = self.authQuery.get_active()
        m3 = ''
        if level == 0:
            p0 = os.popen(self.prefix + "sedutil-cli -n -t --getmbrsize " + devpass + " " + self.devname).read()
            out_regex = 'Shadow.+(?:\n.+)+'
            m3 = re.search(out_regex, p0)
            if not m3:
                self.msg_err("Error: Invalid password")
                return
        txt1 = "NOT_AUTHORIZED"
        txt2 = "AUTHORITY_LOCKED_OUT"
        p1 = ''
        p2 = ''
        if self.VERSION != 1:
            timeStr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            timeStr = timeStr[2:]
            if level == 1:
                statusAW = os.system(self.prefix + "sedutil-cli -n -t -u --auditwrite 03" + timeStr + " " + devpass + " User1 " + self.devname)
                if statusAW != 0:
                    self.msg_err("Error: Invalid password")
                    return
                p2 = os.popen(self.prefix + "sedutil-cli -n -t -u --auditread " + devpass + " User1 " + self.devname).read()
            else:
                statusAW = os.system(self.prefix + "sedutil-cli -n -t -u --auditwrite 02" + timeStr + " " + devpass + " Admin1 " + self.devname)
                if statusAW != 0:
                    self.msg_err("Error: Invalid password")
                    return
                p2 = os.popen(self.prefix + "sedutil-cli -n -t --auditread " + devpass + " Admin1 " + self.devname).read()
        if level == 0:
            p1 = os.popen(self.prefix + "sedutil-cli -n -t --pbaValid " + devpass + " " + self.devname).read()
            r = 'PBA image version \s*:'
            t = re.search(r, p1)
            if not t:
                self.msg_err("Error: Invalid password")
                return
        pba_regex = 'PBA image version\s*:\s*(.+)'
        audit_regex = 'Fidelity Audit Log Version\s*([0-9]+\.[0-9]+)\s*:'
        m1 = re.search(pba_regex, p1)
        m2 = re.search(audit_regex, p2)
        pba_ver = ''
        audit_ver = ''
        if m1:
            pba_ver = m1.group(1)
        else:
            pba_ver = 'N/A'
        if m2:
            audit_ver = m2.group(1)
        else:
            audit_ver = 'N/A'
        if self.VERSION != 1:
            if level == 0:
                self.queryWinText = self.queryWinText + "\n" + m3.group(0) + "\nPBA image version: " + pba_ver + "\nAudit Log Version: " + audit_ver
            else:
                self.queryWinText = self.queryWinText + "\nAudit Log Version: " + audit_ver
        else:
            self.queryWinText = self.queryWinText + "\n" + m3.group(0) + "\nPBA image version: " + pba_ver
        self.queryTextBuffer.set_text(self.queryWinText)
        self.passBoxQ.hide()
        self.authBoxQ.hide()
        self.query_instr.hide()

    def exitapp(self, *args):
        exit(0)

    def reboot(self, *args):
        if self.ostype == 0 :
            status =  os.system("shutdown -r -t 0")
        elif self.ostype == 1 :
            status =  os.system(self.prefix + "reboot now")
        elif self.ostype == 2 :
            status =  os.system(self.prefix + "reboot now")    
        exit(0)
            
    def shutdown(self, *args):
        if self.ostype == 0 :
            status =  os.system("shutdown -s -t 0")
        elif self.ostype == 1 :
            status =  os.system(self.prefix + "poweroff")
        elif self.ostype == 2 :
            status =  os.system(self.prefix + "poweroff")    
        exit(0)
    
    def changed_cb(self, entry):
        act_idx = self.dev_select.get_active()
        if self.view_state == 0:
            self.devname = self.devs_list[act_idx]
            self.dev_vendor.set_text(self.vendor_list[act_idx])
            self.dev_single.set_text(self.devs_list[act_idx])
            self.dev_sn.set_text(self.sn_list[act_idx])
            self.dev_msid.set_text(self.msid_list[act_idx])
            self.dev_pbaVer.set_text(self.pba_list[act_idx])
        elif self.view_state == 1:
            self.devname = self.devs_list[self.locked_list[act_idx]]
            self.dev_vendor.set_text(self.vendor_list[self.locked_list[act_idx]])
            self.dev_single.set_text(self.devs_list[self.locked_list[act_idx]])
            self.dev_sn.set_text(self.sn_list[self.locked_list[act_idx]])
            self.dev_msid.set_text(self.msid_list[self.locked_list[act_idx]])
            self.dev_pbaVer.set_text(self.pba_list[self.locked_list[act_idx]])
        elif self.view_state == 2:
            self.devname = self.devs_list[self.setup_list[act_idx]]
            self.dev_vendor.set_text(self.vendor_list[self.setup_list[act_idx]])
            self.dev_single.set_text(self.devs_list[self.setup_list[act_idx]])
            self.dev_sn.set_text(self.sn_list[self.setup_list[act_idx]])
            self.dev_msid.set_text(self.msid_list[self.setup_list[act_idx]])
            self.dev_pbaVer.set_text(self.pba_list[self.setup_list[act_idx]])
        elif self.view_state == 3:
            self.devname = self.devs_list[self.unlocked_list[act_idx]]
            self.dev_vendor.set_text(self.vendor_list[self.unlocked_list[act_idx]])
            self.dev_single.set_text(self.devs_list[self.unlocked_list[act_idx]])
            self.dev_sn.set_text(self.sn_list[self.unlocked_list[act_idx]])
            self.dev_msid.set_text(self.msid_list[self.unlocked_list[act_idx]])
            self.dev_pbaVer.set_text(self.pba_list[self.unlocked_list[act_idx]])
        elif self.view_state == 4:
            self.devname = self.devs_list[self.nonsetup_list[act_idx]]
            self.dev_vendor.set_text(self.vendor_list[self.nonsetup_list[act_idx]])
            self.dev_single.set_text(self.devs_list[self.nonsetup_list[act_idx]])
            self.dev_sn.set_text(self.sn_list[self.nonsetup_list[act_idx]])
            self.dev_msid.set_text(self.msid_list[self.nonsetup_list[act_idx]])
            self.dev_pbaVer.set_text(self.pba_list[self.nonsetup_list[act_idx]])
        else:
            self.devname = self.devs_list[self.tcg_list[act_idx]]
            self.dev_vendor.set_text(self.vendor_list[self.tcg_list[act_idx]])
            self.dev_single.set_text(self.devs_list[self.tcg_list[act_idx]])
            self.dev_sn.set_text(self.sn_list[self.tcg_list[act_idx]])
            self.dev_msid.set_text(self.msid_list[self.tcg_list[act_idx]])
            self.dev_pbaVer.set_text(self.pba_list[self.tcg_list[act_idx]])
            
        if self.opal_ver_list[act_idx] != "None":
            self.scanning = True
            self.query(1)
            self.scanning = False
        else:
            self.dev_opal_ver.set_text("None")
            self.dev_status.set_text("N/A")
            self.dev_msid.set_text("N/A")
            self.dev_setup.set_text("N/A")
    
    def pass_dialog(self, *args):
        homogeneous = False
        spacing = 0
        expand = False
        fill = False
        padding = 0
        width = 12
        self.box_pass = gtk.HBox(homogeneous, 0)
        
        self.pass_label = gtk.Label("Enter Password")
        self.pass_label.set_width_chars(22)
        self.pass_label.set_alignment(0,0.5)
        self.box_pass.pack_start(self.pass_label, expand, fill, padding)
        
        self.pass_entry = gtk.Entry()
        self.pass_entry.set_text("")
        self.pass_entry.set_visibility(False)
        self.pass_entry.set_width_chars(27)
        self.box_pass.pack_start(self.pass_entry, False, False, padding)
        
 
        if self.VERSION % 2 == 1:
            self.check_pass_rd = gtk.CheckButton("Read password from USB")
            self.check_pass_rd.connect("toggled", self.check_passRead)
            self.check_pass_rd.show()
            self.check_pass_rd.set_tooltip_text('Authenticate using the drive\'s password file from USB')
            self.box_pass.pack_start(self.check_pass_rd, True, fill, padding)
     
        self.vbox.pack_start(self.box_pass, False)
        
    def new_pass_dialog(self, *args):
        homogeneous = False
        spacing = 0
        expand = False
        fill = False
        padding = 0
    
        self.box_newpass = gtk.HBox(homogeneous, 0)
        
        self.new_pass_label = gtk.Label("Enter New Password")
        self.new_pass_label.set_width_chars(22)
        self.new_pass_label.set_alignment(0,0.5)
        self.box_newpass.pack_start(self.new_pass_label, expand, fill, padding)
        self.new_pass_entry = gtk.Entry()
        self.new_pass_entry.set_text("")
        self.new_pass_entry.set_visibility(False)
        self.new_pass_entry.set_width_chars(27)
        self.box_newpass.pack_start(self.new_pass_entry, False, False, padding)
 
        if self.VERSION % 2 == 1:
            self.pass_sav = gtk.CheckButton("Save to USB")
            self.pass_sav.connect("clicked", self.showDrive)
            self.pass_sav.show()
            self.pass_sav.set_tooltip_text('Save the password to a file on a USB device')
            self.box_newpass.pack_start(self.pass_sav, True, fill, padding)
        
        self.vbox.pack_start(self.box_newpass, False)
        
    def openLog_prompt(self, *args):
        self.hideAll()
        self.op_label.set_text('View Audit Log')
        self.op_instr.set_text('\nThe audit log stores a log of actions done on the drive by this application.\nEnter the drive\'s password to access its audit log.')
        self.go_button_cancel.show()
        
        if self.view_state != 5:
            self.view_state = 5
            self.changeList()
        
        if len(self.tcg_list) > 0:
            self.select_instr.show()
            self.dev_select.set_active(0)
        if len(self.tcg_list) == 0:
            self.naDev()
        else:
            self.op_instr.show()
            
            self.box_pass.show()
            self.pass_entry.set_activates_default(True)
            self.pass_entry.grab_focus()
            
            self.viewLog.show()
            self.set_default(self.viewLog)
            
            self.check_box_pass.show()
            
            self.query(1)
            if self.VERSION % 2 == 1:
                self.box_auth.show()
      
    def msg_err(self, msg):
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup(msg)
        res = message.run()
        print message.get_widget_for_response(gtk.RESPONSE_OK)
        print gtk.RESPONSE_OK
        if res == gtk.RESPONSE_OK :
            print "OK button clicked"
        message.destroy()
        
    def msg_ok(self, msg):
        message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
        message.set_markup(msg)
        res = message.run()
        print message.get_widget_for_response(gtk.RESPONSE_OK)
        print gtk.RESPONSE_OK
        if res == gtk.RESPONSE_OK :
            print "OK button clicked"
        message.destroy()
        
    def setup_finish(self, *args):
        index = self.nonsetup_list[self.dev_select.get_active()]
        dev_os = platform.system()
        if dev_os == 'Windows':
            verified = powerset.verify_power()
            if index == 0 and not verified:
                message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_YES_NO)
                message.set_markup("We recommend changing your power settings to better secure your data, would you like to proceed with the changes?")
                res = message.run()
                if res == gtk.RESPONSE_YES:
                    message.destroy()
                    powerset.set_power()
                    self.msg_ok("Your power settings have been changed successfully.")
                elif res == gtk.RESPONSE_NO:
                    message.destroy()
        self.msg_ok("Device " + self.devname + "has been setup successfully.") 
        self.updateDevs(index,[2,3])
        
        self.returnToMain()

    def returnToMain(self, *args):
        self.hideAll()
        self.op_label.set_text('Main')
        self.main_instr.show()
        
        if self.view_state != 0:
            self.view_state = 0
            self.changeList()
        
        if len(self.devs_list) > 0:
            self.dev_select.set_active(0)
            
        self.query(1)
            
        #if self.VERSION == 1:
        #    self.unlock_prompt()
            
    def setup_prompt1(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Full Setup')
        self.op_instr.set_text('\nSetting up a drive includes setting a password which you can use to unlock the drive.\nEnter the new password for the drive and click \'Continue\'.')
        
        if self.view_state != 4:
            self.view_state = 4
            self.changeList()
        
        if len(self.nonsetup_list) > 1:
            self.select_instr.show()
            
        if len(self.nonsetup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            
            self.box_newpass.show()
            self.box_newpass_confirm.show()
            self.setup_next.show()
            
            self.check_box_pass.show()
            
            self.query(1)
        else:
            self.naDevices_instr.show()
        
    def setup_prompt2(self, *args):
        self.box_drive.hide()
        self.box_newpass.hide()
        self.box_newpass_confirm.hide()
        self.setup_next.hide()
        self.check_box_pass.hide()
        self.setupLockOnly.show()
        self.setupLockPBA.show()
        self.op_instr.set_text('\nThe Preboot image is used to unlock the drive for use.\nTo write the image to the shadow MBR, press \'Write Preboot Image\'.')
        self.op_instr.show()
    
        self.go_button_cancel.hide()
        
    def setupPW_prompt(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Set Up Password Only')
        self.op_instr.set_text('\nSetting up a drive includes setting a password which you can use to unlock the drive.\nEnter the new password for the drive and click \'Continue\'.')
        
        if self.view_state != 4:
            self.view_state = 4
            self.changeList()
            
        
        if len(self.nonsetup_list) > 1:
            self.select_instr.show()
            
        if len(self.nonsetup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            
            self.box_newpass.show()
            self.box_newpass_confirm.show()
            self.setupPWOnly.show()
            
            self.check_box_pass.show()
            
            self.query(1)
        else:
            self.naDevices_instr.show()
            
    def setupUser_prompt(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Set Up User Password')
        self.op_instr.set_text('\nSetting up a user password creates a second password with limited authority.')
        
        if self.view_state != 2:
            self.view_state = 2
            self.changeList()
            
        if len(self.setup_list) > 1:
            self.select_instr.show()
            
        if len(self.setup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            self.setupUserPW.show()
            
            self.pass_label.set_text('Enter Admin Password')
            self.new_pass_label.set_text('Enter User Password')
            self.confirm_pass_label.set_text('Confirm User Password')
            self.box_pass.show()
            self.box_newpass.show()
            self.box_newpass_confirm.show()
            self.check_box_pass.show()
            
            self.query(1)
            
        else:
            self.naDevices_instr.show()
        
    def updatePBA_prompt(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Update Preboot Image')
        self.op_instr.set_text('\nUse this to rewrite the Preboot Image or write the image to a set up drive.\nEnter the drive\'s password and press \'Update\'.')
        
        if self.view_state != 2:
            self.view_state = 2
            self.changeList()
        
        if len(self.setup_list) > 1:
            self.select_instr.show()
            
        if len(self.setup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            self.updatePBA_button.show()
            self.set_default(self.updatePBA_button)
            
            self.pass_label.set_text('Enter Admin Password')
            self.box_pass.show()
            self.pass_entry.set_activates_default(True)
            self.pass_entry.grab_focus()
            
            self.check_box_pass.show()
            
            self.query(1)
        else:
            self.naDevices_instr.show()

    def changePW_prompt(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Change Password')
        self.op_instr.set_text('\nTo change the password of the selected drive, enter the drive\'s current password\nand the new password.')
        
        if self.view_state != 2:
            self.view_state = 2
            self.changeList()
        
        if len(self.setup_list) > 1:
            self.select_instr.show()
            
        if len(self.setup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            
            self.box_pass.show()
            self.box_newpass.show()
            self.box_newpass_confirm.show()
            self.go_button_changePW_confirm.show()
            
            self.check_box_pass.show()
            
            if self.VERSION % 2 == 1:
                self.box_auth.show()
            
            self.query(1)
        else:
            self.naDevices_instr.show()
            
    def setupUSB_prompt(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Set up USB')
        self.op_instr.set_text('\nThis will write the bootable image to a USB drive.  You can then use the USB drive to unlock your drive(s).')
        
        if self.view_state != 0:
            self.view_state = 0
            self.changeList()
            
        if len(self.devs_list) > 0:
            self.dev_select.set_active(0)
            self.query(1)
            
        self.drive_list = []
        dev_os = platform.system()
        if dev_os == 'Windows':
            #for drive in ascii_uppercase:
            #    if drive != 'C' and os.path.isdir('%s:\\' % drive):
            #        self.drive_list.append(drive + ':')
            txt = os.popen(self.prefix + 'wmic diskdrive list brief /format:list').read()
            mod_regex = 'DeviceID=.+([1-9]|1[0-5])\s*\nModel=(.*)\r'
            self.usb_list = re.findall(mod_regex, txt)
        elif dev_os == 'Linux':
            txt = os.popen(self.prefix + 'mount').read()
            dev_regex = '/dev/sd[b-z][1-9]?\s*on\s*(\S+)\s*type'
            drive_list = re.findall(dev_regex, txt)
            
            txt2 = os.popen(self.prefix + 'blkid').read()
            dev_regex2 = '(/dev/sd[b-z][1-9]?.+)'
            all_list = re.findall(dev_regex2, txt2)
            r1 = '/dev/sd[b-z][1-9]?'
            r2 = 'TYPE="([a-z]+)"'
            for a in all_list:
                m1 = re.search(r1,a)
                m2 = re.search(r2,a)
                dev_a = m1.group(0)
                type_a = m2.group(1)
                if dev_a not in drive_list:
                    s = os.system(self.prefix + 'mount -t ' + type_a + ' ' + dev_a)
                    drive_list.append(dev_a)
            txt3 = os.popen('mount').read()
            dev_regex3 = '(/dev/sd[b-z][1-9]?)\s*on\s*(\S+)\s*type'
            self.usb_list = re.findall(dev_regex3, txt3)
        model = self.usb_menu.get_model()
        
        iter = gtk.TreeIter
        for row in model:
            model.remove(row.iter)
        
        length = len(self.usb_list)
        
        if length > 0:
            
            for d in self.usb_list:
                if dev_os == 'Windows':
                    self.usb_menu.append(d[1])
                elif dev_os == 'Linux':
                    self.usb_menu.append(d[0])
            self.box_pbausb.show()
            self.usb_menu.set_active(0)
            self.op_instr.show()
            self.setupUSB_button.show()
        
        else:
            self.naDevices_instr.show()
        
    def revert_erase_prompt(self, *args):
        self.hideAll()
        self.op_label.set_text('Revert with Password')
        self.op_instr.set_text('\nRevert with Password reverts the drive\'s LockingSP.\nThis resets the drive\'s password and disables locking.\nEnter the drive\'s password and choose whether or not to erase all data.')
        self.go_button_cancel.show()
        
        if self.view_state != 2:
            self.view_state = 2
            self.changeList()
        
        if len(self.setup_list) > 1:
            self.select_instr.show()
            
        if len(self.setup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            
            self.pass_label.set_text('Enter Admin Password')
            self.box_pass.show()
            self.pass_entry.set_activates_default(True)
            self.pass_entry.grab_focus()
            
            self.go_button_revert_user_confirm.show()
            self.set_default(self.go_button_revert_user_confirm)
            
            self.check_box_pass.show()
            #self.eraseData_check.show()
            self.query(1)  
        else:
            self.naDevices_instr.show()
        
    def revert_psid_prompt(self, *args):
        self.hideAll()
        self.go_button_cancel.show()
        self.op_label.set_text('Revert with PSID')
        self.op_instr.set_text('\nReverting with PSID reverts the drive to manufacturer settings and erases all data.\nEnter the drive\'s PSID and press \'Revert with PSID\'.')
        
        if self.view_state != 5:
            self.view_state = 5
            self.changeList()
            
        if len(self.tcg_list) > 1:
            self.select_instr.show()
            
        if len(self.tcg_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            
            self.box_psid.show()
            self.go_button_revert_psid_confirm.show()
            self.revert_psid_entry.set_text("")
            
            self.query(1)
        else:
            self.naDevices_instr.show()
        
    def unlock_prompt(self, *args):
        self.hideAll()
        self.op_label.set_text('Preboot Unlock')
        self.op_instr.set_text('\nPreboot Unlock unlocks a drive for bootup.\nEnter the drive\'s password and press \'Preboot Unlock\'\nAfterwards, reboot into the unlocked drive.')
        self.go_button_cancel.show()
        
        if self.view_state != 1:
            self.view_state = 1
            self.changeList()
            
        if len(self.locked_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()

            self.box_pass.show()
            self.pass_entry.set_activates_default(True)
            self.pass_entry.grab_focus()
            
            self.pbaUnlockReboot.show()
            self.pbaUnlockOnly.show()
            self.set_default(self.pbaUnlockReboot)
            
            self.check_box_pass.show()
        
            self.query(1)
            if self.VERSION % 2 == 1:
                self.box_auth.show()
        else:
            self.naDevices_instr.show()
                
                
        if len(self.locked_list) > 1:
            self.select_instr.show()
                  
    def revert_keep_prompt(self, *args):
        self.hideAll()
        self.op_label.set_text('Revert Only')
        self.op_instr.set_text('\nReverting a drive disables locking and resets the drive password.\nEnter the password and press \'Revert Drive\'.')
        self.go_button_cancel.show()
        
        if self.view_state != 2:
            self.view_state = 2
            self.changeList()

        if len(self.setup_list) > 1:
            self.select_instr.show()
            
        if len(self.setup_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()

            self.pass_label.set_text('Enter Admin Password')
            self.box_pass.show()
            self.pass_entry.set_activates_default(True)
            self.pass_entry.grab_focus()
            
            self.revertOnly_button.show()
            self.set_default(self.revertOnly_button)
            
            self.check_box_pass.show()
            
            self.query(1)
        else:
            self.naDevices_instr.show()
            
    #def disableLock_prompt(self, *args):
    #    self.hideAll()
    #    self.op_label.set_text('Disable Lock')
    #    self.op_instr.set_text('\nDisabling the lock stops the drive from locking itself when it shuts down, but keeps the set up password.\nEnter the password and press \'Disable Lock\'.')
    #    self.go_button_cancel.show()
    #    
    #    if self.view_state != 2:
    #        self.view_state = 2
    #        self.changeList()
    #
    #    if len(self.setup_list) > 1:
    #        self.select_instr.show()
    #        
    #    if len(self.setup_list) > 0:
    #        self.dev_select.set_active(0)
    #        self.op_instr.show()
    #
    #        self.pass_label.set_text('Enter Admin Password')
    #        self.box_pass.show()
    #        self.pass_entry.set_activates_default(True)
    #        self.pass_entry.grab_focus()
    #        
    #        self.disableLock_button.show()
    #        self.set_default(self.disableLock_button)
    #        
    #        self.check_box_pass.show()
    #        
    #        self.query(1)
    #    else:
    #        self.naDevices_instr.show()

    def unlockUSB_prompt(self, *args):
        self.hideAll()
        self.op_label.set_text('Unlock with USB')
        self.op_instr.set_text('\nUnlock with USB reads passwords from files on your USB to unlock device(s).\nMake sure your USB is mounted and press \'Unlock with USB\'.')
        self.go_button_cancel.show()
        
        if self.view_state != 1:
            self.view_state = 1
            self.changeList()
            
        if len(self.locked_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()

            self.pbaUSB_button.show()
            
            self.query(1)
            
        else:
            self.naDevices_instr.show()

    #def lockEnable_prompt(self, *args):
    #    self.hideAll()
    #    self.op_label.set_text('Lock')
    #    self.op_instr.set_text('\nThis operation enables locking on a drive.\nEnter the selected drive\'s password and press \'Enable Lock\'.')
    #    
    #    self.go_button_cancel.show()
    #    
    #    if self.view_state != 3:
    #        self.view_state = 3
    #        self.changeList()
    #
    #    if len(self.unlocked_list) > 1:
    #        self.select_instr.show()
    #        
    #    if len(self.unlocked_list) > 0:
    #        self.dev_select.set_active(0)
    #        self.op_instr.show()
    #        self.lockEnable_button.show()
    #        self.set_default(self.lockEnable_button)
    #        
    #        self.pass_label.set_text('Enter Admin Password')
    #        self.box_pass.show()
    #        self.pass_entry.set_activates_default(True)
    #        self.pass_entry.grab_focus()
    #        
    #        self.check_box_pass.show()
    #        
    #        self.query(1)
    #        
    #    else:
    #        self.naDevices_instr.show()
            
    def lock_prompt(self, *args):
        self.hideAll()
        self.op_label.set_text('Lock')
        self.op_instr.set_text('\nThis operation enables locking on a drive.\nEnter the selected drive\'s password and press \'Enable Lock\'.')
        
        self.go_button_cancel.show()
        
        if self.view_state != 3:
            self.view_state = 3
            self.changeList()
		
        if len(self.unlocked_list) > 1:
            self.select_instr.show()
            
        if len(self.unlocked_list) > 0:
            self.dev_select.set_active(0)
            self.op_instr.show()
            self.lock_button.show()
            self.set_default(self.lock_button)
            
            self.pass_label.set_text('Enter Admin Password')
            self.box_pass.show()
            self.pass_entry.set_activates_default(True)
            self.pass_entry.grab_focus()
            
            self.check_box_pass.show()
            
            self.query(1)
            
        else:
            self.naDevices_instr.show()
            
    def show_about(self, *args):
        aboutWin = gtk.Window()
        txtVersion = os.popen(self.prefix + "sedutil-cli --version" ).read()
        regex_ver = 'Fidelity Lock Version\s*:\s*.*'
        m = re.search(regex_ver, txtVersion)
        ver_parse = m.group()
        about_label = gtk.Label(ver_parse)
        aboutWin.add(about_label)
        aboutWin.show_all()

    def hideAll(self, *args):
        self.select_instr.hide()
        self.naDevices_instr.hide()
        self.main_instr.hide()
        self.wait_instr.hide()
        self.pba_wait_instr.hide()
        self.op_instr.hide()
    
        self.pass_entry.set_text("")
        self.new_pass_entry.set_text("")
        self.confirm_pass_entry.set_text("")
        #self.eraseData_check.set_active(False)
        self.check_box_pass.set_active(False)
        
        self.box_pass.hide()
        self.box_psid.hide()
        self.go_button_cancel.hide()
        self.go_button_revert_user_confirm.hide()
        self.go_button_revert_psid_confirm.hide()
        self.go_button_changePW_confirm.hide()
        self.setupLockOnly.hide()
        self.setupLockPBA.hide()        
        self.pbaUnlockReboot.hide()
        self.pbaUnlockOnly.hide()
        self.setupPWOnly.hide()
        self.updatePBA_button.hide()
        self.setupUSB_button.hide()
        self.setupUserPW.hide()
        
        self.revertOnly_button.hide()
        #self.disableLock_button.hide()
        self.viewLog.hide()
        self.pbaUSB_button.hide()
        self.lock_button.hide()
        #self.lockEnable_button.hide()
        
        self.box_newpass.hide()
        self.box_newpass_confirm.hide()
        
        self.pass_label.set_text('Enter Password')
        self.new_pass_label.set_text('Enter New Password')
        self.confirm_pass_label.set_text('Confirm New Password')
        
        self.box_drive.hide()
        self.box_auth.hide()
        self.box_pbausb.hide()
        self.setup_next.hide()
        
        self.check_box_pass.hide()
        #self.eraseData_check.hide()
        
        self.auth_menu.set_active(0)
        
        self.waitSpin.hide()
        
        self.pass_entry.set_activates_default(False)
        self.set_default(None)
        
    def start_spin(self, *args):
        self.op_instr.hide()
        self.disable_menu()
        self.waitSpin.show()
        self.waitSpin.start()
        
    def stop_spin(self, *args):
        self.enable_menu()
        self.waitSpin.stop()
        self.waitSpin.hide()
        self.op_instr.show()
        self.pba_wait_instr.hide()
        self.wait_instr.hide()
        
    def disable_menu(self, *args):
        self.navM.set_sensitive(False)
        self.devM.set_sensitive(False)
        self.setupM.set_sensitive(False)
        self.revertM.set_sensitive(False)
        self.helpM.set_sensitive(False)
        self.unlockM.set_sensitive(False)
        if self.VERSION != 1:
            self.lockM.set_sensitive(False)
        if self.VERSION % 2 == 0:
            self.upgradeM.set_sensitive(False)
        
        self.go_button_cancel.set_sensitive(False)
        self.go_button_revert_user_confirm.set_sensitive(False)
        self.go_button_revert_psid_confirm.set_sensitive(False)
        self.go_button_changePW_confirm.set_sensitive(False)
        self.setupLockOnly.set_sensitive(False)
        self.setupLockPBA.set_sensitive(False)
        self.setupUSB_button.set_sensitive(False)
        self.pbaUnlockReboot.set_sensitive(False)
        self.pbaUnlockOnly.set_sensitive(False)
        self.setupPWOnly.set_sensitive(False)
        self.updatePBA_button.set_sensitive(False)
        self.pbaUSB_button.set_sensitive(False)
        #self.lockEnable_button.set_sensitive(False)
        self.lock_button.set_sensitive(False)
        self.revertOnly_button.set_sensitive(False)
        #self.disableLock_button.set_sensitive(False)
        self.viewLog.set_sensitive(False)
        
        self.box_auth.set_sensitive(False)
        self.box_pass.set_sensitive(False)
        self.box_newpass.set_sensitive(False)
        self.box_newpass_confirm.set_sensitive(False)
        self.box_drive.set_sensitive(False)
        self.box_pbausb.set_sensitive(False)
        self.box_auth.set_sensitive(False)
        self.checkbox_box.set_sensitive(False)
        self.setup_next.set_sensitive(False)
        
        
    def enable_menu(self, *args):
        self.navM.set_sensitive(True)
        self.devM.set_sensitive(True)
        self.setupM.set_sensitive(True)
        self.revertM.set_sensitive(True)
        self.helpM.set_sensitive(True)
        self.unlockM.set_sensitive(True)
        if self.VERSION != 1:
            self.lockM.set_sensitive(True)
        if self.VERSION % 2 == 0:
            self.upgradeM.set_sensitive(True)
        
        self.go_button_cancel.set_sensitive(True)
        self.go_button_revert_user_confirm.set_sensitive(True)
        self.go_button_revert_psid_confirm.set_sensitive(True)
        self.go_button_changePW_confirm.set_sensitive(True)
        self.setupLockOnly.set_sensitive(True)
        self.setupLockPBA.set_sensitive(True)
        self.setupUSB_button.set_sensitive(True)
        self.pbaUnlockReboot.set_sensitive(True)
        self.pbaUnlockOnly.set_sensitive(True)
        self.setupPWOnly.set_sensitive(True)
        self.updatePBA_button.set_sensitive(True)
        self.pbaUSB_button.set_sensitive(True)
        #self.lockEnable_button.set_sensitive(True)
        self.lock_button.set_sensitive(True)
        self.revertOnly_button.set_sensitive(True)
        #self.disableLock_button.set_sensitive(True)
        self.viewLog.set_sensitive(True)
        
        self.box_pass.set_sensitive(True)
        self.box_newpass.set_sensitive(True)
        self.box_newpass_confirm.set_sensitive(True)
        self.box_drive.set_sensitive(True)
        self.box_pbausb.set_sensitive(True)
        self.box_auth.set_sensitive(True)
        self.checkbox_box.set_sensitive(True)
        self.setup_next.set_sensitive(True)
        
    def updateDevs(self, index, add, *args):
        if index in self.locked_list:
            self.locked_list.remove(index)
        if index in self.setup_list:
            self.setup_list.remove(index)
        if index in self.unlocked_list:
            self.unlocked_list.remove(index)
        if index in self.nonsetup_list:
            self.nonsetup_list.remove(index)
        for j in add:
            if j == 1:
                self.locked_list.append(index)
            elif j == 2:
                self.setup_list.append(index)
            elif j == 3:
                self.unlocked_list.append(index)
            elif j == 4:
                self.nonsetup_list.append(index)
                
        self.locked_list.sort()
        self.setup_list.sort()
        self.unlocked_list.sort()
        self.nonsetup_list.sort()
        
    def changeList(self, *args):
        model = self.dev_select.get_model()
        
        iter = gtk.TreeIter
        for row in model:
            model.remove(row.iter)
        
        length = 0
        
        if self.view_state == 0:
            length = len(self.devs_list)
            for i in range(length):
                self.dev_select.append(self.devs_list[i])
            if length == 1:
                self.dev_single.set_text(self.devs_list[0])
        elif self.view_state == 1:
            length = len(self.locked_list)
            for i in range(length):
                self.dev_select.append(self.devs_list[self.locked_list[i]])
            if length == 1:
                self.dev_single.set_text(self.devs_list[self.locked_list[0]])
        elif self.view_state == 2:
            length = len(self.setup_list)
            for i in range(length):
                self.dev_select.append(self.devs_list[self.setup_list[i]])
            if length == 1:
                self.dev_single.set_text(self.devs_list[self.setup_list[0]])
        elif self.view_state == 3:
            length = len(self.unlocked_list)
            for i in range(length):
                self.dev_select.append(self.devs_list[self.unlocked_list[i]])
            if length == 1:
                self.dev_single.set_text(self.devs_list[self.unlocked_list[0]])
        elif self.view_state == 4:
            length = len(self.nonsetup_list)
            for i in range(length):
                self.dev_select.append(self.devs_list[self.nonsetup_list[i]])
            if length == 1:
                self.dev_single.set_text(self.devs_list[self.nonsetup_list[0]])
        else:
            length = len(self.tcg_list)
            for i in range(length):
                self.dev_select.append(self.devs_list[self.tcg_list[i]])
            if length == 1:
                self.dev_single.set_text(self.devs_list[self.tcg_list[0]])
        
        if length <= 1:
            self.dev_single.show()
            self.label_dev2.show()
            self.dev_select.hide()
            self.label_dev.hide()
            if length == 0:
                self.dev_single.set_text('None')
                self.dev_vendor.set_text('N/A')
                self.dev_sn.set_text('N/A')
                self.dev_msid.set_text('N/A')
                self.dev_opal_ver.set_text('N/A')
                self.dev_status.set_text('N/A')
                self.dev_setup.set_text('N/A')
                self.dev_series.set_text('N/A')
                self.dev_blockSID.set_text('N/A')
        else:
            self.dev_single.hide()
            self.label_dev2.hide()
            self.dev_select.show()
            self.label_dev.show()
            
    def hide_queryWin(event, self, widget):
        self.hide()
        return True
        
    def destroy_main(event, self, widget):
        gtk.main_quit()
        return False
                        
    def run(self):
        ''' Run the app. '''
        
        gtk.main()

app = LockApp()
app.run()