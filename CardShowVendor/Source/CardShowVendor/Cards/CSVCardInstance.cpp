// Copyright Card Show Vendor. All Rights Reserved.

#include "Cards/CSVCardInstance.h"
#include "Cards/CSVCardData.h"

UCSVCardInstance::UCSVCardInstance()
{
	CardData = nullptr;
	ListedPrice = 0.0f;
	Condition = ECSVCardCondition::NearMint;
	SerialNumber = 0;
	UniqueInstanceID = FGuid::NewGuid();
}

void UCSVCardInstance::InitializeFromData(UCSVCardData* Data)
{
	CardData = Data;
	
	if (CardData)
	{
		ListedPrice = CardData->BaseValue;
		
		// Random condition distribution
		float ConditionRoll = FMath::FRand();
		if (ConditionRoll < 0.05f)
		{
			Condition = ECSVCardCondition::Poor;
		}
		else if (ConditionRoll < 0.15f)
		{
			Condition = ECSVCardCondition::Fair;
		}
		else if (ConditionRoll < 0.30f)
		{
			Condition = ECSVCardCondition::Good;
		}
		else if (ConditionRoll < 0.50f)
		{
			Condition = ECSVCardCondition::VeryGood;
		}
		else if (ConditionRoll < 0.70f)
		{
			Condition = ECSVCardCondition::Excellent;
		}
		else if (ConditionRoll < 0.90f)
		{
			Condition = ECSVCardCondition::NearMint;
		}
		else if (ConditionRoll < 0.98f)
		{
			Condition = ECSVCardCondition::Mint;
		}
		else
		{
			Condition = ECSVCardCondition::GemMint;
		}

		// Generate serial number if card is numbered
		if (CardData->bIsNumbered && CardData->TotalPrintRun > 0)
		{
			SerialNumber = FMath::RandRange(1, CardData->TotalPrintRun);
		}
	}
}

FText UCSVCardInstance::GetCardName() const
{
	if (CardData)
	{
		return CardData->CardName;
	}
	return FText::FromString(TEXT("Unknown Card"));
}

FName UCSVCardInstance::GetSport() const
{
	if (CardData)
	{
		return StaticEnum<ECSVCardSport>()->GetNameByValue((int64)CardData->Sport);
	}
	return NAME_None;
}

int32 UCSVCardInstance::GetRarity() const
{
	if (CardData)
	{
		return (int32)CardData->Rarity;
	}
	return 0;
}

float UCSVCardInstance::GetBaseValue() const
{
	if (CardData)
	{
		return CardData->BaseValue;
	}
	return 0.0f;
}

float UCSVCardInstance::GetMarketValue() const
{
	float BaseValue = GetBaseValue();
	float ConditionMod = GetConditionMultiplier();
	float GradeMod = IsGraded() ? GetGradeMultiplier() : 1.0f;
	
	return BaseValue * ConditionMod * GradeMod;
}

float UCSVCardInstance::GetConditionMultiplier() const
{
	switch (Condition)
	{
	case ECSVCardCondition::Poor:		return 0.1f;
	case ECSVCardCondition::Fair:		return 0.25f;
	case ECSVCardCondition::Good:		return 0.5f;
	case ECSVCardCondition::VeryGood:	return 0.7f;
	case ECSVCardCondition::Excellent:	return 0.85f;
	case ECSVCardCondition::NearMint:	return 1.0f;
	case ECSVCardCondition::Mint:		return 1.25f;
	case ECSVCardCondition::GemMint:	return 1.5f;
	default:							return 1.0f;
	}
}

int32 UCSVCardInstance::GetTotalPrintRun() const
{
	if (CardData)
	{
		return CardData->TotalPrintRun;
	}
	return 0;
}
