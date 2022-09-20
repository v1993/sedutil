/* C:B**************************************************************************
This software is Copyright 2014-2016 Bright Plaza Inc. <drivetrust@drivetrust.com>

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
#include "os.h"
#include <stdio.h>
#include <iostream>
#pragma warning(push)
#pragma warning(disable : 4091)
#include <Ntddscsi.h>
#include <Ntddstor.h>
#pragma warning(pop)
#include <vector>
#include "DtaDiskNVME.h"
#include "DtaEndianFixup.h"
#include "DtaStructures.h"
#include "DtaHexDump.h"
#include "nvme.h"
#include "fips.h""
//#include "nvmeIoctl.h"

///////////////////////////////////////////////////////////////////////////////////////
// issue STORAGE_QUERY

typedef struct _STORAGE_PROPERTY_QUERYA {

	//
	// ID of the property being retrieved
	//

	STORAGE_PROPERTY_ID PropertyId;

	//
	// Flags indicating the type of query being performed
	//

	STORAGE_QUERY_TYPE QueryType;

	//
	// Space for additional parameters if necessary
	//

	//BYTE  AdditionalParameters[1]; // JERRY this additional byte cause DeviceIoControl fail

} STORAGE_PROPERTY_QUERYA, *PSTORAGE_PROPERTY_QUERYA;


	typedef struct {
		STORAGE_PROPERTY_QUERYA Query;
		STORAGE_PROTOCOL_SPECIFIC_DATA ProtocolSpecific;
		BYTE Buffer[IO_BUFFER_LENGTH];
	} StorageQueryWithBuffer, * PStorageQueryWithBuffer;

DWORD GetIDFY(HANDLE hDev, PStorageQueryWithBuffer Qry);
DWORD GetIDFY(HANDLE hDev, PStorageQueryWithBuffer Qry)
{
	LOG(D1) << "Enter GetIDFY";
	DWORD dwRet = NO_ERROR;
	BOOL bRet = 0;
	LOG(D1) << "sizeof(enum) " << sizeof(STORAGE_QUERY_TYPE);
	LOG(D1) << "sizeof(STORAGE_PROPERTY_QUERY) " << sizeof(STORAGE_PROPERTY_QUERY);
	LOG(D1) << "sizeof(STORAGE_PROPERTY_QUERYA) " << sizeof(STORAGE_PROPERTY_QUERYA);
	LOG(D1) << "sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA) " << sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA);
	LOG(D1) << "sizeof(StorageQueryWithBuffer) " << sizeof(StorageQueryWithBuffer);
	memset(Qry, 0,sizeof(StorageQueryWithBuffer));
	
	LOG (D1) << "NVMeDataTypeIdentify";	
	Qry->ProtocolSpecific.ProtocolType = ProtocolTypeNvme;
	Qry->ProtocolSpecific.DataType = NVMeDataTypeIdentify;
	Qry->ProtocolSpecific.ProtocolDataOffset = sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA);
	Qry->ProtocolSpecific.ProtocolDataLength  = IO_BUFFER_LENGTH;
	Qry->ProtocolSpecific.ProtocolDataRequestValue = 1 ; // 0-511, only 1 OK other fail ;  1:0-> OK; 2:0->NG 0:0 -> NG cdw10 maybe CNS value either 0 or 1 ; cdw0 = opcode = 06
	Qry->ProtocolSpecific.ProtocolDataRequestSubValue = 0 ; // nsid 0 - 0ffffh all OK , this is don't care value
	Qry->Query.PropertyId = StorageAdapterProtocolSpecificProperty;
	Qry->Query.QueryType = PropertyStandardQuery;
	// from smartmontools project os_win32.cpp
	/*
	  spsq->ProtocolSpecific.DataType = win10::NVMeDataTypeIdentify;
      spsq->ProtocolSpecific.ProtocolDataRequestValue = in.cdw10;
      spsq->ProtocolSpecific.ProtocolDataRequestSubValue = in.nsid;
	*/
	IFLOG(D4) {
		LOG(D) << "Qry data before DeviceIoControl";
		DtaHexDump(Qry, 128);
	}
	// bRet = nonzero if ok, else 0
	DWORD dwReturned;
	bRet = DeviceIoControl(hDev, IOCTL_STORAGE_QUERY_PROPERTY,
		Qry, sizeof(StorageQueryWithBuffer), Qry, sizeof(StorageQueryWithBuffer), &dwReturned, NULL);
	if (bRet)
	{
		IFLOG(D4) {
			//dumphex(&Qry , sizeof(Qry));
			LOG(D) << "DeviceIoControl IOCTL_STORAGE_QUERY_PROPERTY OK";
			DtaHexDump(&Qry, 128);
			LOG(I) << "Qry->Buffer[IO_BUFFER_LENGTH] : ";
			DtaHexDump(Qry->Buffer, 4096); 
		}
	}
	else
	{
		dwRet = GetLastError();
		IFLOG(D4) {
			LOG(E) << "IOCTL Fail IOCTL_STORAGE_QUERY_PROPERTY error" << "error code = " << dwRet;
			DtaHexDump(&Qry, 128);
		}
		return dwRet;
	}
	LOG(D1) << "Exit GetIDFY";
	return dwRet;
}


BOOL GetScsiAddress(const TCHAR* Path, BYTE* PortNumber, BYTE* PathId, BYTE* TargetId, BYTE* Lun)
{
	HANDLE hDevice = CreateFile(Path,
		GENERIC_READ | GENERIC_WRITE,
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		nullptr,
		OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL,
		nullptr);
	DWORD dwReturned;
	SCSI_ADDRESS ScsiAddr;
	BOOL bRet = DeviceIoControl(hDevice, IOCTL_SCSI_GET_ADDRESS,
		nullptr, 0, &ScsiAddr, sizeof(ScsiAddr), &dwReturned, NULL);

	CloseHandle(hDevice);

	*PortNumber = ScsiAddr.PortNumber;
	*PathId = ScsiAddr.PathId;
	*TargetId = ScsiAddr.TargetId;
	*Lun = ScsiAddr.Lun;

	return bRet == TRUE;
}

/////  Intel RST driver use nvme pass through 
// use scsi address instead of physicaldrive
BOOL DoIdentifyDeviceNVMeIntelRst(BYTE physicalDriveId, BYTE scsiPort, BYTE scsiTargetId, IDENTIFY_DEVICE* data);
BOOL DoIdentifyDeviceNVMeIntelRst(BYTE physicalDriveId, BYTE scsiPort, BYTE scsiTargetId, IDENTIFY_DEVICE* data)
{
	//CString path;
	//path.Format(L"\\\\.\\PhysicalDrive%d", physicalDriveId);
	TCHAR path[64] = TEXT("\0");
	sprintf_s(path, "\\\\.\\PhysicalDrive%d", physicalDriveId);

	/*
	uint8_t physicalDriveId = 0;
	uint8_t scsiTargetId;
	uint8_t scsiPort;
	uint8_t lun;
	*/
	BYTE portNumber, pathId, targetId, lun;
	// translate physical address to scsi port number,
	GetScsiAddress(path, &portNumber, &pathId, &targetId, &lun);
	//CString drive;
	TCHAR drive[64] = TEXT("\0");
	
	sprintf_s(drive, TEXT("\\\\.\\Scsi%d:"), portNumber);
	// LOG(D) << "drive = " << drive ;
	
	HANDLE hIoCtrl = CreateFile(drive,
		GENERIC_READ | GENERIC_WRITE,
		FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr,
		OPEN_EXISTING, 0, nullptr);

	if (hIoCtrl != INVALID_HANDLE_VALUE)
	{
		INTEL_NVME_PASS_THROUGH NVMeData;
		memset(&NVMeData, 0, sizeof(NVMeData));

		NVMeData.SRB.HeaderLength = sizeof(SRB_IO_CONTROL);
		memcpy(NVMeData.SRB.Signature, "IntelNvm", 8);
		NVMeData.SRB.Timeout = 10;
		NVMeData.SRB.ControlCode = IOCTL_INTEL_NVME_PASS_THROUGH;
		NVMeData.SRB.Length = sizeof(INTEL_NVME_PASS_THROUGH) - sizeof(SRB_IO_CONTROL);

		NVMeData.Payload.Version = 1;
		NVMeData.Payload.PathId = pathId;
		NVMeData.Payload.Cmd.CDW0.Opcode = 0x06; // ADMIN_IDENTIFY
		NVMeData.Payload.Cmd.NSID = 0;
		NVMeData.Payload.Cmd.u.IDENTIFY.CDW10.CNS = 1;
		NVMeData.Payload.ParamBufLen = sizeof(INTEL_NVME_PAYLOAD) + sizeof(SRB_IO_CONTROL); //0xA4;
		NVMeData.Payload.ReturnBufferLen = 0x1000;
		NVMeData.Payload.CplEntry[0] = 0;

		DWORD dummy;
		if (DeviceIoControl(hIoCtrl, IOCTL_SCSI_MINIPORT,
			&NVMeData,
			sizeof(NVMeData),
			&NVMeData,
			sizeof(NVMeData),
			&dummy, nullptr))
		{
			memcpy_s(data, sizeof(IDENTIFY_DEVICE), NVMeData.DataBuffer, sizeof(IDENTIFY_DEVICE));
			LOG(D1) << "DeviceIoControl(hIoCtrl, IOCTL_SCSI_MINIPORT, OK " << "sizeof(ADMIN_IDENTIFY_CONTROLLER)=" << sizeof(ADMIN_IDENTIFY_CONTROLLER);
			//DtaHexDump(data, 512);
			//DtaHexDump(NVMeData.DataBuffer, 512);
			return TRUE;
		}
		else {
			LOG(D1) << "DeviceIoControl(hIoCtrl, IOCTL_SCSI_MINIPORT, FAIL";
		}

		CloseHandle(hIoCtrl);
	}
	LOG(D1) << "DeviceIoControl(hIoCtrl, IOCTL_SCSI_MINIPORT, FAIL to OPEN";
	return FALSE;
}


//////////////////////////////////////////////////////////////////////////////////////

using namespace std;
DtaDiskNVME::DtaDiskNVME() { LOG(D1) << "DtaDiskNVME Constructor"; };

void DtaDiskNVME::init(const char * devref)
{
	LOG(D1) << "Creating DtaDiskNVME::DtaDiskNVME() " << devref;
	// find interger value of drive numver fron devref
	// buf is \\\\.\\PhysicaldriveNN at position 20 -> NG, try 17
	physicalDriveId = atoi(devref + 17);
	// printf("physical drive numere is %d\n", physicalDriveId);

	//DtaHexDump((void *)devref, 23);
	SDWA * scsi =
		(SDWA *)_aligned_malloc((sizeof(SDWA)), 4096);
	scsiPointer = (void *)scsi;
	hDev = CreateFile(devref,
		GENERIC_WRITE | GENERIC_READ,
		FILE_SHARE_WRITE | FILE_SHARE_READ,
		NULL,
		OPEN_EXISTING,
		0,
		NULL);

	if (INVALID_HANDLE_VALUE == hDev) {
		LOG(D1) << "Open Nvme fail. hDev = " << hex << hDev << endl;
		return;
	}
    else {
		LOG(D1) << "Open Nvme OK. hDev = " << hex << hDev << endl;
        isOpen = TRUE;
	}
	// seems to be system vol series number NOT IDFY command series number
	//  Drive Series Number :0025_385B_61B0_02FA.
}

uint8_t DtaDiskNVME::sendCmd(ATACOMMAND cmd, uint8_t protocol, uint16_t comID, void * buffer, uint32_t bufferlen)
{
    LOG(D1) << "Entering DtaDiskNVME::sendCmd";
    //DWORD bytesReturned = 0; // data returned
    if (!isOpen) {
        LOG(D1) << "Device open failed";
		return DTAERROR_OPEN_ERR; //disk open failed so this will too
    }
	SDWA * scsi = (SDWA *)scsiPointer;
	memset(scsi, 0, sizeof(SDWA));
	// same for every command
	scsi->scsiDetails.DataBuffer = buffer;
	scsi->scsiDetails.DataTransferLength = bufferlen;
	scsi->scsiDetails.Length = sizeof(SCSI_PASS_THROUGH_DIRECT);
	scsi->scsiDetails.TimeOutValue = 20;
	scsi->scsiDetails.SenseInfoLength = 32;
	scsi->scsiDetails.SenseInfoOffset = offsetof(SDWA, sensebytes);
	scsi->scsiDetails.ScsiStatus = 0;
	scsi->scsiDetails.PathId = 0;
	scsi->scsiDetails.TargetId = 0;
	scsi->scsiDetails.Lun = 0;


	if (IF_RECV == cmd) {
		LOG(D1) << "cmd = Security Receive";
		scsi->scsiDetails.DataIn = SCSI_IOCTL_DATA_IN;
		//memset(scsi.scsiDetails.Cdb, 0x00, sizeof(scsi.scsiDetails.Cdb));
		scsi->scsiDetails.CdbLength = 12;
		scsi->scsiDetails.Cdb[0] = 0xa2; // 0xa2 or 0xb5;
		scsi->scsiDetails.Cdb[1] = protocol;
		scsi->scsiDetails.Cdb[2] = (comID >> 8) & 0xff;
		scsi->scsiDetails.Cdb[3] = comID & 0xff;
		scsi->scsiDetails.Cdb[6] = 0; //  (bufferlen >> 24) & 0xff;
		scsi->scsiDetails.Cdb[7] = 0; // (bufferlen >> 16) & 0xff; 
		scsi->scsiDetails.Cdb[8] = (bufferlen >> 8) & 0xff;
		scsi->scsiDetails.Cdb[9] = bufferlen & 0xff;
		scsi->scsiDetails.Cdb[10] = 0;
		scsi->scsiDetails.Cdb[11] = 0;
	}
	else if (IDENTIFY == cmd) {
		//===============================
		LOG(D1) << "cmd = IDENTIFY";
		//printf("pagecode = %02Xh\n", pagecode);
		scsi->scsiDetails.DataIn = SCSI_IOCTL_DATA_IN;
		scsi->scsiDetails.CdbLength = 6;
		scsi->scsiDetails.Cdb[0] = 0x12; // 0xa2 or 0xa5;
		scsi->scsiDetails.Cdb[1] = 0; // evpd;
		scsi->scsiDetails.Cdb[2] = 0; // pagecode; //  
		scsi->scsiDetails.Cdb[3] = (bufferlen >> 8) & 0xff;
		scsi->scsiDetails.Cdb[4] = bufferlen & 0xff;
	}
	else {
		// security send command
		LOG(D1) << "cmd = Security Send" ;
		scsi->scsiDetails.DataIn = SCSI_IOCTL_DATA_OUT;
		scsi->scsiDetails.CdbLength = 12;
		scsi->scsiDetails.Cdb[0] = 0xb5; // 0xa2 or 0xb5;
		scsi->scsiDetails.Cdb[1] = protocol;
		scsi->scsiDetails.Cdb[2] = (comID >> 8) & 0xff;
		scsi->scsiDetails.Cdb[3] = comID & 0xff;
		scsi->scsiDetails.Cdb[6] = 0; //  (bufferlen >> 24) & 0xff;
		scsi->scsiDetails.Cdb[7] = 0; // (bufferlen >> 16) & 0xff; 
		scsi->scsiDetails.Cdb[8] = (bufferlen >> 8) & 0xff;
		scsi->scsiDetails.Cdb[9] = bufferlen & 0xff;
		scsi->scsiDetails.Cdb[10] = 0;
		scsi->scsiDetails.Cdb[11] = 0;
	}

	DWORD n = 0;
	int status = DeviceIoControl(hDev,
		IOCTL_SCSI_PASS_THROUGH_DIRECT,
		scsi, sizeof(SDWA),
		scsi, sizeof(SDWA),
		&n,
		(LPOVERLAPPED)NULL);

	/*
	If the operation completes successfully, the return value is nonzero
	*/
	if (status)
	{
		LOG(D1) << "DeviceIoControl return non-zero status OK " << status;
		//if (scsi->scsiDetails.ScsiStatus) {
			// it only make sense to look sense info if scsi get error
			//printf("scsi->scsiDetails.ScsiStatus = %d and sense info : \n", scsi->scsiDetails.ScsiStatus);
			//DtaHexDump(scsi->sensebytes, 32);
		//}
	}
	else
	{
		IFLOG(D1) {
			//printf("*************************************************\n");
			//printf("***** DeviceIoControl return zero status NG *****\n");
			//printf("*************************************************\n");
		}
		DWORD err = 0;
		err = GetLastError();
		LOG(D1) << "GetLastError " <<  err;
		return DTAERROR_COMMAND_ERROR;
	}
	IFLOG(D4) {
		//printf("cdb : after DeviceIoControl\n");
		DtaHexDump(scsi->scsiDetails.Cdb, 16);

		//printf("SDBW buffer content : after DeviceIoControl \n");
		DtaHexDump(scsi, sizeof(SDWA));

		//printf("data buffer content : after DeviceIoControl ; returned data length = %ld \n", n);
		DtaHexDump(scsi->scsiDetails.DataBuffer, 256);
	}
	return 0;
}


/** adds the IDENTIFY information to the disk_info structure */

void DtaDiskNVME::identify(OPAL_DiskInfo& disk_info)
{
    LOG(D1) << "Entering DtaDiskNVME::identify()"; 
	vector<uint8_t> nullz(4096, 0x00);
    void * identifyResp = NULL;
	/* NVME identify response

	4096-byte ADMIN_IDENTIFY_CONTROLLER

	*/

#ifdef IDENTIFY_RESPONSE 
#undef IDENTIFY_RESPONSE 
#endif

#define IDENTIFY_RESPONSE ADMIN_IDENTIFY_CONTROLLER

	identifyResp = _aligned_malloc(sizeof(StorageQueryWithBuffer), IO_BUFFER_ALIGNMENT);
	if (NULL == identifyResp) {
		LOG(E) << "DtaDiskNVME::identify allocate memory error";
		return ;
	}
    memset(identifyResp, 0, IO_BUFFER_LENGTH);
	StorageQueryWithBuffer * Q; 
	///////////////////////////////////////////////////////////////
	Q = (StorageQueryWithBuffer *)identifyResp; // Q point to the alloc buffer
	int s = GetIDFY(hDev, (StorageQueryWithBuffer *)identifyResp);
	if (!s) {
		IFLOG(D4) {
			LOG(D1) << "Nvme IDFY OK";
			LOG(D1) << "Q";
			DtaHexDump(identifyResp, 128);
			LOG(D1) << "Q->ProtocolSpecific ";
			DtaHexDump(&(Q->ProtocolSpecific), 128);
			DtaHexDump(&(Q->Query), 128);
			LOG(D1) << "Q->Buffer ";
			DtaHexDump(Q->Buffer, 4096);
		}

	}
	else {
		// try Intel RST before claim fail 
		LOG(D1) << "Nvme IDFY FAIL, Try Nvme Intel RST";
		IDENTIFY_DEVICE*  id = (IDENTIFY_DEVICE*)identifyResp;
		//if (DoIdentifyDeviceNVMeIntelRst(INT physicalDriveId, INT scsiPort, INT scsiTargetId, IDENTIFY_DEVICE* data))
		if (DoIdentifyDeviceNVMeIntelRst(physicalDriveId, scsiPort, scsiTargetId, (IDENTIFY_DEVICE*) identifyResp))
		{
			LOG(D1) << "DoIdentifyDeviceNVMeIntelRst(physicalDriveId, scsiPort, scsiTargetId, (IDENTIFY_DEVICE*) identifyResp) OK";
			// identifyResponse point to data structure NVME_IDENTIFY_DEVICE
			// save it to disk_ifo
			disk_info.devType = DEVICE_TYPE_NVME;
			for (int i = 0; i < sizeof(disk_info.serialNum); i += 1) {
				disk_info.serialNum[i] = id->N.SerialNumber[i];
			}
			for (int i = 0; i < sizeof(disk_info.firmwareRev); i += 1) {
				disk_info.firmwareRev[i] = id->N.FirmwareRev[i];
			}
			for (int i = 0; i < sizeof(disk_info.modelNum); i += 1) {
				disk_info.modelNum[i] = id->N.Model[i];
			}
			if (1 == (disk_info.fips_fw_match = getFwMatch((const char *)disk_info.firmwareRev))) {
				DtaHexDump(id, 4096);
				disk_info.fips_support = *(((uint8_t *)id) + 4093) & 0x01;
				disk_info.fips = (*(((uint8_t *)id) + 4093) & 0x02) >> 1; // bit 0 should AND 0x01 0x02;
				LOG(D1) << "Match Phison Nvme FIPS FW Name ; disk_info.fips_support=" << disk_info.fips_support + 0 << " disk_info.fips=" << disk_info.fips + 0;

			}
			else {
				LOG(D1) << "No Match Phison Nvme FIPS FW Name ";
				disk_info.fips = 0;
				disk_info.fips_support = 0;
			}
			//disk_info.fips = *(((uint8_t *)identifyResp) + 4093) & 0x02 ;

			_aligned_free(identifyResp);
			return;


		}
		else {
			;
			//LOG(D) << "GetIDFY fail, no device info";
			_aligned_free(identifyResp);
			return;
		}
	}
	
	ADMIN_IDENTIFY_CONTROLLER * id = (ADMIN_IDENTIFY_CONTROLLER *)Q->Buffer;
	disk_info.devType = DEVICE_TYPE_NVME;
	for (int i = 0; i < sizeof(disk_info.serialNum); i += 1) {
		disk_info.serialNum[i] = id->serialNum[i];
	}
	for (int i = 0; i < sizeof(disk_info.firmwareRev); i += 1) {
		disk_info.firmwareRev[i] = id->firmwareRev[i];
	}
	for (int i = 0; i < sizeof(disk_info.modelNum); i += 1) {
		disk_info.modelNum[i] = id->modelNum[i];
	}
	if (1 == (disk_info.fips_fw_match = getFwMatch((const char *)disk_info.firmwareRev))) {
		DtaHexDump(id, 4096);
		disk_info.fips_support = *(((uint8_t *)id) + 4093) & 0x01;
		disk_info.fips = (*(((uint8_t *)id) + 4093) & 0x02) >> 1; // bit 0 should AND 0x01 0x02;
		LOG(D1) << "DtaDiskNVME::identify Match Phison Nvme FIPS FW Name ; disk_info.fips_support=" << disk_info.fips_support + 0 << " disk_info.fips=" << disk_info.fips + 0; 
	}
	else {
		LOG(D1) << "DtaDiskNVME::identify No Match Phison Nvme FIPS FW Name ";
		disk_info.fips = 0;
		disk_info.fips_support = 0;
	}
	_aligned_free(identifyResp);
	return;
}

/** Close the filehandle so this object can be delete. */
DtaDiskNVME::~DtaDiskNVME()
{
    LOG(D1) << "Destroying DtaDiskNVME";
    CloseHandle(hDev);
    _aligned_free(scsiPointer);
}

