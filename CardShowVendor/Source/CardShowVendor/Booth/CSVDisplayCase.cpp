// Copyright Card Show Vendor. All Rights Reserved.

#include "Booth/CSVDisplayCase.h"
#include "Cards/CSVCardInstance.h"
#include "CardShowVendor.h"

ACSVDisplayCase::ACSVDisplayCase()
{
	PrimaryActorTick.bCanEverTick = false;

	RootSceneComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));
	SetRootComponent(RootSceneComponent);

	CaseMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CaseMesh"));
	CaseMesh->SetupAttachment(RootSceneComponent);

	MaxSlots = 8;
	CaseType = TEXT("Basic");
	PrestigeBonus = 1.0f;
}

void ACSVDisplayCase::BeginPlay()
{
	Super::BeginPlay();
	InitializeSlots();
}

void ACSVDisplayCase::InitializeSlots()
{
	// Initialize slot array with nulls
	CardSlots.Empty();
	CardSlots.SetNum(MaxSlots);
	for (int32 i = 0; i < MaxSlots; ++i)
	{
		CardSlots[i] = nullptr;
	}

	// Setup default slot positions (2 rows of 4)
	SlotPositions.Empty();
	float SlotWidth = 15.0f;
	float SlotHeight = 20.0f;

	for (int32 Row = 0; Row < 2; ++Row)
	{
		for (int32 Col = 0; Col < 4; ++Col)
		{
			float X = 0.0f;
			float Y = (Col - 1.5f) * SlotWidth;
			float Z = (Row * SlotHeight) + 5.0f;
			SlotPositions.Add(FVector(X, Y, Z));
		}
	}
}

bool ACSVDisplayCase::PlaceCard(UCSVCardInstance* Card, int32 SlotIndex)
{
	if (!Card)
	{
		return false;
	}

	// Auto-assign slot if -1
	if (SlotIndex == -1)
	{
		SlotIndex = GetFirstEmptySlot();
	}

	// Validate slot index
	if (SlotIndex < 0 || SlotIndex >= MaxSlots)
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Invalid slot index: %d"), SlotIndex);
		return false;
	}

	// Check if slot is occupied
	if (CardSlots[SlotIndex] != nullptr)
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Slot %d is already occupied"), SlotIndex);
		return false;
	}

	// Place the card
	CardSlots[SlotIndex] = Card;
	Card->bIsDisplayed = true;
	Card->DisplaySlotIndex = SlotIndex;

	OnCardPlaced.Broadcast(Card, SlotIndex);
	RefreshDisplay();

	UE_LOG(LogCardShowVendor, Verbose, TEXT("Placed card in slot %d"), SlotIndex);
	return true;
}

UCSVCardInstance* ACSVDisplayCase::RemoveCard(int32 SlotIndex)
{
	if (SlotIndex < 0 || SlotIndex >= MaxSlots)
	{
		return nullptr;
	}

	UCSVCardInstance* Card = CardSlots[SlotIndex];
	if (Card)
	{
		CardSlots[SlotIndex] = nullptr;
		Card->bIsDisplayed = false;
		Card->DisplaySlotIndex = -1;

		OnCardRemoved.Broadcast(Card, SlotIndex);
		RefreshDisplay();

		UE_LOG(LogCardShowVendor, Verbose, TEXT("Removed card from slot %d"), SlotIndex);
	}

	return Card;
}

void ACSVDisplayCase::ClearAllCards()
{
	for (int32 i = 0; i < MaxSlots; ++i)
	{
		if (CardSlots[i])
		{
			CardSlots[i]->bIsDisplayed = false;
			CardSlots[i]->DisplaySlotIndex = -1;
			OnCardRemoved.Broadcast(CardSlots[i], i);
			CardSlots[i] = nullptr;
		}
	}
	RefreshDisplay();
	UE_LOG(LogCardShowVendor, Log, TEXT("Cleared all cards from display case"));
}

UCSVCardInstance* ACSVDisplayCase::GetCardInSlot(int32 SlotIndex) const
{
	if (SlotIndex >= 0 && SlotIndex < CardSlots.Num())
	{
		return CardSlots[SlotIndex];
	}
	return nullptr;
}

bool ACSVDisplayCase::IsSlotEmpty(int32 SlotIndex) const
{
	if (SlotIndex >= 0 && SlotIndex < CardSlots.Num())
	{
		return CardSlots[SlotIndex] == nullptr;
	}
	return false;
}

int32 ACSVDisplayCase::GetFirstEmptySlot() const
{
	for (int32 i = 0; i < CardSlots.Num(); ++i)
	{
		if (CardSlots[i] == nullptr)
		{
			return i;
		}
	}
	return -1;
}

TArray<UCSVCardInstance*> ACSVDisplayCase::GetDisplayedCards() const
{
	TArray<UCSVCardInstance*> DisplayedCards;
	for (UCSVCardInstance* Card : CardSlots)
	{
		if (Card)
		{
			DisplayedCards.Add(Card);
		}
	}
	return DisplayedCards;
}

int32 ACSVDisplayCase::GetUsedSlots() const
{
	int32 Used = 0;
	for (UCSVCardInstance* Card : CardSlots)
	{
		if (Card)
		{
			Used++;
		}
	}
	return Used;
}

float ACSVDisplayCase::GetTotalDisplayValue() const
{
	float Total = 0.0f;
	for (UCSVCardInstance* Card : CardSlots)
	{
		if (Card)
		{
			Total += Card->AskingPrice * PrestigeBonus;
		}
	}
	return Total;
}

float ACSVDisplayCase::GetHighestCardValue() const
{
	float Highest = 0.0f;
	for (UCSVCardInstance* Card : CardSlots)
	{
		if (Card && Card->AskingPrice > Highest)
		{
			Highest = Card->AskingPrice;
		}
	}
	return Highest * PrestigeBonus;
}

void ACSVDisplayCase::RefreshDisplay()
{
	// This would update visual representations of cards in the display
	// In a full implementation, this would spawn/update card meshes or widgets
	UE_LOG(LogCardShowVendor, Verbose, TEXT("Display case refreshed: %d/%d slots used"),
		GetUsedSlots(), MaxSlots);
}
