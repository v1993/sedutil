/* C:B**************************************************************************
This software is Copyright 2014, 2022 Bright Plaza Inc. <drivetrust@drivetrust.com>

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
#if !defined(__DTA_LEXICON__H_INCLUDED__)
#defined __DTA_LEXICON__H_INCLUDED__
/*
 * Define the structures and enums needed to map the
 * Opal SSC Pseudo code to procedures.
 *
 * no effort has been made to be complete, these are the values
 * that are required for the basic functionality provided in this
 * program.
 */

/** User IDs used in the TCG storage SSCs */
static const uint8_t OPALUID[][8]={
  // users
  { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff}, /**< session management  */
  { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 }, /**< special "thisSP" syntax */
  { 0x00, 0x00, 0x02, 0x05, 0x00, 0x00, 0x00, 0x01 }, /**< Administrative SP */
  { 0x00, 0x00, 0x02, 0x05, 0x00, 0x00, 0x00, 0x02 }, /**< Locking SP */
  { 0x00, 0x00, 0x02, 0x05, 0x00, 0x01, 0x00, 0x01 }, /**< ENTERPRISE Locking SP  */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00, 0x01 }, /**<anybody */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00, 0x06 }, /**< SID */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x01 }, /**< ADMIN1 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x02 }, /**< ADMIN2 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x03 }, /**< ADMIN3 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x04 }, /**< ADMIN4 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x05 }, /**< ADMIN5 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x06 }, /**< ADMIN6 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x07 }, /**< ADMIN7 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x08 }, /**< ADMIN8 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x00, 0x09 }, /**< ADMIN9 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x01 }, /**< USER1 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x02 }, /**< USER2 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x03 }, /**< USER3 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x04 }, /**< USER4 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x05 }, /**< USER5 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x06 }, /**< USER6 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x07 }, /**< USER7 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x08 }, /**< USER8 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x09 }, /**< USER9 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x0A }, /**< USER10 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x0B }, /**< USER11 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x0C }, /**< USER12 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x0D }, /**< USER13 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x0E }, /**< USER14 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x0F }, /**< USER15 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x10 }, /**< USER16 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x11 }, /**< USER17 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x12 }, /**< USER18 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x13 }, /**< USER19 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x14 }, /**< USER20 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x15 }, /**< USER21 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x16 }, /**< USER22 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x17 }, /**< USER23 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x18 }, /**< USER24 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x19 }, /**< USER25 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x1A }, /**< USER26 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x1B }, /**< USER27 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x1C }, /**< USER28 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x1D }, /**< USER29 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x1E }, /**< USER30 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x1F }, /**< USER31 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x20 }, /**< USER32 */

  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0xff, 0x01 }, /**< PSID user */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x80, 0x01 }, /**< BandMaster 0 */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x84, 0x01 }, /**< EraseMaster */
    // tables
  { 0x00, 0x00, 0x08, 0x02, 0x00, 0x00, 0x00, 0x01 }, /**< Locking_GlobalRange (23) */

  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xE0, 0x01 }, /**< UID ACE_Locking_Range_Set_RdLocked LKRNG0*/

  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xE8, 0x01 }, /**< UID ACE_Locking_Range_Set_WrLocked LKRNG0*/

  { 0x00, 0x00, 0x08, 0x03, 0x00, 0x00, 0x00, 0x01 }, /**< MBR Control Done flag */


  { 0x00, 0x00, 0x08, 0x04, 0x00, 0x00, 0x00, 0x00 }, /**< Shadow MBR */
  { 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00, 0x00 }, /**< AUTHORITY_TABLE */
  { 0x00, 0x00, 0x00, 0x0B, 0x00, 0x00, 0x00, 0x00 }, /**< C_PIN_TABLE */
  { 0x00, 0x00, 0x08, 0x01, 0x00, 0x00, 0x00, 0x01 }, /**< OPAL Locking Info (30) */
  { 0x00, 0x00, 0x08, 0x01, 0x00, 0x00, 0x00, 0x00 }, /**< Enterprise Locking Info */
    //C_PIN_TABLE object ID's
  { 0x00, 0x00, 0x00, 0x0B, 0x00, 0x00, 0x84, 0x02}, /**< C_PIN_MSID */
  { 0x00, 0x00, 0x00, 0x0B, 0x00, 0x00, 0x00, 0x01}, /**< C_PIN_SID */
  { 0x00, 0x00, 0x00, 0x0B, 0x00, 0x01, 0x00, 0x01}, /**< C_PIN_ADMIN1 */
  { 0x00, 0x00, 0x00, 0x0B, 0x00, 0x03, 0x00, 0x01}, /**< C_PIN_USER1 */
    //half UID's (only first 4 bytes used)
  { 0x00, 0x00, 0x0C, 0x05, 0xff, 0xff, 0xff, 0xff}, /** Half-UID – Authority_object_ref */
  { 0x00, 0x00, 0x04, 0x0E, 0xff, 0xff, 0xff, 0xff}, /** Half-UID – Boolean ACE */
    // special value for omitted optional parameter
  { 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff}, /**< HEXFF for omitted */
  { 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x08, 0x04}, /**< Shadow MBR size */
  { 0x00, 0x00, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store  */
  { 0x00, 0x00, 0x10, 0x01, 0x00, 0x00, 0x00, 0x01 }, /**< Data Store2  */
  { 0x00, 0x00, 0x10, 0x01, 0x00, 0x00, 0x00, 0x02 }, /**< Data Store3  */
  { 0x00, 0x00, 0x10, 0x04, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store4  */
  { 0x00, 0x00, 0x10, 0x05, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store5  */
  { 0x00, 0x00, 0x10, 0x06, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store6  */
  { 0x00, 0x00, 0x10, 0x07, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store7  */
  { 0x00, 0x00, 0x10, 0x08, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store8  */
  { 0x00, 0x00, 0x10, 0x09, 0x00, 0x00, 0x00, 0x00 }, /**< Data Store9  */
  { 0x00, 0x00, 0x02, 0x01, 0x00, 0x03, 0x00, 0x01 }, /**< GUDID 12-byte  */
    // data store read authourity table
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xFC, 0x00 }, /**< UID ACE_DataStore_Get_All (49) */
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xFC, 0x01 }, /**< UID ACE_DataStore_Set_All */
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xF8, 0x01 }, /**< UID OPAL_ACE_MBRControl_Set_Done, MBRDone */

    // new table to enable user and admin access
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xF8, 0x00 }, /**< UID OPAL_ACE_MBRControl_Set_Enable, MBREnable */
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xD0, 0x00 }, /**< UID ACE_Locking_GlobalRange_Get_RangeStartToActiveKey*/

  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xE0, 0x00 }, /**< UID ACE_Locking_GlobalRange_Set_ReadLocked (54) */
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xE8, 0x00 }, /**< UID ACE_Locking_GlobalRange_Set_WriteLocked (55) */

  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xF0, 0x00 }, /**< UID ACE_Locking_GlobalRange_Admin_Set  enable locking*/
  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0xF0, 0x01 }, /**< UID ACE_Locking_GlobalRange_Admin_Start set starting and length */

  { 0x00, 0x00, 0x00, 0x08, 0x00, 0x03, 0x00, 0x03 }, /**< UID ACE_TperInfo_Set_ProgrammaticResetEnable*/
    //{ 0x00, 0x00, 0x02, 0x01, 0x00, 0x03, 0x00, 0x01 }, /* invalid parameter */
    };
/** Enum to index OPALUID array */
typedef enum _OPAL_UID {
  // users
  OPAL_SMUID_UID,
  OPAL_THISSP_UID,
  OPAL_ADMINSP_UID,
  OPAL_LOCKINGSP_UID,
  ENTERPRISE_LOCKINGSP_UID,
  OPAL_ANYBODY_UID,
  OPAL_SID_UID,
  OPAL_ADMIN1_UID,
  OPAL_ADMIN2_UID,
  OPAL_ADMIN3_UID,
  OPAL_ADMIN4_UID,
  OPAL_ADMIN5_UID, // increase to 9
  OPAL_ADMIN6_UID,
  OPAL_ADMIN7_UID,
  OPAL_ADMIN8_UID,
  OPAL_ADMIN9_UID,
  OPAL_USER1_UID,
  OPAL_USER2_UID,
  OPAL_USER3_UID,
  OPAL_USER4_UID,
  OPAL_USER5_UID,
  OPAL_USER6_UID,
  OPAL_USER7_UID,
  OPAL_USER8_UID,
  OPAL_USER9_UID,
  OPAL_USER10_UID, // increase to 32 for some lots of user
  OPAL_USER11_UID,
  OPAL_USER12_UID,
  OPAL_USER13_UID,
  OPAL_USER14_UID,
  OPAL_USER15_UID,
  OPAL_USER16_UID,
  OPAL_USER17_UID,
  OPAL_USER18_UID,
  OPAL_USER19_UID,
  OPAL_USER20_UID,
  OPAL_USER21_UID,
  OPAL_USER22_UID,
  OPAL_USER23_UID,
  OPAL_USER24_UID,
  OPAL_USER25_UID,
  OPAL_USER26_UID,
  OPAL_USER27_UID,
  OPAL_USER28_UID,
  OPAL_USER29_UID,
  OPAL_USER30_UID,
  OPAL_USER31_UID,
  OPAL_USER32_UID,

  OPAL_PSID_UID,
  ENTERPRISE_BANDMASTER0_UID,
  ENTERPRISE_ERASEMASTER_UID,
  // tables
  OPAL_LOCKINGRANGE_GLOBAL,

  OPAL_ACE_LOCKINGRANGE1_RDLOCKED,
  OPAL_LOCKINGRANGE_ACE_RDLOCKED=OPAL_ACE_LOCKINGRANGE1_RDLOCKED,
  OPAL_ACE_LOCKINGRANGE1_WRLOCKED,
  OPAL_LOCKINGRANGE_ACE_WRLOCKED=OPAL_ACE_LOCKINGRANGE1_WRLOCKED,


  OPAL_MBRControl_Set_DoneToDOR,
  OPAL_MBRCONTROL=OPAL_MBRControl_Set_DoneToDOR,

  OPAL_MBR,
  OPAL_AUTHORITY_TABLE,
  OPAL_C_PIN_TABLE,
  OPAL_LOCKING_INFO_TABLE,
  ENTERPRISE_LOCKING_INFO_TABLE,
  //C_PIN_TABLE object ID's
  OPAL_C_PIN_MSID,
  OPAL_C_PIN_SID,
  OPAL_C_PIN_ADMIN1,
  OPAL_C_PIN_USER1,
  //half UID's (only first 4 bytes used)
  OPAL_HALF_UID_AUTHORITY_OBJ_REF,
  OPAL_HALF_UID_BOOLEAN_ACE,
  // omitted optional parameter
  OPAL_UID_HEXFF,
  OPAL_MBR_SZ,
  OPAL_DATA_STORE,
  OPAL_DATA_STORE2,
  OPAL_DATA_STORE3,
  OPAL_DATA_STORE4,
  OPAL_DATA_STORE5,
  OPAL_DATA_STORE6,
  OPAL_DATA_STORE7,
  OPAL_DATA_STORE8,
  OPAL_DATA_STORE9,
  OPAL_GUDID_UID,

  OPAL_ACE_DataStore_Get_All,
  OPAL_ACE_DataStore_Set_All,
  OPAL_ACE_MBRControl_Set_Done,

  OPAL_ACE_MBRControl_Set_Enable,
  OPAL_ACE_Locking_GlobalRange_Get_RangeStartToActiveKey,

  OPAL_ACE_Locking_GlobalRange_Set_ReadLocked,
  OPAL_ACE_Locking_GlobalRange_Set_WriteLocked,

  OPAL_ACE_Locking_GlobalRange_Admin_Set,	// allow to set/reset
  OPAL_ACE_Locking_GlobalRange_Admin_Start, // allow to set/reset range start and length

  OPAL_ACE_TperInfo_Set_ProgrammaticResetEnable, //
} OPAL_UID;

/** TCG Storage SSC Methods.
 */
static const uint8_t OPALMETHOD[][8]={
  { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x01}, /**< Properties */
  { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x02}, /**<STARTSESSION */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x02, 0x02}, /**< Revert */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x02, 0x03}, /**< Activate */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x06}, /**< Enterprise Get */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x07}, /**< Enterprise Set */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x08}, /**< NEXT */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x0c}, /**< Enterprise Authenticate */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x0d}, /**< GetACL */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x10}, /**< GenKey */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x11}, /**< revertSP */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x16}, /**< Get */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x17}, /**< Set */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x1c}, /**< Authenticate */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x06, 0x01}, /**< Random */
  { 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x08, 0x03}, /**< Erase */
};
/** Enum for indexing the OPALMETHOD array */
typedef enum _OPAL_METHOD {
  PROPERTIES,
  STARTSESSION,
  REVERT,
  ACTIVATE,
  EGET,
  ESET,
  NEXT,
  EAUTHENTICATE,
  GETACL,
  GENKEY,
  REVERTSP,
  GET,
  SET,
  AUTHENTICATE,
  RANDOM,
  ERASE,
} OPAL_METHOD;

/** Opal SSC TOKENS
 * Single byte non atom tokens used in Opal SSC psuedo code
 */
typedef enum _OPAL_TOKEN {
  //Boolean
  OPAL_TRUE = 0x01,
  OPAL_FALSE = 0x00,
  OPAL_BOOLEAN_EXPR = 0x03,
  // cellblocks
  TABLE = 0x00,
  STARTROW = 0x01,
  ENDROW = 0x02,
  STARTCOLUMN = 0x03,
  ENDCOLUMN = 0x04,
  VALUES = 0x01,
  LOCKONRESETCOLUMN = 0x09,
  LOCKONRESETVALUE = 0x03,
  TPERRESETENABLECOLUMN = 0x08,
  TPERRESETENABLEVALUE = 0x01, // TRUE=0, FALSE=0
  // authority table
  PIN = 0x03,
  TryLimit = 0x05,
  Tries = 0x06,
  // locking tokens
  RANGESTART = 0x03,
  RANGELENGTH = 0x04,
  READLOCKENABLED = 0x05,
  WRITELOCKENABLED = 0x06,
  READLOCKED = 0x07,
  WRITELOCKED = 0x08,
  ACTIVEKEY = 0x0A,
  //locking info table
  MAXRANGES = 0x04,
  // mbr control
  MBRENABLE = 0x01,
  MBRDONE = 0x02,
  // properties
  HOSTPROPERTIES =0x00,
  // response tokenis() returned values
  DTA_TOKENID_BYTESTRING = 0xe0,
  DTA_TOKENID_SINT = 0xe1,
  DTA_TOKENID_UINT = 0xe2,
  DTA_TOKENID_TOKEN = 0xe3, // actual token is returned
  // atoms
  STARTLIST = 0xf0,
  ENDLIST = 0xf1,
  STARTNAME = 0xf2,
  ENDNAME = 0xf3,
  CALL = 0xf8,
  ENDOFDATA = 0xf9,
  ENDOFSESSION = 0xfa,
  STARTTRANSACTON = 0xfb,
  ENDTRANSACTON = 0xfC,
  EMPTYATOM = 0xff,
  WHERE = 0x00,
} OPAL_TOKEN;

/** Useful tiny atoms.
 * Useful for table columns etc
 */
typedef enum _OPAL_TINY_ATOM {
  UINT_00 = 0x00,
  UINT_01 = 0x01,
  UINT_02 = 0x02,
  UINT_03 = 0x03,
  UINT_04 = 0x04,
  UINT_05 = 0x05,
  UINT_06 = 0x06,
  UINT_07 = 0x07,
  UINT_08 = 0x08,
  UINT_09 = 0x09,
  UINT_10 = 0x0a,
  UINT_11 = 0x0b,
  UINT_12 = 0x0c,
  UINT_13 = 0x0d,
  UINT_14 = 0x0e,
  UINT_15 = 0x0f,
} OPAL_TINY_ATOM;

/** Useful short atoms.
 */
typedef enum _OPAL_SHORT_ATOM {
  UINT_3 = 0x83,
  BYTESTRING4 = 0xa4,
  BYTESTRING8 = 0xa8,
} OPAL_SHORT_ATOM;
/** Locking state for a locking range */
typedef enum _OPAL_LOCKINGSTATE {
  READWRITE = 0x01,
  READONLY = 0x02,
  LOCKED = 0x03,
  ARCHIVELOCKED = 0x04,
  ARCHIVEUNLOCKED = 0x05,
} OPAL_LOCKINGSTATE;
/*
 * Structures to build and decode the Opal SSC messages
 * fields that are NOT really numeric are defined as uint8_t[] to
 * help reduce the endianess issues
 */

/** method status codes.
 */
typedef enum _OPALSTATUSCODE {
  SUCCESS = 0x00,
  NOT_AUTHORIZED = 0x01,
  //	OBSOLETE = 0x02,
  SP_BUSY = 0x03,
  SP_FAILED = 0x04,
  SP_DISABLED = 0x05,
  SP_FROZEN = 0x06,
  NO_SESSIONS_AVAILABLE = 0x07,
  UNIQUENESS_CONFLICT = 0x08,
  INSUFFICIENT_SPACE = 0x09,
  INSUFFICIENT_ROWS = 0x0A,
  INVALID_FUNCTION = 0x0B, // defined in early specs, still used in some firmware
  INVALID_PARAMETER = 0x0C,
  INVALID_REFERENCE = 0x0D,
  //	OBSOLETE = 0x0E,
  TPER_MALFUNCTION = 0x0F,
  TRANSACTION_FAILURE = 0x10,
  RESPONSE_OVERFLOW = 0x11,
  AUTHORITY_LOCKED_OUT = 0x12,
  FAIL = 0x3f,
} OPALSTATUSCODE;

#endif //!defined(__DTA_LEXICON__H_INCLUDED__)
