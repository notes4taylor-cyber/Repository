// Copyright Card Show Vendor. All Rights Reserved.

#include "Cards/CSVCardTypes.h"

FString UCSVCardHelpers::GetRarityName(ECSVCardRarity Rarity)
{
	switch (Rarity)
	{
	case ECSVCardRarity::Common:		return TEXT("Common");
	case ECSVCardRarity::Uncommon:		return TEXT("Uncommon");
	case ECSVCardRarity::Rare:			return TEXT("Rare");
	case ECSVCardRarity::UltraRare:		return TEXT("Ultra Rare");
	case ECSVCardRarity::Legendary:		return TEXT("Legendary");
	case ECSVCardRarity::OneOfOne:		return TEXT("1/1");
	default:							return TEXT("Unknown");
	}
}

FLinearColor UCSVCardHelpers::GetRarityColor(ECSVCardRarity Rarity)
{
	switch (Rarity)
	{
	case ECSVCardRarity::Common:		return FLinearColor(0.5f, 0.5f, 0.5f);		// Gray
	case ECSVCardRarity::Uncommon:		return FLinearColor(0.2f, 0.8f, 0.2f);		// Green
	case ECSVCardRarity::Rare:			return FLinearColor(0.2f, 0.4f, 1.0f);		// Blue
	case ECSVCardRarity::UltraRare:		return FLinearColor(0.6f, 0.2f, 0.8f);		// Purple
	case ECSVCardRarity::Legendary:		return FLinearColor(1.0f, 0.8f, 0.0f);		// Gold
	case ECSVCardRarity::OneOfOne:		return FLinearColor(1.0f, 0.2f, 0.2f);		// Red
	default:							return FLinearColor::White;
	}
}

float UCSVCardHelpers::GetRarityValueMultiplier(ECSVCardRarity Rarity)
{
	switch (Rarity)
	{
	case ECSVCardRarity::Common:		return 1.0f;
	case ECSVCardRarity::Uncommon:		return 2.5f;
	case ECSVCardRarity::Rare:			return 10.0f;
	case ECSVCardRarity::UltraRare:		return 50.0f;
	case ECSVCardRarity::Legendary:		return 250.0f;
	case ECSVCardRarity::OneOfOne:		return 1000.0f;
	default:							return 1.0f;
	}
}

FString UCSVCardHelpers::GetConditionName(ECSVCardCondition Condition)
{
	switch (Condition)
	{
	case ECSVCardCondition::Poor:		return TEXT("Poor (1)");
	case ECSVCardCondition::Good:		return TEXT("Good (3)");
	case ECSVCardCondition::VeryGood:	return TEXT("Very Good (5)");
	case ECSVCardCondition::Excellent:	return TEXT("Excellent (7)");
	case ECSVCardCondition::NearMint:	return TEXT("Near Mint (8)");
	case ECSVCardCondition::Mint:		return TEXT("Mint (9)");
	case ECSVCardCondition::GemMint:	return TEXT("Gem Mint (10)");
	case ECSVCardCondition::Ungraded:	return TEXT("Ungraded");
	default:							return TEXT("Unknown");
	}
}

float UCSVCardHelpers::GetConditionValueMultiplier(ECSVCardCondition Condition)
{
	switch (Condition)
	{
	case ECSVCardCondition::Poor:		return 0.1f;
	case ECSVCardCondition::Good:		return 0.25f;
	case ECSVCardCondition::VeryGood:	return 0.5f;
	case ECSVCardCondition::Excellent:	return 0.75f;
	case ECSVCardCondition::NearMint:	return 1.0f;
	case ECSVCardCondition::Mint:		return 1.5f;
	case ECSVCardCondition::GemMint:	return 3.0f;
	case ECSVCardCondition::Ungraded:	return 0.6f;
	default:							return 1.0f;
	}
}

FString UCSVCardHelpers::GetSportName(ECSVCardSport Sport)
{
	switch (Sport)
	{
	case ECSVCardSport::Baseball:			return TEXT("Baseball");
	case ECSVCardSport::Basketball:			return TEXT("Basketball");
	case ECSVCardSport::Football:			return TEXT("Football");
	case ECSVCardSport::Hockey:				return TEXT("Hockey");
	case ECSVCardSport::Soccer:				return TEXT("Soccer");
	case ECSVCardSport::Pokemon:			return TEXT("Pokemon");
	case ECSVCardSport::MagicTheGathering:	return TEXT("Magic: The Gathering");
	case ECSVCardSport::YuGiOh:				return TEXT("Yu-Gi-Oh!");
	case ECSVCardSport::Other:				return TEXT("Other");
	default:								return TEXT("Unknown");
	}
}

int32 UCSVCardHelpers::GetGradeNumber(ECSVCardCondition Condition)
{
	return static_cast<int32>(Condition);
}
