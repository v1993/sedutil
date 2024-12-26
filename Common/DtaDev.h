/* C:B**************************************************************************
 This software is Copyright (c) 2014-2024 Bright Plaza Inc. <drivetrust@drivetrust.com>

 This file is part of sedutil.

 sedutil is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 sedutil is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with sedutil.  If not, see <http://www.gnu.org/licenses/>.

 * C:E********************************************************************** */
#pragma once
#include <vector>
#include <functional>
using namespace std;
//
#include "DtaStructures.h"
#include "DtaResponse.h"
#include "DtaDrive.h"

class DtaCommand;
class DtaSession;

/* C:B**************************************************************************
 This software is Copyright (c) 2014-2024 Bright Plaza Inc. <drivetrust@drivetrust.com>

 This file is part of sedutil.

 sedutil is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 sedutil is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with sedutil.  If not, see <http://www.gnu.org/licenses/>.

 * C:E********************************************************************** */
#pragma once


/** Base class for a storage device.
 * This is a virtual base class defining the minimum functionality of storage device
 * object.  The methods defined here are called by other parts of the program
 * so must be present in all devices
 */
class DtaDev {
public:
    /** Default constructor, does nothing */
    DtaDev();
    /** Default destructor, does nothing*/
    virtual ~DtaDev();

    /** Factory method to produce instance of appropriate subclass
     * @param devref                         name of the device in the OS lexicon
     * @param pdev                          reference into which to store the address of the new instance
     * @param genericIfNotTPer   if true, store an instance of DtaDevGeneric for non-TPers;
     *                          if false, store NULL for non-TPers
     */
    static uint8_t getDtaDev(const char * devref, DtaDev * & pdev,
                             bool genericIfNotTPer=false);

    /** Does the device conform to FIPS reqs */
    uint8_t isFIPS();
    /** Does the device conform to the RUBY SSC */
    uint8_t isRuby();
    /** Does the device conform to the OPALITE SSC */
    uint8_t isOpalite();
    /** Does the device conform to the PYRITE SSC */
    uint8_t isPyrite();
    uint8_t isPyrite2();
    uint8_t isOpal2_minor_v(); /* OPAL 2 subversion */
    uint8_t isOpal2_version(); /* descriptor version */
    /** Does the device conform to the OPAL 2.0 SSC */
    uint8_t isOpal2();
    /** Does the device conform to the OPAL 1.0 SSC */
    uint8_t isOpal1();
    /** Does the device conform to the OPAL Enterprise SSC */
    uint8_t isEprise();
    /** Does the device conform to ANY TCG storage SSC */
    uint8_t isAnySSC();
    /** Is the MBREnabled flag set */
    uint8_t MBREnabled();
    /** Is the MBRDone flag set */
    uint8_t MBRDone();
    /** Is the Locked flag set */
    uint8_t Locked();
    /** Is the Locking SP enabled */
    uint8_t LockingEnabled();
    /** Is there an OS disk represented by this object */
    uint8_t isPresent();
    /** Is device on NVME bus */
    uint8_t isNVMEbus();
    /** Returns the Firmware revision reported by the identify command */
    char *getFirmwareRev();
    /** Returns the Model Number reported by the Identify command */
    char *getModelNum();
    /** Returns the Serial Number reported by the Identify command */
    char *getSerialNum();
    /** Returns the device-specific data to be used as a password salt */
    vector<uint8_t>getPasswordSalt();
    /** Returns the Vendor ID reported by the Identify command */
    char *getVendorID();
    /** Returns the Manufacturer Name reported by the Identify command */
    char *getManufacturerName();
    /** Returns the World Wide Name reported by the Identify command */
    vector<uint8_t>getWorldWideName();
    /** Returns whether the World Wide Name was synthesized from the Manufacturer Name and Serial Number */
    bool isWorldWideNameSynthetic();


    /* What type of disk attachment is used */
    DTA_DEVICE_TYPE getDevType();
    /** displays the information returned by the Discovery 0 reply */
    virtual void puke();
    //
    int TperReset();
    /*
     * virtual methods required in the OS specific
     * device class
     */
    /** OS specific method to send an ATA command to the device
     * @param cmd ATA command to be sent to the device
     * @param protocol security protocol to be used in the command
     * @param comID communications ID to be used
     * @param buffer input/output buffer
     * @param bufferlen length of the input/output buffer
     */
    uint8_t sendCmd(ATACOMMAND cmd, uint8_t protocol, uint16_t comID,
                    void * buffer, unsigned int bufferlen);
    /** OS specific routine to identify the device and fill out the device information struct*/
    bool identify(DTA_DEVICE_INFO& disk_info);
    /** OS specific routine to get size of the device */
    const unsigned long long getSize();
    /*
     * virtual functions required to be implemented
     * because they are called by sedutil.cpp
     */
    /** User command to prepare the device for management by sedutil.
     * Specific to the SSC that the device supports
     * @param password the password that is to be assigned to the SSC master entities
     */
    virtual uint8_t initialSetup(char * password) = 0;
    /** User command to prepare the device for management by sedutil.
     * Specific to the SSC that the device supports
     *  @@param password the password that is to be assigned to the SSC master entities
     */
    virtual uint8_t multiUserSetup(char *) __unimplemented__;
    /** User command to prepare the drive for Single User Mode and rekey a SUM locking range.
     * @param lockingrange locking range number to enable
     * @param start LBA to start locking range
     * @param length length (in blocks) for locking range
     * @param Admin1Password admin1 password for TPer
     * @param password User password to set for locking range
     */
    virtual uint8_t setup_SUM(uint8_t lockingrange, uint64_t start, uint64_t length, char *Admin1Password, char * password) = 0;
    /** Set the SID password.
     * Requires special handling because password is not always hashed.
     * @param oldpassword  current SID password
     * @param newpassword  value password is to be changed to
     * @param hasholdpwd  is the old password to be hashed before being added to the bytestream
     * @param hashnewpwd  is the new password to be hashed before being added to the bytestream
     */
    virtual uint8_t setSIDPassword(char * oldpassword, char * newpassword,
                                   uint8_t hasholdpwd = 1, uint8_t hashnewpwd = 1) = 0;
    /** Set the password of a locking SP user.
     * @param password  current password
     * @param userid the userid whose password is to be changed
     * @param newpassword  value password is to be changed to
     */
    virtual uint8_t setPassword(char * password, char * userid, char * newpassword, uint8_t idx=0) = 0;

    /** Set the password of a locking SP user in Single User Mode.
     * @param password  current user password
     * @param userid the userid whose password is to be changed
     * @param newpassword  value password is to be changed to
     */
    virtual uint8_t setNewPassword_SUM(char * password, char * userid, char * newpassword) = 0;
    virtual uint8_t activate(char * password) = 0;
    virtual uint8_t getmfgstate(void) = 0;
    /** Loads a disk image file to the shadow MBR table.
     * @param password the password for the administrative authority with access to the table
     * @param filename the filename of the disk image
     */
    virtual uint8_t loadPBA(char * password, char * filename) = 0;
    /** Change the locking state of a locking range
     * @param lockingrange The number of the locking range (0 = global)
     * @param lockingstate  the locking state to set
     * @param Admin1Password password of administrative authority for locking range
     */
    virtual uint8_t setLockingRange(uint8_t lockingrange, uint8_t lockingstate, char * Admin1Password, uint8_t idx=0) = 0;
    /** Change the locking state of a locking range in Single User Mode
     * @param lockingrange The number of the locking range (0 = global)
     * @param lockingstate  the locking state to set
     * @param password password of user authority for the locking range
     */
    virtual uint8_t setLockingRange_SUM(uint8_t lockingrange, uint8_t lockingstate,
                                        char * password) = 0;
    /** Change the active state of a locking range
     * @param lockingrange The number of the locking range (0 = global)
     * @param enabled  enable (true) or disable (false) the lockingrange
     * @param password Password of administrative authority for locking range
     */
    virtual uint8_t configureLockingRange(uint8_t lockingrange, uint8_t enabled,
                                          char * password, uint8_t idx=0) = 0;
    /** Setup a locking range.  Initialize a locking range, set it's start
     *  LBA and length, initialize it as unlocked with locking disabled.
     *  @paran lockingrange The Locking Range to be setup
     *  @param start  Starting LBA
     *  @param length Number of blocks
     *  @param password Password of administrator
     */
    virtual uint8_t setupLockingRange(uint8_t lockingrange, uint64_t start,
                                      uint64_t length, char * password) = 0;
    /** Setup a locking range in Single User Mode.  Initialize a locking range,
     *  set it's start LBA and length, initialize it as unlocked with locking enabled.
     *  @paran lockingrange The Locking Range to be setup
     *  @param start  Starting LBA
     *  @param length Number of blocks
     *  @param password Password of administrator
     */
    virtual uint8_t setupLockingRange_SUM(uint8_t lockingrange, uint64_t start,
                                          uint64_t length, char * password) = 0;
    /** List status of locking ranges.
     *  @param password Password of administrator
     */
    virtual uint8_t listLockingRanges(char * password, int16_t rangeid, uint8_t idx=0) = 0;
    /** Generate a new encryption key for a locking range.
     * @param lockingrange locking range number
     * @param password password of the locking sp administrative authority
     */
    virtual uint8_t rekeyLockingRange(uint8_t lockingrange, char * password) = 0;
    /** Enable bands using MSID.
     * @param rangeid locking range number
     */
    virtual uint8_t setBandsEnabled(int16_t rangeid, char * password) = 0;
    /** Primitive to set the MBRDone flag.
     * @param state 0 or 1
     * @param Admin1Password  password of the locking sp administrative authority
     */
    virtual uint8_t setMBRDone(uint8_t state, char * Admin1Password) = 0;


    virtual uint8_t TCGreset(uint8_t state) = 0;


    /** Primitive to set the MBREnable flag.
     * @param state 0 or 1
     * @param Admin1Password  password of the locking sp administrative authority
     */
    virtual uint8_t setMBREnable(uint8_t state, char * Admin1Password) = 0;

    /** enable a locking sp user.
     * @param state 0 or 1
     * @param password password of locking sp administrative authority
     * @param userid  the user to be enabled
     */
    virtual uint8_t enableUser(uint8_t state, char * password, char * userid) = 0;
    /** Enable locking on the device
     * @param state 0 or 1
     * @param password password of the admin sp SID authority
     */
    virtual uint8_t enableUserRead(uint8_t state, char * password, char * userid) = 0;

    /** Enable locking on the device
     * @param password password of the admin sp SID authority
     */
    virtual uint8_t activateLockingSP(char * password) = 0;

    /** Enable locking on the device
     * @param HostChallenge HostChallenge of the admin sp SID authority
     */
    virtual uint8_t activateLockingSP(vector<uint8_t>HostChallenge) = 0;

    /** Enable locking on the device in Single User Mode
     * @param lockingrange the locking range number to activate in SUM
     * @param password password of the admin sp SID authority
     */
    virtual uint8_t activateLockingSP_SUM(uint8_t lockingrange, char * password) = 0;
    /** Erase a Single User Mode locking range by calling the drive's erase method
     * @param lockingrange The Locking Range to erase
     * @param password The administrator password for the drive
     */
    virtual uint8_t eraseLockingRange_SUM(uint8_t lockingrange, char * password) = 0;
    /** Change the SID password from it's MSID default
     * @param newpassword  new password for SID and locking SP admins
     */
    virtual uint8_t takeOwnership(char * newpassword) = 0;

    /** Reset the Locking SP to its factory default condition
     * ERASES ALL DATA!
     * @param password of Administrative user
     * @param keep true false for noerase function NOT WWORKING
     */
    virtual uint8_t revertLockingSP(char * password, uint8_t keep = 0) = 0;

    /** Reset the TPER to its factory condition
     * @param password password of authority (SID or PSID)
     * @param PSID true or false is the authority the PSID
     * @param AdminSP true or false is the SP the AdminSP or ThisSP (Enterprise Only)
     */
    virtual uint8_t revertTPer(char * password, uint8_t PSID = 0, uint8_t AdminSP = 0 ) = 0;

    /** Erase a locking range
     * @param lockingrange The number of the locking range (0 = global)
     * @param password Password of administrative authority for locking range
     */
    virtual uint8_t eraseLockingRange(uint8_t lockingrange, char * password) = 0;
    /** Dumps an object for diagnostic purposes
     * @param sp index into the OPALUID table for the SP the object is in
     * @param auth the authority ti use for the dump
     * @param pass the password for the suthority
     * @param objID the UID of the object to dump
     */
    virtual uint8_t objDump(char *sp, char * auth, char *pass,
                            char * objID) = 0;
    /** Issue any command to the drive for diagnostic purposes
     * @param sp index into the OPALUID table for the SP the object is in
     * @param auth the authority ti use for the dump
     * @param pass the password for the suthority
     * @param invoker caller of the method
     * @param method the method to call
     * @param plist  the parameter list for the command
     */
    virtual uint8_t rawCmd(char *sp, char * auth, char *pass,
                           char *invoker, char *method, char *plist) = 0;


    /** Primitive to extract the MSID into a std::string
     * @param MSID the string to receive the MSID
     */
    virtual uint8_t getMSID(string& MSID) = 0;

    /** Primitive to print the MSID to stdout
     */
    virtual uint8_t printDefaultPassword() = 0;

    /// The methods below are slightly lower-level versions of the similarly-named ones above.
    ///   They differ in that they take a byte vector host challenge that is passed through
    ///   unchanged, i.e. not a null-terminated C string, and not (possibly) hashed.

    /** User command to manipulate the state of a locking range.
     * RW|RO|LK are the supported states @see OPAL_LOCKINGSTATE
     * @param lockingrange locking range number
     * @param lockingstate desired locking state (see above)
     * @param Admin1HostChallenge  host challenge -- unsalted password of the locking administrative authority
     */
    virtual uint8_t setLockingRange(uint8_t lockingrange, uint8_t lockingstate,
                                    vector<uint8_t> Admin1HostChallenge, uint8_t idx=0)=0;

    /** Primitive to set the MBRDone flag.
     * @param state 0 or 1
     * @param Admin1HostChallenge  host challenge -- unsalted password of the locking administrative authority
     */
    virtual uint8_t setMBRDone(uint8_t state, vector<uint8_t> Admin1HostChallenge) = 0;


    /** User command to prepare the device for management by sedutil.
     * Specific to the SSC that the device supports
     * @param HostChallenge the HostChallenge that is to be assigned to the SSC master entities
     */
    virtual uint8_t initialSetup(vector<uint8_t> HostChallenge) = 0;

    /** User command to prepare the device for management by sedutil.
     * Specific to the SSC that the device supports
     * @@param hostChallenge the password that is to be assigned to the SSC master entities
     */
    virtual uint8_t multiUserSetup(vector<uint8_t>) __unimplemented__;

    /** Change the SID HostChallenge from its MSID default
     * @param HostChallenge  new HostChallenge for SID and locking SP admins
     */
    virtual uint8_t takeOwnership(vector<uint8_t> HostChallenge) = 0;
    /** Change the active state of a locking range
     * @param lockingrange The number of the locking range (0 = global)
     * @param enabled  enable (true) or disable (false) the lockingrange
     * @param HostChallenge  HostChallenge of administrative authority for locking range
     */
    virtual uint8_t configureLockingRange(uint8_t lockingrange, uint8_t enabled,
                                          vector<uint8_t> HostChallenge, uint8_t idx=0) = 0;

    /** Set the SID password.
     * @param oldHostChallenge  current SID host challenge
     * @param newHostChallenge  value host challenge is to be changed to
     * @note neither value is hashed
     */
    virtual uint8_t setSIDHostChallenge(vector<uint8_t> oldHostChallenge,
                                        vector<uint8_t> newHostChallenge) = 0;

    /** Primitive to set the MBREnable flag.
     * @param state 0 or 1
     * @param Admin1HostChallenge  host challenge -- unsalted password of the locking administrative authority
     */
    virtual uint8_t setMBREnable(uint8_t state, vector<uint8_t> Admin1HostChallenge) = 0;

    /** Set the host challenge of a locking SP user.
     *   Note that the version above of this method is called setPassword
     * @param currentHostChallenge  current host challenge
     * @param userid the userid whose host challenge is to be changed
     * @param newHostChallenge  value  host challenge is to be changed to
     */
    virtual uint8_t setHostChallenge(vector<uint8_t> currentHostChallenge, char * userid,
                                     vector<uint8_t> newHostChallenge, uint8_t idx=0) = 0;


    /** enable a locking sp user.
     * @param state 0 or 1
     * @param HostChallenge HostChallenge of locking sp administrative authority
     * @param userid  the user to be enabled
     */
    virtual uint8_t enableUser(uint8_t state, vector<uint8_t> HostChallenge, char * userid) = 0;

    /** Enable locking on the device
     * @param state 0 or 1
     * @param HostChallenge HostChallenge of the admin sp SID authority
     */
    virtual uint8_t enableUserRead(uint8_t state, vector<uint8_t> HostChallenge, char * userid) = 0;

    /** Reset the Locking SP to its factory default condition
     * ERASES ALL DATA!
     * @param HostChallenge of Administrative user
     * @param keep true false for noerase function NOT WWORKING
     */
    virtual uint8_t revertLockingSP(vector<uint8_t> HostChallenge, uint8_t keep = 0) = 0;

    /** Reset the TPER to its factory condition
     * @param HostChallenge HostChallenge of authority (SID or PSID)
     * @param PSID true or false is the authority the PSID
     * @param AdminSP true or false is the SP the AdminSP or ThisSP (Enterprise Only)
     */
    virtual uint8_t revertTPer(vector<uint8_t> HostChallenge, uint8_t PSID = 0, uint8_t AdminSP = 0 ) = 0;



    /// Wrapper methods that allow concise TPer function methods

    /** Start a session using some kind of authentication, and
     * then do something within that session.
     * This method handles errors starting the session, and cleans
     * up by deleting the session afterwards,
     * returning the result of any session start error
     * or otherwise the result of the session body function
     *
     * Note that it is expected that these "function" parameters
     * will probably be closures.
     *
     * @param startSessionFn a function that starts a session, returning a uint8_t
     * @param sessionBodyFn a function that runs within that session, returning a uint8_t
     */
    uint8_t WithSession(std::function<uint8_t(void)>startSessionFn,
                        std::function<uint8_t(void)>sessionBodyFn);

    /** Start a session using a simple start method call, and
     * then do something within that session.
     * This method handles errors starting the session, and cleans
     * up by deleting the session afterwards,
     * returning the result of any session start error
     * or otherwise the result of the session body function
     *
     * Note that it is expected that these "function" parameters
     * will probably be closures.
     *
     * @param SP the securitly provider to start the session with
     * @param password the password to start the session
     * @param SignAuthority the Signing authority (in a simple session this is the user)
     * @param sessionBodyFn a function that runs within that session, returning a uint8_t
     */
    template <typename PasswordType, typename AuthorityType>
    uint8_t WithSimpleSession(OPAL_UID SP, PasswordType password, AuthorityType SignAuthority,
                              std::function<uint8_t(void)>sessionBodyFn) {
        std::function<uint8_t(void)>startSessionFn = [this, SP, password, SignAuthority](){
            return start(SP, password, SignAuthority);
        };
        return WithSession(startSessionFn, sessionBodyFn);
    }


    /** Start a session using some kind of authentication,
     * create a DtaCommand object, and then run that command within that session.
     * This method handles errors starting the session and creating the command,
     * and cleans up by deleting the command and session afterwards,
     * returning the result of any session start error
     * or command creation error
     * or otherwise the result of executing sendCommand on the command
     * leaving the response in the response instance variable
     *
     * Note that it is expected that these "function" parameters
     * will probably be closures.
     *
     * @param startSessionFn a function that starts a session, returning a uint8_t
     * @param commandWriterFn a function that runs within that session,
     *                       takes a DtaCommand parameter,
     *                       and writes into that DtaCommand
     *                       and then simply returns no value
     */


    uint8_t WithSessionCommand(std::function<uint8_t(void)>startSessionFn,
                               std::function<void(DtaCommand * command)>commandWriterFn);


    /** Start a session using a simple start method call,
     * create a DtaCommand object, and then run that command within that session.
     * This method handles errors starting the session and creating the command,
     * and cleans up by deleting the command and session afterwards,
     * returning the result of any session start error
     * or command creation error
     * or otherwise the result of executing sendCommand on the command
     * leaving the response in the response instance variable
     *
     * Note that it is expected that these "function" parameters
     * will probably be closures.
     *
     * @param SP the securitly provider to start the session with
     * @param password the password to start the session
     * @param SignAuthority the Signing authority (in a simple session this is the user)
     * @param commandWriterFn a function that runs within that session,
     *                       takes a DtaCommand parameter,
     *                       and writes into that DtaCommand
     *                       and then simply returns no value
     */
    template <typename PasswordType, typename AuthorityType>
    uint8_t WithSimpleSessionCommand(OPAL_UID SP, PasswordType password, AuthorityType SignAuthority,
                                     std::function<void(DtaCommand * command)>commandWriterFn) {
        std::function<uint8_t(void)>startSessionFn = [this, SP, password, SignAuthority](){
            return start(SP, password, SignAuthority);
        };
        return WithSessionCommand(startSessionFn, commandWriterFn);
    }


    /**
     * virtual functions required to be implemented
     * because they are called by DtaSession.cpp
     */

    /** Send a command to the device and wait for the response
     * @param cmd the MswdCommand object containing the command
     * @param response the DtaResonse object containing the response
     * @param protocol The security protocol number to use for the command
     */
    virtual uint8_t exec(DtaCommand * cmd, DtaResponse & response, uint8_t protocol = 0x01) = 0;
    /** return the communications ID to be used for sessions to this device */
    virtual uint16_t comID() = 0;

    bool no_hash_passwords = FALSE; /** disables hashing of passwords */
    bool usermodeON = FALSE;
    bool translate_req = FALSE;
    bool skip_activate = FALSE;

protected:
    const char * dev;   /**< character string representing the device in the OS lexicon */
    DTA_DEVICE_INFO device_info;  /**< Structure containing info from identify and discovery 0 */

    uint8_t isOpen = FALSE;  /**< The device has been opened */
    uint8_t isNVME = FALSE;  /**< This device is NVME */

    uint8_t adj_host = FALSE;
    uint16_t adj_io_buffer_length = 2048; // 10240; // 17408; // user safe low buffer length

    DtaResponse response;   /**< shared response object */
    DtaResponse propertiesResponse;  /**< response from properties exchange */
    DtaSession *session;  /**< shared session object pointer */

    /** start an anonymous session
     * @param SP the Security Provider to start the session with */
    uint8_t start(OPAL_UID SP);


    /** Start an authenticated session (OPAL only)
     * @param SP the securitly provider to start the session with
     * @param password the password to start the session
     * @param SignAuthority the Signing authority (in a simple session this is the user)
     */
    uint8_t start(OPAL_UID SP, char * password, OPAL_UID SignAuthority);



    /** Start an authenticated session (OPAL only)
     * @param SP the securitly provider to start the session with
     * @param HostChallenge the password to start the session
     * @param SignAuthority the Signing authority (in a simple session this is the user)
     */
    uint8_t start(OPAL_UID SP, vector<uint8_t> HostChallenge, OPAL_UID SignAuthority);


    /** Start an authenticated session (OPAL only)
     * @param SP the securitly provider to start the session with
     * @param password the password to start the session
     * @param SignAuthority the Signing authority (in a simple session this is the user)
     *  */
    uint8_t start(OPAL_UID SP, char * password, vector<uint8_t> SignAuthority);


    /** Start an authenticated session (OPAL only)
     * @param SP the securitly provider to start the session with
     * @param HostChallenge the password to start the session
     * @param SignAuthority the Signing authority (in a simple session this is the user)
     *  */
    uint8_t start(OPAL_UID SP, vector<uint8_t>  HostChallenge, vector<uint8_t> SignAuthority);



    uint8_t discovery0buffer[MIN_BUFFER_LENGTH + IO_BUFFER_ALIGNMENT] = { 0 }; // NG->__attribute__((aligned(16)));

    uint32_t Tper_sz_MaxComPacketSize = 2048;
    uint32_t Tper_sz_MaxResponseComPacketSize = 2048;
    uint32_t Tper_sz_MaxPacketSize = 2028;
    uint32_t Tper_sz_MaxIndTokenSize = 1992;
    uint32_t Host_sz_MaxComPacketSize = 2048;
    uint32_t Host_sz_MaxResponseComPacketSize = 2048;
    uint32_t Host_sz_MaxPacketSize = 2028 ;
    uint32_t Host_sz_MaxIndTokenSize = 1992 ;

public:


    /** Factory method to produce instance of appropriate subclass
     *   Note that all of DtaDevGeneric, DtaDevEnterprise, DtaDevOpal, ... derive from DtaDev
     * @param devref             name of the device in the OS lexicon
     * @param pdev                pointer to location into which to store the address of the new instance
     * @param genericIfNotTPer   if true, store an instance of DtaDevGeneric for non-TPers;
     *                          if false, store NULL for non-TPers
     */
    static uint8_t getDtaDev(const char * devref,
                             DtaDev * * pdev,
                             bool genericIfNotTPer=false);





    /** A static function to scan for supported drives */
    static uint8_t diskScan();

    /** Short-circuit routine re-uses initialized drive and disk_info */
    DtaDev(const char * devref, DtaDrive * drv, DTA_DEVICE_INFO & di)
    : drive(drv)
    {dev=devref; device_info=di; drive=drv; isOpen=(drv!=NULL && drv->isOpen());};

protected:
    /** Minimal internal type-switching routine
     *
     *  Checks that the drive responds to discovery0.
     *  Assumes all the identify/discovery0 information is thus in di,
     *  and that drive has a file descriptor open on devref.
     *  Just tests di SSC bits and picks DtaDev subclass accordingly.
     *  Otherwise return NULL, or
     *  a DtaDevGeneric instance if genericIfNotTper is true.
     */
    static DtaDev* getDtaDev(const char * devref,
                             DtaDrive * drive,
                             DTA_DEVICE_INFO & di,
                             bool genericIfNotTPer=false);


private:
    /* Protocol-specific subclass instance -- Nvme, Scsi, Sata, ... */
    DtaDrive *drive;

    // /** Default constructor */
    // DtaDev()
    //   : drive(NULL)
    // { dev=NULL;
    //   isOpen=FALSE;
    //   memset(&disk_info, 0, sizeof(disk_info));
    //   assert(FALSE);  // ***TODO*** this is never used
    // };


};


static inline void set8(std::vector<uint8_t> & v, const uint8_t value[8])
{
    v.clear();
    v.push_back(OPAL_SHORT_ATOM::BYTESTRING8);
    for (int i = 0; i < 8; i++)
    {
        v.push_back(value[i]);
    }
}



static inline std::vector<uint8_t> vUID(OPAL_UID uid)
{
    std::vector<uint8_t> v(9);
    set8(v,OPALUID[uid]);
    return v;
}

extern std::vector<uint8_t> getUID(char * userid, std::vector<uint8_t> &auth2, std::vector<uint8_t> &auth3, uint8_t hu);




// from DtaHashPwd.cpp
// credit
// https://www.codeproject.com/articles/99547/hex-strings-to-raw-data-and-back
//

inline unsigned char hex_digit_to_nybble(char ch)
{
  switch (ch)
    {
    case '0': return 0x0;
    case '1': return 0x1;
    case '2': return 0x2;
    case '3': return 0x3;
    case '4': return 0x4;
    case '5': return 0x5;
    case '6': return 0x6;
    case '7': return 0x7;
    case '8': return 0x8;
    case '9': return 0x9;
    case 'a': return 0xa;
    case 'A': return 0xa;
    case 'b': return 0xb;
    case 'B': return 0xb;
    case 'c': return 0xc;
    case 'C': return 0xc;
    case 'd': return 0xd;
    case 'D': return 0xd;
    case 'e': return 0xe;
    case 'E': return 0xe;
    case 'f': return 0xf;
    case 'F': return 0xf;
    default: return 0xff;  // throw invalid_argument();
    }
}
