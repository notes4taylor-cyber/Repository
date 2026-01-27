// Copyright Card Show Vendor. All Rights Reserved.

#include "Core/CSVPlayerController.h"
#include "Core/CSVPlayerState.h"
#include "Core/CSVGameMode.h"
#include "UI/CSVMainHUD.h"
#include "Cards/CSVCardInstance.h"
#include "Cards/CSVCardDatabase.h"
#include "Booth/CSVVendorBooth.h"
#include "CardShowVendor.h"

ACSVPlayerController::ACSVPlayerController()
{
	MainHUDWidget = nullptr;
	CurrentBooth = nullptr;
}

void ACSVPlayerController::BeginPlay()
{
	Super::BeginPlay();

	// Set input mode for game and UI
	FInputModeGameAndUI InputMode;
	InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	SetInputMode(InputMode);
	bShowMouseCursor = true;

	// Create main HUD
	ShowMainHUD();
}

void ACSVPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	// Bind input actions - in a full implementation, use Enhanced Input
}

void ACSVPlayerController::ShowMainHUD()
{
	if (!MainHUDWidget && MainHUDClass)
	{
		MainHUDWidget = CreateWidget<UCSVMainHUD>(this, MainHUDClass);
	}

	if (MainHUDWidget && !MainHUDWidget->IsInViewport())
	{
		MainHUDWidget->AddToViewport();
	}
}

void ACSVPlayerController::HideMainHUD()
{
	if (MainHUDWidget && MainHUDWidget->IsInViewport())
	{
		MainHUDWidget->RemoveFromViewport();
	}
}

void ACSVPlayerController::OpenInventory()
{
	// Implementation would show inventory widget
	UE_LOG(LogCardShowVendor, Log, TEXT("Opening inventory"));
}

void ACSVPlayerController::CloseInventory()
{
	UE_LOG(LogCardShowVendor, Log, TEXT("Closing inventory"));
}

void ACSVPlayerController::OpenBoothManagement()
{
	UE_LOG(LogCardShowVendor, Log, TEXT("Opening booth management"));
}

void ACSVPlayerController::OpenMarketView()
{
	UE_LOG(LogCardShowVendor, Log, TEXT("Opening market view"));
}

void ACSVPlayerController::OpenPackOpening()
{
	UE_LOG(LogCardShowVendor, Log, TEXT("Opening pack opening interface"));
}

void ACSVPlayerController::InteractWithBooth(ACSVVendorBooth* Booth)
{
	CurrentBooth = Booth;
	if (Booth)
	{
		OpenBoothManagement();
	}
}

void ACSVPlayerController::SetCardPrice(UCSVCardInstance* Card, float NewPrice)
{
	if (Card)
	{
		Card->SetListedPrice(NewPrice);
		UE_LOG(LogCardShowVendor, Log, TEXT("Set card price to $%.2f"), NewPrice);
	}
}

void ACSVPlayerController::AddCardToDisplay(UCSVCardInstance* Card, int32 SlotIndex)
{
	if (CurrentBooth && Card)
	{
		CurrentBooth->AddCardToDisplay(Card, SlotIndex);
	}
}

void ACSVPlayerController::RemoveCardFromDisplay(int32 SlotIndex)
{
	if (CurrentBooth)
	{
		CurrentBooth->RemoveCardFromDisplay(SlotIndex);
	}
}

bool ACSVPlayerController::BuyPack(FName PackName)
{
	ACSVPlayerState* PS = GetPlayerState<ACSVPlayerState>();
	ACSVGameMode* GM = GetWorld()->GetAuthGameMode<ACSVGameMode>();

	if (!PS || !GM || !GM->GetCardDatabase())
	{
		return false;
	}

	FCSVPackConfiguration PackConfig = GM->GetCardDatabase()->GetPackByName(PackName);
	if (PackConfig.PackName.IsNone())
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Pack not found: %s"), *PackName.ToString());
		return false;
	}

	if (!PS->SpendMoney(PackConfig.PackPrice))
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Cannot afford pack"));
		return false;
	}

	// Open the pack
	TArray<UCSVCardInstance*> PackContents = GM->GetCardDatabase()->OpenPack(PackConfig, PS);

	// Add cards to inventory
	int32 Rares = 0;
	int32 Legendaries = 0;
	for (UCSVCardInstance* Card : PackContents)
	{
		if (Card)
		{
			PS->AddCardToInventory(Card);
			if (Card->GetRarity() >= 2) Rares++; // Rare+
			if (Card->GetRarity() >= 4) Legendaries++; // Legendary
		}
	}

	// Record for progression
	if (GM->GetProgressionManager())
	{
		GM->GetProgressionManager()->RecordPackOpened(Rares, Legendaries);
	}

	UE_LOG(LogCardShowVendor, Log, TEXT("Opened pack %s, got %d cards"), 
		*PackName.ToString(), PackContents.Num());

	return true;
}

bool ACSVPlayerController::SellCard(UCSVCardInstance* Card, float Price)
{
	ACSVPlayerState* PS = GetPlayerState<ACSVPlayerState>();
	ACSVGameMode* GM = GetWorld()->GetAuthGameMode<ACSVGameMode>();

	if (!PS || !Card)
	{
		return false;
	}

	if (!PS->RemoveCardFromInventory(Card))
	{
		return false;
	}

	PS->AddMoney(Price);

	// Record for progression
	if (GM && GM->GetProgressionManager())
	{
		GM->GetProgressionManager()->RecordSale(Price, Card->GetRarity());
	}

	UE_LOG(LogCardShowVendor, Log, TEXT("Sold card for $%.2f"), Price);
	return true;
}

bool ACSVPlayerController::BuyCard(UCSVCardInstance* Card, float Price)
{
	ACSVPlayerState* PS = GetPlayerState<ACSVPlayerState>();
	ACSVGameMode* GM = GetWorld()->GetAuthGameMode<ACSVGameMode>();

	if (!PS || !Card)
	{
		return false;
	}

	if (!PS->SpendMoney(Price))
	{
		return false;
	}

	PS->AddCardToInventory(Card);

	// Record for progression
	if (GM && GM->GetProgressionManager())
	{
		GM->GetProgressionManager()->RecordPurchase(Price);
	}

	UE_LOG(LogCardShowVendor, Log, TEXT("Bought card for $%.2f"), Price);
	return true;
}

void ACSVPlayerController::OnPausePressed()
{
	ACSVGameMode* GM = GetWorld()->GetAuthGameMode<ACSVGameMode>();
	if (GM)
	{
		GM->PauseGame();
	}
}

void ACSVPlayerController::OnInventoryPressed()
{
	OpenInventory();
}

void ACSVPlayerController::OnInteractPressed()
{
	// Interaction logic
}
