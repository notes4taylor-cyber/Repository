// Copyright Card Show Vendor. All Rights Reserved.

#include "Booth/CSVVendorBooth.h"
#include "Cards/CSVCardInstance.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "CardShowVendor.h"

ACSVVendorBooth::ACSVVendorBooth()
{
	PrimaryActorTick.bCanEverTick = true;

	// Create root component
	BoothMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BoothMesh"));
	RootComponent = BoothMesh;

	// Create interaction volume
	InteractionVolume = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractionVolume"));
	InteractionVolume->SetupAttachment(RootComponent);
	InteractionVolume->SetBoxExtent(FVector(200.0f, 200.0f, 100.0f));
	InteractionVolume->SetCollisionProfileName(TEXT("Trigger"));

	CurrentLevel = 1;
	BoothName = FText::FromString(TEXT("My Booth"));
}

void ACSVVendorBooth::BeginPlay()
{
	Super::BeginPlay();

	InteractionVolume->OnComponentBeginOverlap.AddDynamic(this, &ACSVVendorBooth::OnInteractionBeginOverlap);

	InitializeBooth(CurrentLevel);
}

void ACSVVendorBooth::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ACSVVendorBooth::InitializeBooth(int32 BoothLevel)
{
	CurrentLevel = BoothLevel;

	// Calculate display slots based on level
	int32 SlotCount = 4 + (BoothLevel * 2); // Base 4 slots + 2 per level
	SetupDisplaySlots(SlotCount);

	UE_LOG(LogCardShowVendor, Log, TEXT("Booth initialized at level %d with %d display slots"), 
		CurrentLevel, DisplaySlots.Num());
}

void ACSVVendorBooth::UpgradeBooth()
{
	CurrentLevel++;
	int32 NewSlotCount = 4 + (CurrentLevel * 2);
	
	// Add new slots without clearing existing cards
	while (DisplaySlots.Num() < NewSlotCount)
	{
		FCSVDisplaySlot NewSlot;
		NewSlot.SlotIndex = DisplaySlots.Num();
		NewSlot.LocalPosition = FVector(
			(NewSlot.SlotIndex % 4) * 50.0f - 75.0f,
			(NewSlot.SlotIndex / 4) * 50.0f,
			50.0f
		);
		DisplaySlots.Add(NewSlot);
	}

	UE_LOG(LogCardShowVendor, Log, TEXT("Booth upgraded to level %d with %d display slots"), 
		CurrentLevel, DisplaySlots.Num());
}

void ACSVVendorBooth::SetupDisplaySlots(int32 SlotCount)
{
	DisplaySlots.Empty();

	for (int32 i = 0; i < SlotCount; ++i)
	{
		FCSVDisplaySlot Slot;
		Slot.SlotIndex = i;
		Slot.DisplayedCard = nullptr;
		Slot.LocalPosition = FVector(
			(i % 4) * 50.0f - 75.0f,
			(i / 4) * 50.0f,
			50.0f
		);
		Slot.bIsHighlighted = false;
		DisplaySlots.Add(Slot);
	}
}

bool ACSVVendorBooth::AddCardToDisplay(UCSVCardInstance* Card, int32 SlotIndex)
{
	if (!Card)
	{
		return false;
	}

	if (!DisplaySlots.IsValidIndex(SlotIndex))
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Invalid slot index %d"), SlotIndex);
		return false;
	}

	if (DisplaySlots[SlotIndex].DisplayedCard != nullptr)
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Slot %d already occupied"), SlotIndex);
		return false;
	}

	DisplaySlots[SlotIndex].DisplayedCard = Card;
	Card->bIsOnDisplay = true;
	Card->DisplaySlotIndex = SlotIndex;

	UE_LOG(LogCardShowVendor, Verbose, TEXT("Card added to display slot %d"), SlotIndex);
	return true;
}

UCSVCardInstance* ACSVVendorBooth::RemoveCardFromDisplay(int32 SlotIndex)
{
	if (!DisplaySlots.IsValidIndex(SlotIndex))
	{
		return nullptr;
	}

	UCSVCardInstance* Card = DisplaySlots[SlotIndex].DisplayedCard;
	if (Card)
	{
		Card->bIsOnDisplay = false;
		Card->DisplaySlotIndex = -1;
		DisplaySlots[SlotIndex].DisplayedCard = nullptr;

		UE_LOG(LogCardShowVendor, Verbose, TEXT("Card removed from display slot %d"), SlotIndex);
	}

	return Card;
}

void ACSVVendorBooth::ClearAllDisplays()
{
	for (int32 i = 0; i < DisplaySlots.Num(); ++i)
	{
		RemoveCardFromDisplay(i);
	}
}

UCSVCardInstance* ACSVVendorBooth::GetCardInSlot(int32 SlotIndex) const
{
	if (DisplaySlots.IsValidIndex(SlotIndex))
	{
		return DisplaySlots[SlotIndex].DisplayedCard;
	}
	return nullptr;
}

TArray<UCSVCardInstance*> ACSVVendorBooth::GetAllDisplayedCards() const
{
	TArray<UCSVCardInstance*> Cards;
	for (const FCSVDisplaySlot& Slot : DisplaySlots)
	{
		if (Slot.DisplayedCard)
		{
			Cards.Add(Slot.DisplayedCard);
		}
	}
	return Cards;
}

bool ACSVVendorBooth::SellCard(UCSVCardInstance* Card, float Price)
{
	if (!Card)
	{
		return false;
	}

	// Remove from display if displayed
	if (Card->bIsOnDisplay && Card->DisplaySlotIndex >= 0)
	{
		RemoveCardFromDisplay(Card->DisplaySlotIndex);
	}

	RecordSale(Price);
	OnCardSold.Broadcast(Card, Price);

	UE_LOG(LogCardShowVendor, Log, TEXT("Card sold for $%.2f"), Price);
	return true;
}

void ACSVVendorBooth::RecordSale(float Amount)
{
	Stats.SalesThisShow++;
	Stats.RevenueThisShow += Amount;

	if (Amount > Stats.HighestSale)
	{
		Stats.HighestSale = Amount;
	}
}

void ACSVVendorBooth::ResetShowStats()
{
	Stats.SalesThisShow = 0;
	Stats.RevenueThisShow = 0.0f;
	Stats.CustomersVisited = 0;
	Stats.HighestSale = 0.0f;
}

void ACSVVendorBooth::OnInteractionBeginOverlap(UPrimitiveComponent* OverlappedComponent, 
	AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, 
	bool bFromSweep, const FHitResult& SweepResult)
{
	if (OtherActor)
	{
		Stats.CustomersVisited++;
		OnCustomerApproached.Broadcast(OtherActor);
	}
}
