// Copyright Card Show Vendor. All Rights Reserved.

#include "Core/CSVPlayerState.h"
#include "Cards/CSVCardInstance.h"
#include "Cards/CSVCardData.h"
#include "CardShowVendor.h"

ACSVPlayerState::ACSVPlayerState()
{
	Money = 0.0f;
	BoothLevel = 1;
	DisplayCaseCount = 2;
}

void ACSVPlayerState::BeginPlay()
{
	Super::BeginPlay();
	InitializeStartingState();
}

void ACSVPlayerState::InitializeStartingState()
{
	Money = StartingMoney;
	BoothLevel = StartingBoothLevel;
	DisplayCaseCount = StartingDisplayCases;

	UE_LOG(LogCardShowVendor, Log, TEXT("Player initialized with $%.2f"), Money);
}

void ACSVPlayerState::AddMoney(float Amount)
{
	if (Amount > 0)
	{
		Money += Amount;
		OnMoneyChanged.Broadcast(Money);
		UE_LOG(LogCardShowVendor, Verbose, TEXT("Added $%.2f, new total: $%.2f"), Amount, Money);
	}
}

bool ACSVPlayerState::SpendMoney(float Amount)
{
	if (Amount <= 0)
	{
		return false;
	}

	if (Money >= Amount)
	{
		Money -= Amount;
		OnMoneyChanged.Broadcast(Money);
		UE_LOG(LogCardShowVendor, Verbose, TEXT("Spent $%.2f, new total: $%.2f"), Amount, Money);
		return true;
	}

	UE_LOG(LogCardShowVendor, Warning, TEXT("Cannot afford $%.2f (have $%.2f)"), Amount, Money);
	return false;
}

bool ACSVPlayerState::AddCardToInventory(UCSVCardInstance* Card)
{
	if (!Card)
	{
		return false;
	}

	if (!HasInventorySpace())
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Inventory full, cannot add card"));
		return false;
	}

	CardInventory.Add(Card);
	OnInventoryChanged.Broadcast(CardInventory.Num());
	UE_LOG(LogCardShowVendor, Verbose, TEXT("Added card to inventory, count: %d"), CardInventory.Num());
	return true;
}

bool ACSVPlayerState::RemoveCardFromInventory(UCSVCardInstance* Card)
{
	if (!Card)
	{
		return false;
	}

	int32 RemovedCount = CardInventory.Remove(Card);
	if (RemovedCount > 0)
	{
		OnInventoryChanged.Broadcast(CardInventory.Num());
		UE_LOG(LogCardShowVendor, Verbose, TEXT("Removed card from inventory, count: %d"), CardInventory.Num());
		return true;
	}

	return false;
}

TArray<UCSVCardInstance*> ACSVPlayerState::GetCardsByRarity(int32 Rarity) const
{
	TArray<UCSVCardInstance*> Result;
	for (UCSVCardInstance* Card : CardInventory)
	{
		if (Card && Card->GetRarity() == Rarity)
		{
			Result.Add(Card);
		}
	}
	return Result;
}

TArray<UCSVCardInstance*> ACSVPlayerState::GetCardsBySport(FName Sport) const
{
	TArray<UCSVCardInstance*> Result;
	for (UCSVCardInstance* Card : CardInventory)
	{
		if (Card && Card->GetSport() == Sport)
		{
			Result.Add(Card);
		}
	}
	return Result;
}

void ACSVPlayerState::SortInventoryByValue(bool bDescending)
{
	CardInventory.Sort([bDescending](const UCSVCardInstance& A, const UCSVCardInstance& B)
	{
		if (bDescending)
		{
			return A.GetMarketValue() > B.GetMarketValue();
		}
		return A.GetMarketValue() < B.GetMarketValue();
	});

	OnInventoryChanged.Broadcast(CardInventory.Num());
}

UCSVCardInstance* ACSVPlayerState::CreateCardInstance(UCSVCardData* CardData)
{
	if (!CardData)
	{
		return nullptr;
	}

	UCSVCardInstance* NewCard = NewObject<UCSVCardInstance>(this);
	NewCard->InitializeFromData(CardData);
	return NewCard;
}

bool ACSVPlayerState::UnlockFeature(FName FeatureName, float Cost)
{
	if (HasFeature(FeatureName))
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Feature %s already unlocked"), *FeatureName.ToString());
		return false;
	}

	if (!SpendMoney(Cost))
	{
		return false;
	}

	UnlockedFeatures.Add(FeatureName);
	UE_LOG(LogCardShowVendor, Log, TEXT("Unlocked feature: %s"), *FeatureName.ToString());
	return true;
}

bool ACSVPlayerState::HasFeature(FName FeatureName) const
{
	return UnlockedFeatures.Contains(FeatureName);
}
