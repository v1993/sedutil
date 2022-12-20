/* C:B**************************************************************************
This software is Copyright 2014-2022 Bright Plaza Inc. <drivetrust@drivetrust.com>

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

#include <log/log.h>

#include "DtaHexDump.h"
#include "DtaStructures.h"
#include "DtaDevMacOSTPer.h"
#include "DtaConstants.h"

#include "DtaDevGeneric.h"
#include "DtaDevEnterprise.h"
#include "DtaDevOpal1.h"
#include "DtaDevOpal2.h"

using namespace std;


static DtaDevOS* getDtaDevOSSubclassInstance(DtaDevMacOSTPer * t,
                                             const char * devref,
                                             bool genericIfNotTPer) {
    if (t->isOpal2())     return new DtaDevOpal2(devref);
    if (t->isOpal1())     return new DtaDevOpal1(devref);
    if (t->isEprise())    return new DtaDevEnterprise(devref);
//  if (t->isRuby()) ...  etc.
    
    if (genericIfNotTPer) return new DtaDevGeneric(devref);
    
    LOG(E) << "Unknown OPAL SSC ";
    return NULL;
}

static uint8_t getDtaDevOS(DtaDevMacOSBlockStorageDevice *blockStorageDevice,
                           const char *devref, DtaDevOS * &device, bool genericIfNotTPer) {
    if (!blockStorageDevice->isAnySSC()) {
        if (genericIfNotTPer) {
            device = new DtaDevGeneric(devref);
            return DTAERROR_SUCCESS;
        }
        LOG(E) << "Invalid or unsupported device " << devref;
        return DTAERROR_COMMAND_ERROR;
    }
    
    DtaDevMacOSTPer * t = dynamic_cast<DtaDevMacOSTPer *>(blockStorageDevice);
    if (NULL == t) {
        if (genericIfNotTPer) {
            device = new DtaDevGeneric(devref);
            return DTAERROR_SUCCESS;
        }
        LOG(E) << "Create DtaDevMacOSTPer object failed?!";
        return DTAERROR_OBJECT_CREATE_FAILED;
    }
    
    device = getDtaDevOSSubclassInstance(t, devref, genericIfNotTPer);
    
    if (NULL == device) {
        LOG(E) << "Create DtaDevOS object failed?!";
        return DTAERROR_OBJECT_CREATE_FAILED;
    }
    
    return DTAERROR_SUCCESS;
}

uint8_t DtaDevOS::getDtaDevOS(const char * devref, DtaDevOS * & device, bool genericIfNotTPer)
{
    DTA_DEVICE_INFO di;
    bzero(&di,sizeof(di));
    DtaDevMacOSBlockStorageDevice * bsd =
        DtaDevMacOSBlockStorageDevice::getBlockStorageDevice(devref, &di);
    if (bsd==NULL) {
        LOG(E) << "Unrecognized device '" << devref << "'";
        return DTAERROR_OBJECT_CREATE_FAILED;
    }
    return ::getDtaDevOS(bsd, devref, device, genericIfNotTPer);
}

uint8_t DtaDev::getDtaDev(const char * devref, DtaDev * & device, bool genericIfNotTPer)
{
    DtaDevOS * d;
    uint8_t result = DtaDevOS::getDtaDevOS(devref, d, genericIfNotTPer);
    if (result == DTAERROR_SUCCESS) {
        device = static_cast<DtaDev *>(d);
    }
    return result;
}

