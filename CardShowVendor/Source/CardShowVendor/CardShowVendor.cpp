// Copyright Card Show Vendor. All Rights Reserved.

#include "CardShowVendor.h"

DEFINE_LOG_CATEGORY(LogCardShowVendor);

#define LOCTEXT_NAMESPACE "FCardShowVendorModule"

void FCardShowVendorModule::StartupModule()
{
	UE_LOG(LogCardShowVendor, Log, TEXT("Card Show Vendor module started"));
}

void FCardShowVendorModule::ShutdownModule()
{
	UE_LOG(LogCardShowVendor, Log, TEXT("Card Show Vendor module shutdown"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_PRIMARY_GAME_MODULE(FCardShowVendorModule, CardShowVendor, "CardShowVendor");
