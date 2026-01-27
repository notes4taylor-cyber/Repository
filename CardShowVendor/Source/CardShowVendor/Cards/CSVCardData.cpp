// Copyright Card Show Vendor. All Rights Reserved.

#include "Cards/CSVCardData.h"

UCSVCardData::UCSVCardData()
{
	Sport = ECSVCardSport::Baseball;
	Rarity = ECSVCardRarity::Common;
	Era = ECSVCardEra::Modern;
	BaseValue = 1.0f;
	SpawnWeight = 1.0f;
	Year = 2024;
}

FPrimaryAssetId UCSVCardData::GetPrimaryAssetId() const
{
	return FPrimaryAssetId(TEXT("CSVCardData"), CardID);
}
